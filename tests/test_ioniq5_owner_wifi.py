"""Fixture-only tests for the independent IONIQ5 owner Wi-Fi overlay."""
from __future__ import annotations

import configparser
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import textwrap
import time
import unittest


REPOSITORY = Path(__file__).parents[1]
TOOL = REPOSITORY / "tools/uk_fw/ioniq5_owner_wifi.py"
SPEC = importlib.util.spec_from_file_location("ioniq5_owner_wifi", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load owner Wi-Fi tool")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class OwnerWifiFixtureTests(unittest.TestCase):
    """Exercise generation, policy, and startup behavior without hardware."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="owner-wifi-test-")
        # unittest runs cleanups in reverse order: stop later-registered child
        # processes before removing files their EXIT handlers can still write.
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.fixture_index = 0
        self.current_marker = self.root / "unset-wpa-marker"
        self.passphrase = self.root / "passphrase.txt"
        self.passphrase.write_bytes(b"correct horse battery\n")
        self.output = self.root / "overlay"
        self.manifest = MODULE.ioniq5_owner_wifi_generate(
            output=self.output,
            passphrase_file=self.passphrase,
        )
        self.startup = self.output / "opt/ioniq-owner/start-owner-wifi"
        self.wpa_config = self.output / MODULE._WPA_CONFIG

    def make_sysfs(self) -> Path:
        """Create the stock-style netlink and cfg80211 marker."""
        self.fixture_index += 1
        sysroot = self.root / f"sys-{self.fixture_index}"
        interface = sysroot / "devices/platform/wifi/net/wlan0"
        interface.mkdir(parents=True)
        (interface / "ifindex").write_text("17\n")
        (interface / "phy80211").mkdir()
        class_net = sysroot / "class/net"
        class_net.mkdir(parents=True)
        os.symlink(interface, class_net / "wlan0")
        return sysroot

    def write_stub(self, path: Path, content: str) -> None:
        """Write one executable fixture command."""
        path.write_text(textwrap.dedent(content))
        path.chmod(0o755)

    def make_stubs(self, sysroot: Path) -> tuple[Path, Path]:
        """Create only commands needed by the generated startup script."""
        bin_dir = self.root / f"stubbin-{self.fixture_index}"
        bin_dir.mkdir()
        log = self.root / "commands.log"
        log.write_text("")

        self.write_stub(
            bin_dir / "modprobe",
            """\
            #! /bin/sh
            printf 'modprobe %s\\n' "$*" >>"$WIFI_STUB_LOG"
            [ "${WIFI_MODPROBE_FAIL:-0}" != 1 ] || exit 1
            exit 0
            """,
        )
        self.write_stub(
            bin_dir / "pidof",
            """\
            #! /bin/sh
            printf 'pidof %s\\n' "$*" >>"$WIFI_STUB_LOG"
            if [ "${WIFI_EXISTING_WPA:-0}" = 1 ] && [ "$1" = wpa_supplicant ]; then
                echo 999
                exit 0
            fi
            exit 1
            """,
        )
        self.write_stub(
            bin_dir / "iw",
            """\
            #! /bin/sh
            printf 'iw %s\\n' "$*" >>"$WIFI_STUB_LOG"
            if [ "$*" = 'dev wlan0 info' ]; then
                if [ -e "$WIFI_WPA_READY" ]; then
                    echo '        type AP'
                else
                    echo '        type managed'
                fi
                exit 0
            fi
            exit 0
            """,
        )
        self.write_stub(
            bin_dir / "ip",
            """\
            #! /bin/sh
            printf 'ip %s\\n' "$*" >>"$WIFI_STUB_LOG"
            [ "${WIFI_IP_FAIL:-0}" != 1 ] || exit 1
            case " $* " in
                *" -4 -o addr show "*)
                    [ "${WIFI_ADDRESS_CONFLICT:-0}" != 1 ] ||
                        echo '4: wlan0 inet 10.99.0.2/24 scope global wlan0'
                    ;;
                *" -4 route show exact 10.43.0.0/24 "*)
                    [ "${WIFI_ROUTE_CONFLICT:-0}" != 1 ] ||
                        echo '10.43.0.0/24 dev acme0 proto static'
                    ;;
                *" -o link show dev wlan0 "*)
                    echo '7: wlan0: <BROADCAST,MULTICAST> mtu 1500'
                    ;;
            esac
            exit 0
            """,
        )
        firewall = """\
            #! /bin/sh
            tool=${0##*/}
            printf '%s %s\\n' "$tool" "$*" >>"$WIFI_STUB_LOG"
            case "$1 " in
                "-L ") [ "${WIFI_FIREWALL_COLLISION:-0}" = 1 ] && exit 0; exit 1 ;;
                "-N ") [ "${WIFI_FIREWALL_FAIL:-0}" != 1 ] ||
                    [ "$2" != IONIQ5_WIFI_OUTPUT ] || exit 1 ;;
            esac
            exit 0
        """
        self.write_stub(bin_dir / "iptables", firewall)
        self.write_stub(bin_dir / "ip6tables", firewall)
        self.write_stub(
            bin_dir / "wpa_supplicant",
            """\
            #! /bin/sh
            printf 'wpa_supplicant %s\\n' "$*" >>"$WIFI_STUB_LOG"
            [ "${WIFI_WPA_FAIL:-0}" != 1 ] || exit 1
            : >"$WIFI_WPA_READY"
            exec /bin/sleep 30
            """,
        )
        self.write_stub(
            bin_dir / "wpa_cli",
            """\
            #! /bin/sh
            printf 'wpa_cli %s\\n' "$*" >>"$WIFI_STUB_LOG"
            [ -e "$WIFI_WPA_READY" ] || exit 1
            echo PONG
            exit 0
            """,
        )
        self.write_stub(
            bin_dir / "dropbear",
            """\
            #! /bin/sh
            printf 'dropbear %s\\n' "$*" >>"$WIFI_STUB_LOG"
            [ "${WIFI_DROPBEAR_FAIL:-0}" != 1 ] || exit 1
            if [ -n "${WIFI_MUTATE_IFINDEX:-}" ]; then
                printf '%s\\n' "$WIFI_MUTATE_IFINDEX" \
                    >"$WIFI_SYSROOT/class/net/wlan0/ifindex"
            fi
            exec /bin/sleep 30
            """,
        )
        self.write_stub(
            bin_dir / "mount",
            """\
            #! /bin/sh
            printf 'mount %s\\n' "$*" >>"$WIFI_STUB_LOG"
            exit 0
            """,
        )
        self.write_stub(
            bin_dir / "chown",
            """\
            #! /bin/sh
            printf 'chown %s\\n' "$*" >>"$WIFI_STUB_LOG"
            exit 0
            """,
        )
        self.write_stub(
            bin_dir / "stat",
            """\
            #! /bin/sh
            printf 'stat %s\\n' "$*" >>"$WIFI_STUB_LOG"
            case "$3" in
                *authorized_keys|*dropbear_ed25519_host_key|*owner_password_hash|*wpa_supplicant.conf)
                    echo '0:0:600'
                    ;;
                *) echo '0:0:700' ;;
            esac
            """,
        )
        self.write_stub(
            bin_dir / "sleep",
            """\
            #! /bin/sh
            /bin/sleep 0.01
            """,
        )
        return bin_dir, log

    def prepare_runtime(self, sysroot: Path) -> tuple[Path, Path, Path]:
        """Relocate generated absolute paths into the fixture tree."""
        self.fixture_index += 1
        source = self.startup.read_text()
        bin_dir, log = self.make_stubs(sysroot)
        runtime_base = self.root / f"runtime-base-{self.fixture_index}"
        self.current_marker = self.root / f"wpa-ready-{self.fixture_index}"
        (runtime_base / "keys").mkdir(parents=True)
        (runtime_base / "wifi").mkdir()
        (runtime_base / "bin").mkdir()
        for name in (
            "authorized_keys",
            "dropbear_ed25519_host_key",
        ):
            (runtime_base / "keys" / name).write_text("fixture\n")
        (runtime_base / "keys/owner_password_hash").write_text(
            "$6$rounds=5000$saltstring$" + "A" * 86 + "\n"
        )
        (runtime_base / "wifi/wpa_supplicant.conf").write_bytes(
            self.wpa_config.read_bytes()
        )
        (runtime_base / "bin/dropbear").write_text("")
        source = source.replace(
            "exec >>/var/log/IONIQ5_OWNER_WIFI.log 2>&1",
            f"exec >>'{log}' 2>&1",
        )
        source = source.replace(
            "PATH=/opt/ioniq-owner/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            f"PATH={bin_dir}:/usr/sbin:/usr/bin:/sbin:/bin",
        )
        source = source.replace(
            "base=/opt/ioniq-owner",
            f"base={runtime_base}",
        )
        source = source.replace(
            "run=/run/ioniq5-owner-wifi",
            f"run={self.root / 'run'}",
        )
        source = source.replace("sysroot=/sys", f"sysroot={sysroot}")
        source = source.replace("wait_count=15", "wait_count=1")
        source = source.replace("ap_wait=15", "ap_wait=2")
        source = source.replace(
            '"$base/bin/dropbear"',
            f"'{bin_dir / 'dropbear'}'",
        )
        script = self.root / "start-owner-wifi"
        script.write_text(source)
        return script, log, runtime_base

    def environment(self, sysroot: Path, log: Path) -> dict[str, str]:
        """Return fixture environment with bounded subprocess paths."""
        return os.environ | {
            "WIFI_STUB_LOG": str(log),
            "WIFI_SYSROOT": str(sysroot),
            "WIFI_WPA_READY": str(self.current_marker),
        }

    def start_runtime(
        self,
        *,
        extra: dict[str, str] | None = None,
    ) -> tuple[subprocess.Popen[str], Path, Path]:
        """Start the service and wait for its boot-visible AP status line."""
        sysroot = self.make_sysfs()
        script, log, runtime_base = self.prepare_runtime(sysroot)
        environment = self.environment(sysroot, log)
        if extra:
            environment.update(extra)
        process = subprocess.Popen(
            ["/bin/sh", str(script)],
            env=environment,
            text=True,
        )
        self.addCleanup(self.stop_runtime, process)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            current = log.read_text() if log.exists() else ""
            mutation_done = (
                not extra
                or not extra.get("WIFI_MUTATE_IFINDEX")
                or (sysroot / "class/net/wlan0/ifindex").read_text().strip()
                == extra["WIFI_MUTATE_IFINDEX"]
            )
            if (
                "IONIQ5_OWNER_WIFI_VERSION=1.0.0" in current
                and "dropbear -F" in current
                and mutation_done
            ):
                return process, log, runtime_base
            if process.poll() is not None:
                self.fail(f"owner Wi-Fi startup exited early: {current}")
            time.sleep(0.02)
        process.kill()
        process.wait(timeout=2)
        self.fail("owner Wi-Fi startup did not reach its status line")

    def run_to_finish(
        self,
        *,
        extra: dict[str, str] | None = None,
        create_sysfs: bool = True,
        timeout: int = 8,
    ) -> tuple[subprocess.CompletedProcess[str], Path, Path]:
        """Run one rejection or bounded startup path with fixture commands."""
        if create_sysfs:
            sysroot = self.make_sysfs()
        else:
            sysroot = self.root / "sys"
            sysroot.mkdir()
        script, log, runtime_base = self.prepare_runtime(sysroot)
        environment = self.environment(sysroot, log)
        if extra:
            environment.update(extra)
        result = subprocess.run(
            ["/bin/sh", str(script)],
            env=environment,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return result, log, runtime_base

    def stop_runtime(self, process: subprocess.Popen[str]) -> None:
        """Send TERM and require the owned child cleanup to finish."""
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
        process.wait(timeout=5)

    def test_config_policy_and_shell_syntax(self) -> None:
        syntax = subprocess.run(
            ["/bin/sh", "-n", str(self.startup)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(syntax.returncode, 0, syntax.stderr)
        source = self.startup.read_text()
        self.assertIn("modprobe bcmdhd", source)
        self.assertIn(
            'wpa_supplicant -Dnl80211 -i"$iface" -c "$base/wifi/wpa_supplicant.conf"',
            source,
        )
        self.assertNotIn("? wpa_supplicant", source)
        self.assertIn('"$base/bin/dropbear" -F -m -l "$iface" -p 10.43.0.1:22', source)
        self.assertIn('-D "$auth_dir"', source)
        self.assertNotIn(
            '-p 10.43.0.1:22 \\\n    -s',
            source,
        )
        self.assertIn("-i \"$iface\" -s 10.43.0.0/24 -d 10.43.0.1", source)
        for forbidden in (
            "systemctl",
            "pkill",
            "rfkill",
            "/tmp/no_unece",
            "ip route add",
            "MASQUERADE",
            "ownerusb0",
        ):
            self.assertNotIn(forbidden, source)
        self.assertNotIn("ip addr flush", source)

        config = self.wpa_config.read_text()
        self.assertIn("mode=2", config)
        self.assertIn("ssid=494f4e4951352d4f776e6572", config)
        self.assertIn("key_mgmt=WPA-PSK", config)
        self.assertIn("proto=RSN", config)
        self.assertIn("pairwise=CCMP", config)
        self.assertIn("group=CCMP", config)
        self.assertIn("frequency=2412", config)
        self.assertNotIn("correct horse battery", config)
        generated_bytes = b"".join(
            path.read_bytes()
            for path in self.output.rglob("*")
            if path.is_file()
        )
        self.assertNotIn(b"correct horse battery", generated_bytes)
        expected_psk = hashlib.pbkdf2_hmac(
            "sha1",
            b"correct horse battery",
            b"IONIQ5-Owner",
            4096,
            32,
        ).hex()
        self.assertIn(f"psk={expected_psk}", config)

    def test_manifest_modes_determinism_and_boot_enable(self) -> None:
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.wpa_config.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.manifest["ssid"], "IONIQ5-Owner")
        self.assertEqual(self.manifest["interface"], "wlan0")
        self.assertEqual(self.manifest["ssh_address"], "10.43.0.1:22")
        self.assertNotIn("correct horse battery", json.dumps(self.manifest))
        for name, entry in self.manifest["files"].items():
            path = self.output / name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"])
            self.assertEqual(path.stat().st_mode & 0o777, int(entry["mode"], 8))
            self.assertEqual((entry["uid"], entry["gid"]), (0, 0))
        for name, target in self.manifest["symlinks"].items():
            self.assertFalse(Path(target).is_absolute())
            resolved = (self.output / name).parent / target
            self.assertTrue(
                resolved.resolve().is_relative_to(self.output.resolve())
            )
            self.assertEqual(os.readlink(self.output / name), target)
        enabled = self.output / "etc/systemd/system/multi-user.target.wants/ioniq5-owner-wifi.service"
        self.assertTrue(enabled.is_symlink())
        unit = (self.output / MODULE._UNIT_FILE).read_text()
        self.assertIn("WantedBy=multi-user.target", unit)
        self.assertNotIn("ownerusb0", unit)
        self.assertNotIn("Requires=ioniq-owner-ssh", unit)
        second_passphrase = self.root / "second-passphrase"
        second_passphrase.write_text("another valid passphrase\n")
        second = self.root / "second"
        second_manifest = MODULE.ioniq5_owner_wifi_generate(
            output=second,
            passphrase_file=second_passphrase,
            ssid="Second Owner AP",
        )
        self.assertEqual(second_manifest["ssid"], "Second Owner AP")
        self.assertNotEqual(second_manifest["files"], self.manifest["files"])
        self.assertEqual(
            (second / "opt/ioniq-owner/start-owner-wifi").read_text(),
            self.startup.read_text(),
        )

    def test_connman_and_vendor_suppression_are_narrow(self) -> None:
        existing = self.root / "main.conf"
        existing.write_text(
            "[General]\n"
            "NetworkInterfaceBlacklist=eth0, ownerusb0\n"
            "OtherOption=keep-me\n"
        )
        output = self.root / "merged"
        MODULE.ioniq5_owner_wifi_generate(
            output=output,
            passphrase_file=self.passphrase,
            connman_config=existing,
        )
        parser = configparser.ConfigParser(interpolation=None)
        parser.read_string((output / MODULE._CONNMAN_CONFIG).read_text())
        excluded = set(parser["General"]["NetworkInterfaceBlacklist"].split(","))
        self.assertEqual(excluded, {"eth0", "ownerusb0", "wlan0"})
        self.assertEqual(parser["General"]["OtherOption"], "keep-me")
        dropin = (output / MODULE._VENDOR_DROPIN).read_text()
        self.assertIn(
            "ConditionPathExists=!/opt/ioniq-owner/wifi/vendor-manager-suppressed",
            dropin,
        )
        self.assertNotIn("mask", dropin)
        self.assertNotIn("systemctl", dropin)
        self.assertEqual(
            (output / MODULE._MODULES_LOAD).read_text(),
            "cfg80211\nbcmdhd\n",
        )

    def test_credentials_and_ssid_are_strictly_bounded(self) -> None:
        cases = (
            b"1234567\n",
            b"x" * 64 + b"\n",
            b"correct\tpassword\n",
            "caf\u00e9password".encode("utf-8"),
            b"line\nbreak\n",
            b"",
        )
        for index, data in enumerate(cases):
            path = self.root / f"bad-pass-{index}"
            path.write_bytes(data)
            output = self.root / f"bad-output-{index}"
            with self.subTest(data=data), self.assertRaises(ValueError):
                MODULE.ioniq5_owner_wifi_generate(
                    output=output,
                    passphrase_file=path,
                )
            self.assertFalse(output.exists())
        for index, ssid in enumerate(("", "x" * 33, "bad\nssid", "caf\u00e9", 5)):
            output = self.root / f"bad-ssid-{index}"
            with self.subTest(ssid=ssid), self.assertRaises(ValueError):
                MODULE.ioniq5_owner_wifi_generate(
                    output=output,
                    passphrase_file=self.passphrase,
                    ssid=ssid,
                )
            self.assertFalse(output.exists())
        passphrase_link = self.root / "passphrase-link"
        passphrase_link.symlink_to(self.passphrase)
        with self.assertRaises(OSError):
            MODULE.ioniq5_owner_wifi_generate(
                output=self.root / "symlink-output",
                passphrase_file=passphrase_link,
            )

    def test_happy_path_owns_only_wifi_state_and_restores_managed_mode(self) -> None:
        process, log, _ = self.start_runtime()
        commands = log.read_text()
        self.assertIn("modprobe bcmdhd", commands)
        self.assertIn("ip link set wlan0 down", commands)
        self.assertIn("wpa_supplicant -Dnl80211 -iwlan0", commands)
        self.assertIn("ip addr add 10.43.0.1/24 dev wlan0", commands)
        self.assertIn(
            "iptables -A IONIQ5_WIFI_INPUT -i wlan0 -s 10.43.0.0/24 "
            "-d 10.43.0.1 -p tcp --dport 22",
            commands,
        )
        self.assertIn(
            "dropbear -F -m -l wlan0 -p 10.43.0.1:22",
            commands,
        )
        self.assertNotIn("ownerusb0", commands)
        self.assertNotIn("ip route add default", commands)
        runtime_key = self.root / "run/.ssh/authorized_keys"
        self.assertEqual(runtime_key.read_text(), "fixture\n")
        self.assertEqual(runtime_key.stat().st_mode & 0o777, 0o600)

        self.stop_runtime(process)
        commands = log.read_text()
        self.assertIn("ip addr del 10.43.0.1/24 dev wlan0", commands)
        self.assertIn("iptables -D INPUT -j IONIQ5_WIFI_INPUT", commands)
        self.assertIn("ip6tables -X IONIQ5_WIFI_FORWARD", commands)
        self.assertIn("iw dev wlan0 set type managed", commands)

    def test_missing_radio_and_preexisting_supplicant_fail_before_mutation(self) -> None:
        result, log, _ = self.run_to_finish(create_sysfs=False)
        self.assertNotEqual(result.returncode, 0)
        commands = log.read_text()
        self.assertIn("did not appear", commands)
        self.assertNotIn("wpa_supplicant -D", commands)
        self.assertNotIn("ip addr add", commands)

        result, log, _ = self.run_to_finish(extra={"WIFI_EXISTING_WPA": "1"})
        self.assertNotEqual(result.returncode, 0)
        commands = log.read_text()
        self.assertIn("pre-existing wpa_supplicant", commands)
        self.assertNotIn("ip link set", commands)
        self.assertNotIn("wpa_supplicant -D", commands)

    def test_address_route_and_firewall_collisions_preserve_foreign_state(self) -> None:
        for variable, message in (
            ("WIFI_ADDRESS_CONFLICT", "already has an IPv4 address"),
            ("WIFI_ROUTE_CONFLICT", "subnet conflicts"),
            ("WIFI_FIREWALL_COLLISION", "firewall name collision"),
        ):
            with self.subTest(variable=variable):
                result, log, _ = self.run_to_finish(extra={variable: "1"})
                self.assertNotEqual(result.returncode, 0)
                commands = log.read_text()
                self.assertIn(message, commands)
                self.assertNotIn("ip link set wlan0 down", commands)
                self.assertNotIn("wpa_supplicant -D", commands)

    def test_bad_password_hash_and_wpa_failure_cleanup(self) -> None:
        sysroot = self.make_sysfs()
        script, log, runtime_base = self.prepare_runtime(sysroot)
        (runtime_base / "keys/owner_password_hash").write_text("*\n")
        environment = self.environment(sysroot, log)
        result = subprocess.run(
            ["/bin/sh", str(script)],
            env=environment,
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("password hash rejected", log.read_text())
        self.assertNotIn("wpa_supplicant -D", log.read_text())

        for variable in ("WIFI_WPA_FAIL", "WIFI_DROPBEAR_FAIL", "WIFI_FIREWALL_FAIL", "WIFI_IP_FAIL"):
            with self.subTest(variable=variable):
                result, log, _ = self.run_to_finish(extra={variable: "1"})
                self.assertNotEqual(result.returncode, 0)
                commands = log.read_text()
                self.assertNotIn("ip route add", commands)
                if variable == "WIFI_WPA_FAIL":
                    self.assertNotIn("ip addr add", commands)
                elif variable in ("WIFI_DROPBEAR_FAIL", "WIFI_FIREWALL_FAIL"):
                    self.assertIn("iptables -X IONIQ5_WIFI_INPUT", commands)

    def test_name_reuse_never_removes_replacement_state(self) -> None:
        process, log, _ = self.start_runtime(extra={"WIFI_MUTATE_IFINDEX": "999"})
        self.stop_runtime(process)
        commands = log.read_text()
        self.assertIn("ip addr add 10.43.0.1/24 dev wlan0", commands)
        self.assertNotIn("ip addr del 10.43.0.1/24 dev wlan0", commands)
        self.assertNotIn("iw dev wlan0 set type managed", commands)

    def test_output_failure_rolls_back_without_deleting_foreign_files(self) -> None:
        foreign = self.output / "sentinel"
        foreign.write_text("keep")
        with self.assertRaises(ValueError):
            MODULE.ioniq5_owner_wifi_generate(
                output=self.output,
                passphrase_file=self.passphrase,
            )
        self.assertEqual(foreign.read_text(), "keep")
        failed = self.root / "failed"
        real_write = Path.write_bytes

        def fail_config(path: Path, data: bytes) -> int:
            if path.name == "main.conf":
                raise OSError("simulated write failure")
            return real_write(path, data)

        from unittest import mock
        with mock.patch.object(Path, "write_bytes", fail_config), self.assertRaises(OSError):
            MODULE.ioniq5_owner_wifi_generate(
                output=failed,
                passphrase_file=self.passphrase,
            )
        self.assertFalse(failed.exists())
        self.assertFalse(failed.with_name(failed.name + ".manifest.json").exists())
        self.assertEqual(list(self.root.glob(".ioniq5-owner-wifi-*")), [])

    def test_cli_accepts_ssid_and_preserves_existing_connman(self) -> None:
        existing = self.root / "cli-main.conf"
        existing.write_text("[General]\nNetworkInterfaceBlacklist=eth0\n")
        output = self.root / "cli"
        argv = [
            "--output", str(output),
            "--passphrase-file", str(self.passphrase),
            "--connman-config", str(existing),
            "--ssid", "Owner Test AP",
        ]
        from unittest import mock
        with mock.patch("builtins.print"):
            self.assertEqual(MODULE.ioniq5_owner_wifi_main(argv), 0)
        manifest = json.loads(
            output.with_name(output.name + ".manifest.json").read_text()
        )
        self.assertEqual(manifest["ssid"], "Owner Test AP")
        self.assertIn("wlan0", (output / MODULE._CONNMAN_CONFIG).read_text())


class RetainedRadioEvidenceTests(unittest.TestCase):
    """Check retained stock evidence without executing target programs."""

    def test_stock_radio_binaries_modules_and_disabling_policy_exist(self) -> None:
        rootfs = REPOSITORY / "work/decrypted-eu-260128/extracted-safe/mango-rootfs"
        modules = rootfs / "lib/modules/4.1.27-abl"
        required = (
            rootfs / "usr/sbin/wpa_supplicant",
            rootfs / "usr/sbin/wpa_cli",
            rootfs / "usr/sbin/iw",
            modules / "kernel/net/wireless/cfg80211.ko",
            modules / "kernel/drivers/net/wireless/bcmdhd/bcmdhd.ko",
        )
        if not all(path.is_file() for path in required):
            self.skipTest("retained private rootfs unavailable")
        self.assertEqual(
            (rootfs / "etc/modprobe.d/wifi_disable.conf").read_text(),
            "blacklist bcmdhd\nblacklist cfg80211\n",
        )
        manager = (rootfs / "lib/systemd/system/supplicantmanager.service").read_text()
        self.assertIn("ExecStartPre=/sbin/modprobe cfg80211", manager)
        self.assertIn("ExecStart=/app/bin/supplicantmanager", manager)
        path_unit = (rootfs / "lib/systemd/system/supplicantmanager.path").read_text()
        self.assertIn("PathExists=/tmp/no_unece", path_unit)
        binary = (rootfs / "usr/sbin/wpa_supplicant").read_bytes()
        for marker in (
            b"No SSID configured for AP mode",
            b"Driver does not support AP mode",
            b"nl80211: beacon_int=%d",
        ):
            self.assertIn(marker, binary)


if __name__ == "__main__":
    unittest.main()
