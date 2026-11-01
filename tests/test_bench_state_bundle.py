from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOL = Path(__file__).parents[1] / "tools" / "uk_fw" / "bench_state_bundle.py"
SPEC = importlib.util.spec_from_file_location("bench_state_bundle", TOOL)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def framed_record(key: str, value: str) -> str:
    return f"@@R|{key}|{value.encode('utf-8').hex()}"


def valid_capture(extra: dict[str, list[tuple[str, str]]] | None = None) -> bytes:
    records = {name: [] for name in MODULE.EXPECTED_SECTIONS}
    records["meta"] = [("schema", MODULE.SCHEMA)]
    records["complete"] = [("result", "complete")]
    for section, values in (extra or {}).items():
        records[section].extend(values)
    lines: list[str] = []
    for section in MODULE.EXPECTED_SECTIONS:
        lines.append(f"@@IONIQ_BENCH_STATE_V1|BEGIN|{section}@@")
        lines.extend(framed_record(key, value) for key, value in records[section])
        lines.append(f"@@IONIQ_BENCH_STATE_V1|END|{section}|0@@")
    return ("\n".join(lines) + "\n").encode()


class BenchStateBundleTests(unittest.TestCase):
    def test_emitted_probe_passes_safety_and_shell_syntax(self) -> None:
        self.assertEqual(MODULE.audit_script(MODULE.PROBE_SCRIPT), [])
        ok, error = MODULE.shell_syntax_check(MODULE.PROBE_SCRIPT)
        self.assertTrue(ok, error)

    def test_emitted_probe_covers_required_passive_sections(self) -> None:
        script = MODULE.PROBE_SCRIPT
        for section in (
            "identity",
            "processes",
            "smack",
            "units",
            "interfaces",
            "cellular",
            "bluetooth",
            "dropbear",
            "storage",
            "hashes",
            "complete",
        ):
            self.assertIn(f"begin_section {section}", script)
        self.assertIn("systemctl show", script)
        self.assertIn("Dbuslaunch.service", script)
        self.assertIn("file_meta /tmp/session_appmgr\n", script)
        self.assertIn("file_meta /tmp/session_appmgr.env", script)
        self.assertIn("sdptool browse local", script)
        self.assertNotIn("hciconfig -a", script)
        self.assertNotIn("wpa_cli", script)
        self.assertEqual(script.count("command -v"), 1)  # only inside has_command()
        self.assertNotIn("if command -v", script)
        self.assertNotRegex(script, r"\biw\s+.*\bscan\b")
        for process_name in ("AppLauncher", "AppDMClient", "AppScomoDM", "AppUpgrade"):
            self.assertIn(process_name, script)
        self.assertIn('record process-credentials "$P_PID|$P_UID|$P_EUID|$P_SUID|$P_FSUID|$P_GID|$P_EGID|$P_SGID|$P_FSGID|$P_GROUPS"', script)
        self.assertIn('record process-security "$P_PID|$P_PPID|$P_CAP_INH|$P_CAP_PRM|$P_CAP_EFF|$P_CAP_BND|$P_CAP_AMB|$P_NO_NEW_PRIVS|$P_SECCOMP"', script)
        for status_name in (
            '"PPid:"',
            '"CapInh:"',
            '"CapPrm:"',
            '"CapEff:"',
            '"CapBnd:"',
            '"CapAmb:"',
            '"NoNewPrivs:"',
            '"Seccomp:"',
        ):
            self.assertIn(status_name, script)
        for sysctl_name in (
            "kernel/kexec_load_disabled",
            "kernel/modules_disabled",
            "kernel/dmesg_restrict",
            "vm/mmap_min_addr",
        ):
            self.assertIn(sysctl_name, script)
        for update_path in (
            "/bin/busybox",
            "/usr/bin/unzip",
            "/usr/bin/unzip64",
            "/bin/sh",
            "/bin/bash",
            "/lib/ld-linux-x86-64.so.2",
            "/lib/ld-2.25.so",
            "/bin/date",
            "/usr/bin/date",
            "/lib/systemd/systemd",
            "/lib/systemd/esinit",
            "/app/bin/AppLauncher",
            "/app/bin/AppLauncher.sh",
            "/app/bin/AppDMClient",
            "/app/bin/AppScomoDM",
            "/app/bin/AppUpgrade",
            "/app/bin/NaviUpdateApp",
            "/app/bin/CarOption.csv",
            "/app/share/AppUpgrade/DecryptToPIPE",
            "/app/share/AppUpgrade/teruten5_pub.key",
            "/etc/update_start_5w.sh.ori",
            "/etc/smack-relabel-ro.sh",
            "/etc/smack_setup.sh",
            "/etc/smack_setup_recovery.sh",
            "/update",
            "/update/usb",
            "/update/sysroot",
            "/update/usb/upgrade",
            "/update/usb/bin",
            "/update/usb/bin/AppUpgrade",
            "/update/usb/bin/.lge.upgrade.xml",
            "/tmp/AppUpgrade",
        ):
            self.assertIn(update_path, script)
        for update_flag in (
            "disableNaviMapSignatureCheck_20230207",
            "force_launch",
            "system_update_complete",
            "system_update_completed",
            "firmware_update_complete",
            "scheduled_update_complete",
            "scheduled_update_complete_for_DM",
        ):
            self.assertRegex(script, rf"for S_FLAG in [^\n]*\b{update_flag}\b")
        self.assertIn('capture_file update-flag "/update/$S_FLAG"', script)
        self.assertNotIn('[ -r "/update/$S_FLAG" ]', script)
        self.assertIn('P_UID_STATUS=$?', script)
        self.assertIn('P_GID_STATUS=$?', script)
        self.assertIn('P_GROUPS_STATUS=$?', script)
        self.assertIn('U_STATUS=$?', script)
        for pty_path in ("/dev/ptmx", "/dev/pts", "/dev/pts/ptmx"):
            self.assertIn(pty_path, script)
        self.assertIn("capture_file modules /proc/modules", script)
        self.assertIn("read_scalar perf-event-paranoid /proc/sys/kernel/perf_event_paranoid", script)
        self.assertIn("/lib/modules/4.1.27-abl/kernel/net/unix/unix.ko", script)
        self.assertIn('read_scalar interface-operstate', script)
        self.assertIn('record unreadable-file', script)

        smack_paths = (
            "/update",
            "/update/usb",
            "/update/usb/bin",
            "/update/usb/bin/AppUpgrade",
            "/update/usb/bin/.lge.upgrade.xml",
            "/app/bin/AppLauncher",
            "/app/bin/AppLauncher.sh",
            "/app/bin/AppDMClient",
            "/app/bin/AppUpgrade",
            "/app/share/AppUpgrade/teruten5_pub.key",
            "/etc/update_start_5w.sh.ori",
            "/etc/smack-relabel-ro.sh",
            "/etc/smack_setup.sh",
            "/etc/smack_setup_recovery.sh",
            "/bin/sh",
            "/bin/bash",
            "/lib/ld-linux-x86-64.so.2",
            "/lib/ld-2.25.so",
            "/bin/date",
            "/usr/bin/date",
            "/lib/systemd/systemd",
            "/tmp",
        )
        smack_path_loop = next(
            line for line in script.splitlines() if line.startswith("for SX_PATH in ")
        )
        for path in smack_paths:
            self.assertIn(f" {path}", smack_path_loop)
        self.assertEqual(
            script.count(
                'getfattr -h --absolute-names --dump --match="^security\\\\.$SX_NAME$" "$SX_PATH"'
            ),
            1,
        )
        self.assertEqual(
            script.count(
                'getfattr -h --only-values -n "security.$SX_NAME" "$SX_PATH"'
            ),
            1,
        )
        self.assertIn("for SX_NAME in SMACK64 SMACK64EXEC", script)
        self.assertIn('capture_smack_xattr "$SX_NAME" "$SX_PATH"', script)
        smack_helper = script.split("capture_smack_xattr() {", 1)[1].split(
            "\nhash_file() {", 1
        )[0]
        self.assertNotRegex(smack_helper, r"\b(?:cat|head|tail|hash_file)\b")
        self.assertNotRegex(script, r"\b(?:setfattr|chsmack|chattr)\b")
        self.assertNotRegex(script, r"\battr\b[^\n]*(?:\s-s\b|\s-r\b|--set\b|--remove\b)")
        self.assertNotIn("[ ! -r \"$SX_PATH\" ]", smack_helper)

    def test_process_security_awk_accepts_linux_v41_optional_field_absence(self) -> None:
        awk_program = MODULE.PROBE_SCRIPT.split("P_SECURITY_FIELDS=$(awk '\n", 1)[1].split(
            "\n    ' \"$P_DIR/status\"", 1
        )[0]
        status = """Name:\ttest
PPid:\t1
CapInh:\t0000000000000000
CapPrm:\t0000003fffffffff
CapEff:\t0000003fffffffff
CapBnd:\t0000003fffffffff
Seccomp:\t0
"""
        with tempfile.TemporaryDirectory() as tmp:
            status_path = Path(tmp) / "status"
            status_path.write_text(status, encoding="ascii")
            proc = subprocess.run(
                ["awk", awk_program, str(status_path)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(
            proc.stdout.strip(),
            "1|0000000000000000|0000003fffffffff|0000003fffffffff|0000003fffffffff|unavailable|unavailable|0",
        )

    def test_smack_xattr_helper_records_success_absence_and_fail_closed_errors(self) -> None:
        preamble = MODULE.PROBE_SCRIPT.split("if ! has_command od", 1)[0]
        exercise = r'''
begin_section smack
capture_smack_xattr SMACK64 "$1"
capture_smack_xattr SMACK64EXEC "$1"
capture_smack_xattr SMACK64 "$2"
capture_smack_xattr SMACK64 "$3"
capture_smack_xattr SMACK64 "$4"
capture_smack_xattr SMACK64 "$5"
capture_smack_xattr SMACK64 "$6"
record collect-failure "$COLLECT_FAILURE"
end_section smack "$COLLECT_FAILURE"
begin_section complete
if [ "$COLLECT_FAILURE" -eq 0 ]; then
    record result complete
    end_section complete 0
else
    record result collection-error
    end_section complete 1
fi
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_getfattr = fake_bin / "getfattr"
            fake_getfattr.write_text(
                "#!/bin/sh\n"
                "for arg in \"$@\"; do path=$arg; done\n"
                "case \"$path\" in *query-error) exit 7;; esac\n"
                "case \" $* \" in\n"
                "  *' --dump '*)\n"
                "    case \"$path\" in\n"
                "      *attribute-absent) exit 0;;\n"
                "      *) case \" $* \" in\n"
                "           *SMACK64EXEC*) printf 'security.SMACK64EXEC=\\\"\\\"\\n';;\n"
                "           *) printf 'security.SMACK64=\\\"\\\"\\n';;\n"
                "         esac;;\n"
                "    esac;;\n"
                "  *' --only-values '*)\n"
                "    case \"$path\" in\n"
                "      *empty) exit 0;;\n"
                "      *malformed) printf 'bad/label\\n';;\n"
                "      *) case \" $* \" in\n"
                "           *SMACK64EXEC*) printf 'App::Upgrade\\n';;\n"
                "           *) printf 'Update::Source\\n';;\n"
                "         esac;;\n"
                "    esac;;\n"
                "  *) exit 99;;\n"
                "esac\n",
                encoding="ascii",
            )
            fake_getfattr.chmod(0o700)
            success = root / "success"
            query_error = root / "query-error"
            empty = root / "empty"
            malformed = root / "malformed"
            attribute_absent = root / "attribute-absent"
            for path in (success, query_error, empty, malformed, attribute_absent):
                path.write_text("contents-must-not-be-read", encoding="ascii")
            path_absent = root / "path-absent"
            env = dict(os.environ)
            env["PATH"] = f"{fake_bin}:/usr/bin:/bin"
            proc = subprocess.run(
                [
                    "/bin/sh",
                    "-s",
                    "--",
                    str(success),
                    str(query_error),
                    str(empty),
                    str(malformed),
                    str(attribute_absent),
                    str(path_absent),
                ],
                input=preamble + exercise,
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = MODULE.parse_capture(proc.stdout.encode())
        records = [
            (item["key"], item["value"])
            for section in report["sections"]
            for item in section["records"]
        ]
        self.assertIn(
            ("smack-xattr", f"{success}|SMACK64|present|getfattr|Update::Source"),
            records,
        )
        self.assertIn(
            ("smack-xattr", f"{success}|SMACK64EXEC|present|getfattr|App::Upgrade"),
            records,
        )
        self.assertIn(
            ("smack-xattr", f"{query_error}|SMACK64|query-error|getfattr|status=7"),
            records,
        )
        self.assertIn(
            ("smack-xattr", f"{empty}|SMACK64|malformed|getfattr|reason=empty"),
            records,
        )
        self.assertIn(
            ("smack-xattr", f"{malformed}|SMACK64|malformed|getfattr|reason=invalid-label"),
            records,
        )
        self.assertIn(
            ("smack-xattr", f"{attribute_absent}|SMACK64|attribute-absent|getfattr|"),
            records,
        )
        self.assertIn(
            ("smack-xattr", f"{path_absent}|SMACK64|path-absent||"),
            records,
        )
        self.assertIn(("collect-failure", "1"), records)
        complete = next(
            section for section in report["sections"] if section["name"] == "complete"
        )
        self.assertEqual(complete["end_status"], 1)

    def test_smack_xattr_provider_unavailable_is_explicit(self) -> None:
        preamble = MODULE.PROBE_SCRIPT.split("if ! has_command od", 1)[0]
        exercise = r'''
has_command() {
    [ "$1" = getfattr ] && return 1
    command -v "$1" >/dev/null 2>&1
}
begin_section smack
capture_smack_xattr SMACK64 "$1"
capture_smack_xattr SMACK64EXEC "$1"
record collect-failure "$COLLECT_FAILURE"
end_section smack "$COLLECT_FAILURE"
'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "existing"
            path.write_text("contents-must-not-be-read", encoding="ascii")
            proc = subprocess.run(
                ["/bin/sh", "-s", "--", str(path)],
                input=preamble + exercise,
                text=True,
                capture_output=True,
                env={**os.environ, "PATH": "/usr/bin:/bin"},
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = MODULE.parse_capture(proc.stdout.encode())
        records = [
            (item["key"], item["value"])
            for section in report["sections"]
            for item in section["records"]
        ]
        self.assertIn(
            ("smack-xattr", f"{path}|SMACK64|provider-unavailable|getfattr|"),
            records,
        )
        self.assertIn(
            ("smack-xattr", f"{path}|SMACK64EXEC|provider-unavailable|getfattr|"),
            records,
        )
        self.assertIn(("collect-failure", "0"), records)

    def test_smack_xattr_records_survive_parsing_and_derive_facts(self) -> None:
        values = [
            ("smack-xattr", "/update|SMACK64|present|getfattr|Update::Source"),
            (
                "smack-xattr",
                "/update|SMACK64EXEC|provider-unavailable|getfattr|",
            ),
            (
                "smack-xattr",
                "/update/usb|SMACK64|attribute-absent|getfattr|",
            ),
            (
                "smack-xattr",
                "/app/bin/AppUpgrade|SMACK64|query-error|getfattr|status=13",
            ),
        ]
        report = MODULE.parse_capture(valid_capture({"smack": values}))
        self.assertTrue(report["complete"])
        smack = next(section for section in report["sections"] if section["name"] == "smack")
        self.assertEqual(
            smack["records"],
            [{"key": key, "value": value} for key, value in values],
        )
        self.assertEqual(
            report["facts"]["smack_xattrs"]["/update"]["SMACK64"],
            {"state": "present", "provider": "getfattr", "value": "Update::Source"},
        )
        self.assertEqual(
            report["facts"]["smack_xattrs"]["/app/bin/AppUpgrade"]["SMACK64"],
            {"state": "query-error", "provider": "getfattr", "value": "status=13"},
        )

    def test_perf_event_paranoid_success_is_emitted_before_state_reuse(self) -> None:
        preamble = MODULE.PROBE_SCRIPT.split("if ! has_command od", 1)[0]
        exercise = r'''
begin_section identity
read_scalar perf-event-paranoid "$1"
if [ "$RS_STATE" = present ]; then
    I_PERF_VALUE=$RS_VALUE
    case "$I_PERF_VALUE" in
        -*) I_PERF_DIGITS=${I_PERF_VALUE#-} ;;
        *) I_PERF_DIGITS=$I_PERF_VALUE ;;
    esac
    case "$I_PERF_DIGITS" in
        ''|*[!0-9]*)
            record malformed-scalar "perf-event-paranoid|$I_PERF_VALUE"
            COLLECT_FAILURE=1
            ;;
        *) record perf-event-paranoid "$I_PERF_VALUE" ;;
    esac
fi
read_scalar reused-state "$2"
end_section identity "$COLLECT_FAILURE"
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            perf_value = root / "perf-event-paranoid"
            perf_value.write_text("1\n", encoding="ascii")
            reused = root / "reused"
            reused.write_text("overwritten\n", encoding="ascii")
            run = subprocess.run(
                ["/bin/sh", "-s", "--", str(perf_value), str(reused)],
                input=preamble + exercise,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        self.assertIn("@@R|perf-event-paranoid|31\n", run.stdout)
        emitted_records = [
            line for line in run.stdout.splitlines() if line.startswith("@@R|")
        ]
        self.assertEqual(emitted_records, ["@@R|perf-event-paranoid|31"])
        placeholder = framed_record("perf-event-paranoid", "placeholder").encode()
        capture = valid_capture({"identity": [("perf-event-paranoid", "placeholder")]})
        capture = capture.replace(placeholder, emitted_records[0].encode(), 1)
        report = MODULE.parse_capture(capture)
        identity = next(section for section in report["sections"] if section["name"] == "identity")
        self.assertIn({"key": "perf-event-paranoid", "value": "1"}, identity["records"])

    def test_probe_helpers_fail_closed_on_collection_errors(self) -> None:
        preamble = MODULE.PROBE_SCRIPT.split("if ! has_command od", 1)[0]
        exercise = r'''
begin_section storage
read_scalar scalar "$1"
capture_file read-error "$2"
file_meta "$3"
file_meta "$4"
hash_file "$5"
hash_file "$6"
hash_file "$7"
hash_file "$8"
capture_file update-flag "$9"
capture_unit test.service
capture_interface "${10}"
capture_command command-test probe-fail
record collect-failure "$COLLECT_FAILURE"
end_section storage "$COLLECT_FAILURE"
begin_section complete
if [ "$COLLECT_FAILURE" -eq 0 ]; then
    record result complete
    end_section complete 0
else
    record result collection-error
    end_section complete 1
fi
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_awk = fake_bin / "awk"
            fake_awk.write_text("#!/bin/sh\nexit 9\n")
            fake_awk.chmod(0o700)
            fake_cat = fake_bin / "cat"
            fake_cat.write_text(
                "#!/bin/sh\ncase \"$1\" in *scalar-read-error|*/operstate) exit 6;; esac\n"
                "exec /bin/cat \"$@\"\n"
            )
            fake_cat.chmod(0o700)
            fake_stat = fake_bin / "stat"
            fake_stat.write_text(
                "#!/bin/sh\nfor LAST do :; done\n"
                "case \"$LAST\" in *meta-fail) exit 7;; esac\n"
                "printf '644|0|0|1|regular file\\n'\n"
            )
            fake_stat.chmod(0o700)
            fake_readlink = fake_bin / "readlink"
            fake_readlink.write_text("#!/bin/sh\nexit 5\n")
            fake_readlink.chmod(0o700)
            fake_sha = fake_bin / "sha256sum"
            fake_sha.write_text(
                "#!/bin/sh\ncase \"$1\" in\n"
                "  *hash-empty) exit 0;;\n"
                "  *hash-fail) exit 8;;\n"
                "  *hash-garbage) printf '%064d  %s garbage\\n' 0 \"$1\";;\n"
                "  *) printf 'not-a-digest  %s\\n' \"$1\";;\n"
                "esac\n"
            )
            fake_sha.chmod(0o700)
            fake_systemctl = fake_bin / "systemctl"
            fake_systemctl.write_text("#!/bin/sh\nexit 12\n")
            fake_systemctl.chmod(0o700)
            fake_command = fake_bin / "probe-fail"
            fake_command.write_text("#!/bin/sh\nexit 11\n")
            fake_command.chmod(0o700)

            scalar_error = root / "scalar-read-error"
            scalar_error.write_text("scalar")
            read_error = root / "directory"
            read_error.mkdir()
            meta_fail = root / "meta-fail"
            meta_fail.write_text("meta")
            link_fail = root / "link-fail"
            link_fail.symlink_to(meta_fail)
            hash_bad = root / "hash-bad"
            hash_bad.write_text("bad")
            hash_empty = root / "hash-empty"
            hash_empty.write_text("empty")
            hash_fail = root / "hash-fail"
            hash_fail.write_text("fail")
            hash_garbage = root / "hash-garbage"
            hash_garbage.write_text("garbage")
            update_marker = root / "force_launch"
            update_marker.write_text("run")
            update_marker.chmod(0)
            interface = root / "interface"
            interface.mkdir()
            for name, value in (
                ("operstate", "up"),
                ("carrier", "1"),
                ("type", "1"),
                ("ifindex", "3"),
                ("iflink", "3"),
            ):
                (interface / name).write_text(value)

            env = dict(os.environ)
            env["PATH"] = f"{fake_bin}:/usr/bin:/bin"
            proc = subprocess.run(
                [
                    "/bin/sh",
                    "-s",
                    "--",
                    str(scalar_error),
                    str(read_error),
                    str(meta_fail),
                    str(link_fail),
                    str(hash_bad),
                    str(hash_empty),
                    str(hash_fail),
                    str(hash_garbage),
                    str(update_marker),
                    str(interface),
                ],
                input=preamble + exercise,
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            report = MODULE.parse_capture(proc.stdout.encode())
            records = [
                (item["key"], item["value"])
                for section in report["sections"]
                for item in section["records"]
            ]
            keys = {key for key, _ in records}
            self.assertIn("file-read-error", keys)
            self.assertIn("file-meta-error", keys)
            self.assertIn("file-link-error", keys)
            self.assertIn("hash-error", keys)
            self.assertIn("command-error", keys)
            self.assertIn("unit-error", keys)
            self.assertIn("interface-read-error", keys)
            self.assertTrue("unreadable-file" in keys or "file-read-error" in keys)
            hash_errors = [value for key, value in records if key == "hash-error"]
            self.assertEqual(len(hash_errors), 4)
            self.assertTrue(any("hash-empty" in value for value in hash_errors))
            self.assertTrue(any("hash-fail" in value for value in hash_errors))
            self.assertTrue(any("hash-garbage" in value for value in hash_errors))
            values = dict(records)
            self.assertEqual(values["collect-failure"], "1")
            self.assertEqual(values["result"], "collection-error")
            complete = next(
                section for section in report["sections"] if section["name"] == "complete"
            )
            self.assertEqual(complete["end_status"], 1)
            self.assertFalse(report["complete"])

    def test_process_environ_partial_output_failure_is_not_complete(self) -> None:
        preamble = MODULE.PROBE_SCRIPT.split("if ! has_command od", 1)[0]
        exercise = r'''
begin_section processes
capture_process_path 42 "$1"
record collect-failure "$COLLECT_FAILURE"
end_section processes "$COLLECT_FAILURE"
begin_section complete
if [ "$COLLECT_FAILURE" -eq 0 ]; then
    record result complete
    end_section complete 0
else
    record result collection-error
    end_section complete 1
fi
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            proc_dir = root / "42"
            proc_dir.mkdir()
            (proc_dir / "environ").write_bytes(b"PATH=/real/bin\0OTHER=value\0")
            fake_bin = root / "bin"
            fake_bin.mkdir()
            fake_tr = fake_bin / "tr"
            fake_tr.write_text(
                "#!/bin/sh\n"
                "if [ \"$1\" = '\\000' ] && [ \"$2\" = '\\n' ]; then\n"
                "  printf 'PATH=/partial/bin\\n'\n"
                "  exit 7\n"
                "fi\n"
                "exec /usr/bin/tr \"$@\"\n"
            )
            fake_tr.chmod(0o700)
            env = dict(os.environ)
            env["PATH"] = f"{fake_bin}:/usr/bin:/bin"
            proc = subprocess.run(
                ["/bin/sh", "-s", "--", str(proc_dir)],
                input=preamble + exercise,
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            report = MODULE.parse_capture(proc.stdout.encode())
            records = [
                (item["key"], item["value"])
                for section in report["sections"]
                for item in section["records"]
            ]
            self.assertIn(("process-path", "42|/partial/bin"), records)
            errors = [value for key, value in records if key == "process-read-error"]
            self.assertTrue(any("producer=7" in value for value in errors))
            complete = next(
                section for section in report["sections"] if section["name"] == "complete"
            )
            self.assertEqual(complete["end_status"], 1)
            self.assertFalse(report["complete"])

    def test_missing_hash_and_readlink_providers_are_explicit_nonfailures(self) -> None:
        preamble = MODULE.PROBE_SCRIPT.split("if ! has_command od", 1)[0]
        exercise = r'''
has_command() {
    case "$1" in sha256sum|openssl|readlink|stat|ls) return 1 ;; esac
    command -v "$1" >/dev/null 2>&1
}
begin_section hashes
hash_file "$1"
file_meta "$2"
read_link_value test-link "$2"
record collect-failure "$COLLECT_FAILURE"
end_section hashes "$COLLECT_FAILURE"
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target"
            target.write_text("target")
            link = root / "link"
            link.symlink_to(target)
            env = dict(os.environ)
            env["PATH"] = "/usr/bin:/bin"
            proc = subprocess.run(
                ["/bin/sh", "-s", "--", str(target), str(link)],
                input=preamble + exercise,
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            report = MODULE.parse_capture(proc.stdout.encode())
            records = [
                (item["key"], item["value"])
                for section in report["sections"]
                for item in section["records"]
            ]
            self.assertIn(("hash", f"{target}|unavailable"), records)
            self.assertTrue(any(key == "file-meta-unavailable" for key, _ in records))
            self.assertTrue(any(key == "file-link-unavailable" for key, _ in records))
            self.assertIn(("collect-failure", "0"), records)

    def test_record_encoder_faults_are_fatal(self) -> None:
        preamble = MODULE.PROBE_SCRIPT.split("if ! has_command od", 1)[0]
        exercise = r'''
begin_section complete
record result complete
end_section complete "$COLLECT_FAILURE"
'''
        for failed_tool in ("od", "tr"):
            with self.subTest(failed_tool=failed_tool), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                fake_bin = root / "bin"
                fake_bin.mkdir()
                fake_tool = fake_bin / failed_tool
                if failed_tool == "od":
                    fake_tool.write_text("#!/bin/sh\nprintf ' 72 65 63 6f 72 64'\nexit 7\n")
                else:
                    fake_tool.write_text("#!/bin/sh\n/bin/cat\nexit 8\n")
                fake_tool.chmod(0o700)
                env = dict(os.environ)
                env["PATH"] = f"{fake_bin}:/usr/bin:/bin"
                proc = subprocess.run(
                    ["/bin/sh", "-s"],
                    input=preamble + exercise,
                    text=True,
                    capture_output=True,
                    env=env,
                    check=False,
                )
                self.assertEqual(proc.returncode, 0, proc.stderr)
                report = MODULE.parse_capture(proc.stdout.encode())
                fatal = [
                    item["value"]
                    for section in report["sections"]
                    for item in section["records"]
                    if item["key"] == "fatal"
                ]
                self.assertEqual(fatal, ["record-encode-error"])
                self.assertIn("probe reported fatal collection error", report["warnings"])
                complete = report["sections"][0]
                self.assertEqual(complete["end_status"], 1)
                self.assertFalse(report["complete"])

    def test_audit_rejects_target_writes_and_active_commands(self) -> None:
        unsafe = """#!/bin/sh
systemctl start ofono.service
mount -o remount,rw /
printf x > /tmp/result
wpa_cli p2p_find
"""
        violations = MODULE.audit_script(unsafe)
        self.assertGreaterEqual(len(violations), 4)
        self.assertTrue(any("redirection" in item for item in violations))

        for path_qualified_write in (
            "/bin/rm /tmp/x\n",
            "/usr/bin/touch /tmp/x\n",
            "/sbin/mount /dev/x /mnt\n",
            "./mkdir /tmp/x\n",
            "/usr/bin/curl https://example.invalid/\n",
            "/usr/bin/systemctl restart dbus.service\n",
        ):
            with self.subTest(path_qualified_write=path_qualified_write):
                self.assertTrue(MODULE.audit_script(path_qualified_write))

        for xattr_write in (
            "setfattr -n security.SMACK64 -v label /update\n",
            "/usr/bin/setfattr -n security.SMACK64 -v label /update\n",
            "chsmack -a label /update\n",
            "/sbin/chsmack -a label /update\n",
            "/usr/bin/chattr +i /update\n",
            "/bin/chmod 777 /update\n",
            "/bin/chown 1:1 /update\n",
            "attr -Sq -s SMACK64 -V label /update\n",
            "/usr/bin/attr --remove SMACK64 /update\n",
        ):
            with self.subTest(xattr_write=xattr_write):
                self.assertTrue(MODULE.audit_script(xattr_write))

    def test_audit_rejects_non_allowlisted_environment_read(self) -> None:
        unsafe_lines = (
            '''P_PATH=$(cat < "$P_DIR/environ" 2>/dev/null)\n''',
            '''P_PATH=$(cat "$P_DIR/environ" 2>/dev/null)\n''',
            '''capture_file process-env "$P_DIR/environ"\n''',
        )
        for unsafe in unsafe_lines:
            with self.subTest(unsafe=unsafe):
                violations = MODULE.audit_script(unsafe)
                self.assertTrue(
                    any("non-allowlisted environment read" in item for item in violations)
                )
        self.assertEqual(MODULE.audit_script(MODULE.SAFE_ENVIRON_READ_LINE + "\n"), [])

    def test_parse_timestamped_capture_and_derive_facts(self) -> None:
        capture = valid_capture(
            {
                "processes": [
                    (
                        "process",
                        "12|100|200|App::bluetooth|/tmp/vbtd|vbtd|/app/bin/vbtd -d /dev/ttyS0",
                    ),
                    (
                        "process-credentials",
                        "12|100|101|102|103|200|201|202|203|4 5 44",
                    ),
                    (
                        "process-security",
                        "12|1|0000000000000000|0000000000200000|0000000000200000|0000003fffffffff|unavailable|unavailable|0",
                    ),
                    ("process-path", "12|/usr/local/bin:/usr/bin:/bin"),
                ],
                "identity": [
                    ("security-sysctl", "kernel/kexec_load_disabled|0"),
                    ("security-sysctl", "kernel/modules_disabled|1"),
                ],
                "units": [("unit", "vbtd.service|LoadState=loaded;ActiveState=active;")],
                "interfaces": [
                    ("interface", "wlan0|up|1|1|3|3|/sys/bus/pci/drivers/test"),
                    ("listener", "tcp LISTEN 0 5 0.0.0.0:22"),
                ],
                "hashes": [("hash", "/tmp/vbtd|" + "a" * 64)],
            }
        )
        timestamped = b"noise before probe\n" + b"".join(
            f"[12:00:00.001] {line.decode()}".encode()
            for line in capture.splitlines(keepends=True)
        )
        report = MODULE.parse_capture(timestamped)
        self.assertTrue(report["complete"])
        self.assertEqual(report["warnings"], [])
        self.assertEqual(report["facts"]["processes"][0]["smack_label"], "App::bluetooth")
        self.assertEqual(
            report["facts"]["process_credentials"]["12"],
            {
                "ruid": 100,
                "euid": 101,
                "suid": 102,
                "fsuid": 103,
                "rgid": 200,
                "egid": 201,
                "sgid": 202,
                "fsgid": 203,
                "supplementary_groups": [4, 5, 44],
            },
        )
        self.assertEqual(
            report["facts"]["process_security"]["12"],
            {
                "ppid": 1,
                "cap_inheritable": {"hex": "0000000000000000", "value": 0, "names": []},
                "cap_permitted": {"hex": "0000000000200000", "value": 1 << 21, "names": ["CAP_SYS_ADMIN"]},
                "cap_effective": {"hex": "0000000000200000", "value": 1 << 21, "names": ["CAP_SYS_ADMIN"]},
                "cap_bounding": {
                    "hex": "0000003fffffffff",
                    "value": 0x3FFFFFFFFF,
                    "names": list(MODULE.CAPABILITY_NAMES),
                },
                "cap_ambient": None,
                "no_new_privs": None,
                "seccomp": 0,
            },
        )
        self.assertEqual(
            report["facts"]["process_paths"]["12"],
            "/usr/local/bin:/usr/bin:/bin",
        )
        self.assertEqual(
            report["facts"]["security_sysctls"],
            {"kernel/kexec_load_disabled": 0, "kernel/modules_disabled": 1},
        )
        self.assertEqual(report["facts"]["units"]["vbtd.service"], "LoadState=loaded;ActiveState=active;")
        self.assertEqual(report["facts"]["interfaces"][0]["name"], "wlan0")
        self.assertEqual(report["facts"]["interfaces"][0]["ifindex"], 3)
        self.assertEqual(report["facts"]["hashes"]["/tmp/vbtd"], "a" * 64)
        self.assertEqual(report["facts"]["listeners"], ["tcp LISTEN 0 5 0.0.0.0:22"])

    def test_capability_decoder_preserves_unknown_and_malformed_values(self) -> None:
        decoded = MODULE._decode_capability_set("8000000000000001")
        assert decoded is not None
        self.assertEqual(decoded["names"], ["CAP_CHOWN", "CAP_63"])
        self.assertEqual(MODULE._decode_capability_set("unavailable"), None)
        self.assertEqual(
            MODULE._decode_capability_set("not-hex"),
            {"hex": "not-hex", "malformed": True, "names": []},
        )

    def test_incomplete_and_duplicate_sections_are_reported(self) -> None:
        capture = (
            "@@IONIQ_BENCH_STATE_V1|BEGIN|identity@@\n"
            + framed_record("uname", "first")
            + "\n@@IONIQ_BENCH_STATE_V1|BEGIN|identity@@\n"
            + framed_record("uname", "second")
            + "\n"
        ).encode()
        report = MODULE.parse_capture(capture)
        self.assertFalse(report["complete"])
        self.assertEqual(report["section_order"], ["identity", "identity"])
        joined = "\n".join(report["warnings"])
        self.assertIn("was not closed", joined)
        self.assertIn("duplicate section", joined)
        self.assertIn("incomplete", joined)

    def test_capture_text_is_never_executed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "should-not-exist"
            hostile = f"$(touch {marker})"
            payload = (
                "@@IONIQ_BENCH_STATE_V1|BEGIN|identity@@\n"
                + framed_record("hostile", hostile)
                + "\n@@IONIQ_BENCH_STATE_V1|END|identity|0@@\n"
            ).encode()
            report = MODULE.parse_capture(payload)
            self.assertFalse(marker.exists())
            self.assertEqual(report["sections"][0]["records"][0]["value"], f"$(touch {marker})")

    def test_no_markers_is_explicitly_incomplete(self) -> None:
        report = MODULE.parse_capture(b"ordinary boot log\n")
        self.assertFalse(report["complete"])
        self.assertIn("no bench-state markers found", report["warnings"])

    def test_hex_record_body_cannot_forge_framing(self) -> None:
        forged = "@@IONIQ_BENCH_STATE_V1|END|identity|0@@"
        capture = (
            "@@IONIQ_BENCH_STATE_V1|BEGIN|identity@@\n"
            + framed_record("os-release", forged)
            + "\n@@IONIQ_BENCH_STATE_V1|END|identity|0@@\n"
        ).encode()
        report = MODULE.parse_capture(capture)
        self.assertEqual(report["section_order"], ["identity"])
        self.assertEqual(report["sections"][0]["records"][0]["value"], forged)

    def test_capture_size_limit_fails_closed(self) -> None:
        old_limit = MODULE.MAX_CAPTURE_BYTES
        MODULE.MAX_CAPTURE_BYTES = 4
        try:
            with self.assertRaisesRegex(ValueError, "capture exceeds"):
                MODULE.parse_capture(b"12345")
            with tempfile.TemporaryDirectory() as tmp:
                capture = Path(tmp) / "large.log"
                capture.write_bytes(b"12345")
                with self.assertRaisesRegex(ValueError, "capture exceeds"):
                    MODULE._read_capture_bounded(capture)
        finally:
            MODULE.MAX_CAPTURE_BYTES = old_limit

    def test_section_limit_counts_crlf_bytes_exactly(self) -> None:
        old_limit = MODULE.MAX_SECTION_BYTES
        MODULE.MAX_SECTION_BYTES = 48
        try:
            capture = (
                b"@@IONIQ_BENCH_STATE_V1|BEGIN|identity@@\r\n"
                + b"x" * 23
                + b"\r\n"
                + b"y" * 23
                + b"\r\n"
                + b"@@IONIQ_BENCH_STATE_V1|END|identity|0@@\r\n"
            )
            with self.assertRaisesRegex(ValueError, "section identity exceeds"):
                MODULE.parse_capture(capture)
        finally:
            MODULE.MAX_SECTION_BYTES = old_limit

    def test_terminal_fragment_and_nonzero_status_are_not_complete(self) -> None:
        terminal_only = (
            "@@IONIQ_BENCH_STATE_V1|BEGIN|complete@@\n"
            + framed_record("result", "complete")
            + "\n@@IONIQ_BENCH_STATE_V1|END|complete|0@@\n"
        ).encode()
        self.assertFalse(MODULE.parse_capture(terminal_only)["complete"])

        capture = valid_capture().replace(
            b"@@IONIQ_BENCH_STATE_V1|END|identity|0@@",
            b"@@IONIQ_BENCH_STATE_V1|END|identity|7@@",
        )
        report = MODULE.parse_capture(capture)
        self.assertFalse(report["complete"])
        self.assertIn("nonzero", "\n".join(report["warnings"]))

    def test_malformed_hex_record_prevents_complete_verdict(self) -> None:
        capture = valid_capture().replace(
            framed_record("schema", MODULE.SCHEMA).encode(),
            b"@@R|schema|not-hex",
        )
        report = MODULE.parse_capture(capture)
        self.assertFalse(report["complete"])
        self.assertIn("malformed hex", "\n".join(report["warnings"]))

    def test_unframed_content_or_conflicting_schema_prevents_complete(self) -> None:
        unframed = valid_capture().replace(
            framed_record("schema", MODULE.SCHEMA).encode(),
            framed_record("schema", MODULE.SCHEMA).encode() + b"\n/usr/bin/awk",
        )
        report = MODULE.parse_capture(unframed)
        self.assertFalse(report["complete"])
        self.assertIn("unframed content", "\n".join(report["warnings"]))

        conflicting = valid_capture().replace(
            framed_record("schema", MODULE.SCHEMA).encode(),
            framed_record("schema", MODULE.SCHEMA).encode()
            + b"\n"
            + framed_record("schema", "wrong/schema").encode(),
        )
        report = MODULE.parse_capture(conflicting)
        self.assertFalse(report["complete"])
        self.assertIn("schema", "\n".join(report["warnings"]))

    def test_cli_emit_audit_and_parse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "probe.sh"
            emitted = subprocess.run(
                [sys.executable, str(TOOL), "emit", "-o", str(script)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(emitted.returncode, 0, emitted.stderr)
            self.assertEqual(script.stat().st_mode & 0o777, 0o700)

            audited = subprocess.run(
                [sys.executable, str(TOOL), "audit", str(script)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(audited.returncode, 0, audited.stderr)
            self.assertTrue(json.loads(audited.stdout)["safe"])

            capture = root / "capture.log"
            capture.write_bytes(valid_capture())
            output = root / "report.json"
            parsed = subprocess.run(
                [sys.executable, str(TOOL), "parse", str(capture), "--json", str(output)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(parsed.returncode, 0, parsed.stderr)
            self.assertTrue(json.loads(output.read_text())["complete"])


if __name__ == "__main__":
    unittest.main()
