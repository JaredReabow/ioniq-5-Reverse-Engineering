"""Fixture-only tests for the IONIQ5 USB-Ethernet owner SSH overlay."""
from __future__ import annotations

import configparser
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import struct
import subprocess
import tempfile
import textwrap
import time
import unittest
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


REPOSITORY = Path(__file__).parents[1]
TOOL = REPOSITORY / "tools/uk_fw/ioniq5_owner_ssh.py"
SPEC = importlib.util.spec_from_file_location("ioniq5_owner_ssh", TOOL)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load owner SSH tool")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def ssh_string(value: bytes) -> bytes:
    """Encode one SSH length-prefixed byte string."""
    return len(value).to_bytes(4, "big") + value


def fixture_elf() -> bytes:
    """Build a structural static ELF containing the required version markers."""
    payload = (
        b"SSH-2.0-dropbear_2026.94\0dropbear\0dropbearkey\0scp\0"
        + b"\0" * 128
    )
    ident = b"\x7fELF\x02\x01\x01" + b"\0" * 9
    header = struct.pack(
        "<16sHHIQQQIHHHHHH",
        ident,
        2,
        62,
        1,
        0x400078,
        64,
        0,
        0,
        64,
        56,
        1,
        0,
        0,
        0,
    )
    program = struct.pack(
        "<IIQQQQQQ",
        1,
        5,
        120,
        0x400000,
        0,
        len(payload),
        len(payload),
        0x1000,
    )
    return header + program + payload


class OwnerSshFixtureTests(unittest.TestCase):
    """Exercise generated policy and startup behavior with fixture files only."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.original_digest = MODULE._PINNED_BINARY_SHA256
        MODULE._PINNED_BINARY_SHA256 = hashlib.sha256(fixture_elf()).hexdigest()

    @classmethod
    def tearDownClass(cls) -> None:
        MODULE._PINNED_BINARY_SHA256 = cls.original_digest

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="owner-ssh-test-")
        self.root = Path(self.temporary.name).resolve()
        self.sysroot = self.root / "sys"
        self.class_net = self.sysroot / "class/net"
        self.class_net.mkdir(parents=True)
        self.owner_home = self.root / "home/root"
        self.owner_home.mkdir(parents=True)
        self.binary = self.root / "dropbearmulti"
        self.binary.write_bytes(fixture_elf())
        self.binary.chmod(0o755)
        self.public = self.root / "public.pub"
        self.host = self.root / "dropbear_host_key"
        self._write_keys()
        self.interface_links: dict[str, tuple[Path, Path]] = {}
        self.make_interface("ownerusb0", "r8152", slot=1)
        self.output = self.root / "overlay"
        self.manifest = MODULE.ioniq5_owner_ssh_generate(
            dropbear=self.binary,
            public_key=self.public,
            host_key=self.host,
            output=self.output,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_keys(self) -> None:
        private = Ed25519PrivateKey.generate()
        public = private.public_key().public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH,
        )
        self.public.write_bytes(public + b"\n")
        seed = private.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption(),
        )
        public_raw = private.public_key().public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        self.host.write_bytes(ssh_string(b"ssh-ed25519") + ssh_string(seed + public_raw))

    def make_interface(
        self,
        name: str,
        driver: str,
        *,
        slot: int,
        vendor: str = "0bda",
        product: str = "8153",
    ) -> Path:
        """Create a small sysfs graph with a real usbN ancestor."""
        usb_root = self.sysroot / "devices/pci0000:00/0000:00:14.0/usb1"
        usb_device = usb_root / f"1-{slot}"
        interface_device = usb_device / f"1-{slot}:1.0"
        interface_real = interface_device / "net" / name
        interface_real.mkdir(parents=True)
        usb_root.mkdir(parents=True, exist_ok=True)
        usb_device.mkdir(parents=True, exist_ok=True)
        (usb_device / "idVendor").write_text(vendor + "\n")
        (usb_device / "idProduct").write_text(product + "\n")
        (interface_real / "ifindex").write_text(str(10 + slot))
        driver_path = self.sysroot / "bus/usb/drivers" / driver
        driver_path.mkdir(parents=True, exist_ok=True)
        os.symlink(interface_device, interface_real / "device")
        os.symlink(driver_path, interface_device / "driver")
        class_link = self.class_net / name
        os.symlink(interface_real, class_link)
        self.interface_links[name] = (class_link, interface_device)
        return class_link

    def replace_interface_name(self, old: str, new: str, *, slot: int = 2) -> None:
        """Replace the sole fixture NIC with a new sysfs identity and name."""
        self.interface_links[old][0].unlink()
        self.interface_links.pop(old)
        self.make_interface(new, "r8152", slot=slot)

    def replace_driver(self, name: str, driver: str) -> None:
        """Retarget the fixture's bound-driver symlink."""
        _, interface_device = self.interface_links[name]
        driver_link = interface_device / "driver"
        driver_link.unlink()
        driver_path = self.sysroot / "bus/usb/drivers" / driver
        driver_path.mkdir(parents=True, exist_ok=True)
        os.symlink(driver_path, driver_link)

    def make_non_usb_interface(self) -> None:
        """Replace the fixture NIC with a non-USB network device."""
        class_link, _ = self.interface_links.pop("ownerusb0")
        class_link.unlink()
        device = self.sysroot / "devices/pci0000:00/nonusb"
        interface_real = device / "net/ownerusb0"
        interface_real.mkdir(parents=True)
        (interface_real / "ifindex").write_text("40\n")
        os.symlink(device, interface_real / "device")
        driver_path = self.sysroot / "bus/pci/drivers/e1000e"
        driver_path.mkdir(parents=True)
        os.symlink(driver_path, device / "driver")
        os.symlink(interface_real, self.class_net / "ownerusb0")

    def make_stubs(self) -> tuple[Path, Path]:
        """Create only the commands exercised by the generated startup script."""
        stub_bin = self.root / "stubbin"
        stub_bin.mkdir(exist_ok=True)
        log = self.root / "commands.log"
        log.write_text("")
        common = "#! /bin/sh\nprintf '%s\\n' \"$*\" >>\"$OWNER_STUB_LOG\"\n"
        (stub_bin / "ip").write_text(
            textwrap.dedent(
                """\
                #! /bin/sh
                printf 'ip %s\\n' "$*" >>"$OWNER_STUB_LOG"
                [ "${OWNER_IP_PROBE_FAIL:-0}" != 1 ] || exit 1
                if [ "${OWNER_ADDRESS_CONFLICT:-0}" = 1 ]; then
                    case " $* " in
                        *" -4 -o addr show "*)
                            echo "4: eth0 inet 10.99.0.2/24 scope global eth0"
                            ;;
                    esac
                fi
                if [ "${OWNER_ROUTE_CONFLICT:-0}" = 1 ]; then
                    case " $* " in
                        *" -4 route show exact 10.42.0.0/24 "*)
                            echo "10.42.0.0/24 dev oem0 proto static"
                            ;;
                    esac
                fi
                exit 0
                """
            )
        )
        firewall = textwrap.dedent(
            """\
            #! /bin/sh
            tool=${0##*/}
            printf '%s %s\\n' "$tool" "$*" >>"$OWNER_STUB_LOG"
            case "$1 " in
                "-L ") [ "${OWNER_FIREWALL_COLLISION:-0}" = 1 ] && exit 0; exit 1 ;;
                "-N ") [ "${OWNER_FIREWALL_FAIL:-0}" != 1 ] || [ "$2" != IONIQ5_OWNER_OUTPUT ] || exit 1 ;;
            esac
            exit 0
            """
        )
        (stub_bin / "iptables").write_text(firewall)
        (stub_bin / "ip6tables").write_text(firewall)
        (stub_bin / "dropbear").write_text(
            textwrap.dedent(
                """\
                #! /bin/sh
                printf 'dropbear %s\\n' "$*" >>"$OWNER_STUB_LOG"
                [ "${OWNER_CHILD_FAIL:-0}" != 1 ] || exit 1
                if [ -n "${OWNER_MUTATE_IFINDEX:-}" ]; then
                    printf '%s\\n' "$OWNER_MUTATE_IFINDEX" \
                        >"$OWNER_SYSROOT/class/net/ownerusb0/ifindex"
                fi
                exec /bin/sleep 30
                """
            )
        )
        (stub_bin / "mount").write_text(common + "exit 0\n")
        (stub_bin / "cp").write_text(
            common
            + '[ "${OWNER_KEY_COPY_FAIL:-0}" != 1 ] || exit 1\n'
            + 'exec /bin/cp "$@"\n'
        )
        (stub_bin / "chown").write_text(
            common + '[ "${OWNER_CHOWN_FAIL:-0}" != 1 ] || exit 1\nexit 0\n'
        )
        (stub_bin / "stat").write_text(
            textwrap.dedent(
                """\
                #! /bin/sh
                printf 'stat %s\\n' "$*" >>"$OWNER_STUB_LOG"
                if [ "${OWNER_BAD_METADATA:-0}" = 1 ]; then
                    echo '1000:1000:777'
                else
                    case "$3" in
                        */authorized_keys|*/owner_password_hash) echo '0:0:600' ;;
                        *) echo '0:0:700' ;;
                    esac
                fi
                """
            )
        )
        (stub_bin / "sleep").write_text("#! /bin/sh\n/bin/sleep 0.02\n")
        for name in (
            "ip", "iptables", "ip6tables", "dropbear", "sleep", "mount",
            "cp", "chown", "stat",
        ):
            (stub_bin / name).chmod(0o755)
        return stub_bin, log

    def runtime_script(self) -> tuple[Path, Path, Path]:
        """Relocate generated paths so the script can run without target access."""
        source = (self.output / "opt/ioniq-owner/start-owner-ssh").read_text()
        stub_bin, log = self.make_stubs()
        runtime_base = self.root / "runtime-base"
        runtime_base.mkdir(exist_ok=True)
        runtime_keys = runtime_base / "keys"
        runtime_keys.mkdir(exist_ok=True)
        (runtime_keys / "authorized_keys").write_bytes(
            (self.output / "opt/ioniq-owner/keys/authorized_keys").read_bytes()
        )
        (runtime_keys / "owner_password_hash").write_bytes(
            (self.output / "opt/ioniq-owner/keys/owner_password_hash").read_bytes()
        )
        source = source.replace(
            "exec >>/var/log/IONIQ5_OWNER_SSH.log 2>&1",
            f"exec >>'{log}' 2>&1",
        )
        source = source.replace(
            "exec >>/var/log/IONIQ5_OWNER_AUTH.log 2>&1",
            f"exec >>'{log}' 2>&1",
        )
        source = source.replace(
            "PATH=/opt/ioniq-owner/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            f"PATH={stub_bin}:/usr/sbin:/usr/bin:/sbin:/bin",
        )
        source = source.replace("base=/opt/ioniq-owner", f"base={runtime_base}")
        source = source.replace("run=/run/ioniq-owner", f"run={self.root / 'run'}")
        source = source.replace("sysroot=/sys", f"sysroot={self.sysroot}")
        source = source.replace("owner_home=/home/root", f"owner_home={self.owner_home}")
        source = source.replace("wait_seconds=30", "wait_seconds=1")
        source = source.replace(
            '"$base/bin/dropbear"',
            f"'{stub_bin / 'dropbear'}'",
        )
        script = self.root / "start-owner-ssh"
        script.write_text(source)
        return script, log, stub_bin

    def start_runtime(
        self,
        *,
        environment: dict[str, str] | None = None,
    ) -> tuple[subprocess.Popen[str], Path, Path]:
        """Start the fixture service and wait for its boot-visible version line."""
        script, log, stub_bin = self.runtime_script()
        run_environment = os.environ | {
            "OWNER_STUB_LOG": str(log),
            "OWNER_SYSROOT": str(self.sysroot),
        }
        if environment:
            run_environment.update(environment)
        process = subprocess.Popen(
            ["/bin/sh", str(script)],
            env=run_environment,
            text=True,
        )
        self.addCleanup(self.stop_runtime, process)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            current_log = log.read_text() if log.exists() else ""
            mutation_done = not environment or not environment.get("OWNER_MUTATE_IFINDEX") or (
                self.class_net / "ownerusb0/ifindex").read_text().strip() == environment["OWNER_MUTATE_IFINDEX"]
            if f"IONIQ5_OWNER_SSH_VERSION={MODULE._VERSION}" in current_log and "dropbear -F" in current_log and mutation_done:
                return process, log, stub_bin
            if process.poll() is not None:
                self.fail(f"owner startup exited early: {log.read_text()}")
            time.sleep(0.02)
        process.kill()
        process.wait(timeout=2)
        self.fail("owner startup did not reach its boot-visible version line")

    def run_to_finish(
        self,
        *,
        environment: dict[str, str] | None = None,
        timeout: int = 8,
    ) -> tuple[subprocess.CompletedProcess[str], Path]:
        """Run a rejection path with the same fixture commands."""
        script, log, _ = self.runtime_script()
        run_environment = os.environ | {
            "OWNER_STUB_LOG": str(log),
            "OWNER_SYSROOT": str(self.sysroot),
        }
        if environment:
            run_environment.update(environment)
        result = subprocess.run(
            ["/bin/sh", str(script)],
            env=run_environment,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return result, log

    def stop_runtime(self, process: subprocess.Popen[str]) -> None:
        """Send the service a TERM and require its bounded cleanup to finish."""
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
        process.wait(timeout=5)

    def test_generated_policy_and_shell_syntax(self) -> None:
        startup = self.output / "opt/ioniq-owner/start-owner-ssh"
        syntax = subprocess.run(
            ["/bin/sh", "-n", str(startup)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(syntax.returncode, 0, syntax.stderr)

        source = startup.read_text()
        self.assertIn("for netlink in \"$sysroot\"/class/net/ownerusb0", source)
        self.assertIn(
            '"$base/bin/dropbear" -F -m -l "$iface" -p 10.42.0.1:22',
            source,
        )
        self.assertIn('-D "$auth_dir"', source)
        self.assertNotIn('-D "$base/keys"', source)
        self.assertIn('owner_require_metadata "$auth_dir/authorized_keys" 600 file', source)
        self.assertNotIn(' -E ', source)
        self.assertIn("-i \"$iface\" -s 10.42.0.0/24 -d 10.42.0.1", source)
        self.assertNotIn("smsc95xx", source)
        self.assertIn("ip link set \"$iface\" down", source)
        self.assertNotIn("ip addr flush", source)
        self.assertNotIn("ip route add default", source)
        self.assertNotIn("systemctl stop", source)
        self.assertNotIn("systemctl mask", source)
        for forbidden in ("hostapd", "wpa_supplicant", "passphrase", "ssid"):
            self.assertNotIn(forbidden, source.lower())

        authorized = (self.output / "opt/ioniq-owner/keys/authorized_keys").read_text()
        self.assertIn("no-port-forwarding,no-agent-forwarding,no-X11-forwarding", authorized)
        self.assertNotIn("no-pty", authorized)

        unit = (self.output / "etc/systemd/system/ioniq-owner-ssh.service").read_text()
        self.assertIn("BindsTo=sys-subsystem-net-devices-ownerusb0.device", unit)
        self.assertIn("Restart=no", unit)
        self.assertNotIn("StartLimitIntervalSec", unit)
        self.assertNotIn("[Install]", unit)

        connman = configparser.ConfigParser(interpolation=None)
        connman.read_string((self.output / "etc/connman/main.conf").read_text())
        exclusions = set(
            connman["General"]["NetworkInterfaceBlacklist"].split(",")
        )
        self.assertTrue({"ownerusb0"} <= exclusions)
        self.assertTrue(
            any("modules-load" in str(path) for path in self.output.rglob("*"))
        )
        self.assertEqual(self.manifest["version"], MODULE._VERSION)
        self.assertEqual(
            set(self.manifest["usb_ids"]),
            set(MODULE.ioniq5_owner_ssh_usb_ids()),
        )
        self.assertTrue(any("Dropbear behavior" in item
                            for item in self.manifest["limitations"]))

    def test_happy_path_applies_only_owned_state_and_cleans_up(self) -> None:
        process, log, _ = self.start_runtime()
        commands_before_cleanup = log.read_text()
        self.assertIn("ip addr add 10.42.0.1/24 dev ownerusb0", commands_before_cleanup)
        self.assertIn(
            "iptables -A IONIQ5_OWNER_INPUT -i ownerusb0 -s 10.42.0.0/24 "
            "-d 10.42.0.1 -p tcp --dport 22",
            commands_before_cleanup,
        )
        self.assertIn(
            "ip6tables -A IONIQ5_OWNER_FORWARD -i ownerusb0 -j DROP",
            commands_before_cleanup,
        )
        self.assertIn(
            "dropbear -F -m -l ownerusb0 -p 10.42.0.1:22",
            commands_before_cleanup,
        )
        self.assertIn(" -D ", commands_before_cleanup)
        runtime_key = self.root / "run/.ssh/authorized_keys"
        self.assertEqual(
            runtime_key.read_bytes(),
            (self.output / "opt/ioniq-owner/keys/authorized_keys").read_bytes(),
        )
        self.assertEqual(runtime_key.stat().st_mode & 0o777, 0o600)
        self.assertEqual(commands_before_cleanup.count("ip link set ownerusb0 down"), 1)
        self.assertNotIn("ip addr flush", commands_before_cleanup)
        self.assertNotIn("ip route add default", commands_before_cleanup)

        self.stop_runtime(process)
        commands = log.read_text()
        self.assertIn("ip addr del 10.42.0.1/24 dev ownerusb0", commands)
        self.assertIn("iptables -D INPUT -j IONIQ5_OWNER_INPUT", commands)
        self.assertIn("ip6tables -X IONIQ5_OWNER_FORWARD", commands)
        self.assertEqual(commands.count("ip link set ownerusb0 down"), 2)

    def test_runtime_key_staging_failure_never_starts_dropbear(self) -> None:
        """A failed or unsafe runtime key path must fail before the listener."""
        for variable in ("OWNER_KEY_COPY_FAIL", "OWNER_CHOWN_FAIL", "OWNER_BAD_METADATA"):
            with self.subTest(variable=variable):
                result, log = self.run_to_finish(environment={variable: "1"})
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("dropbear -F", log.read_text())

    def test_runtime_key_symlink_is_rejected_before_dropbear(self) -> None:
        """Do not follow a pre-existing symlink in the private auth path."""
        run = self.root / "run"
        run.mkdir()
        foreign = self.root / "foreign-auth"
        foreign.mkdir()
        (run / ".ssh").symlink_to(foreign)
        result, log = self.run_to_finish()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("runtime path rejected: symlink", log.read_text())
        self.assertNotIn("dropbear -F", log.read_text())

    def test_zero_usb_candidates_rejected(self) -> None:
        class_link, _ = self.interface_links.pop("ownerusb0")
        class_link.unlink()
        result, log = self.run_to_finish()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no renamed USB candidate", log.read_text())
        self.assertNotIn("ip addr add", log.read_text())

    def test_unrelated_usb_candidate_is_not_claimed(self) -> None:
        self.make_interface("eth1", "asix", slot=2)
        process, log, _ = self.start_runtime()
        self.stop_runtime(process)
        self.assertNotIn("ip addr add 10.42.0.1/24 dev eth1", log.read_text())

    def test_non_usb_candidate_rejected(self) -> None:
        self.make_non_usb_interface()
        result, log = self.run_to_finish()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no renamed USB candidate", log.read_text())
        self.assertNotIn("ip addr add", log.read_text())

    def test_usb0_and_enx_names_rejected(self) -> None:
        for index, name in enumerate(("usb0", "enx001122334455"), start=2):
            with self.subTest(name=name):
                current = "ownerusb0" if index == 2 else "usb0"
                self.replace_interface_name(current, name, slot=index)
                result, log = self.run_to_finish()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("no renamed USB candidate", log.read_text())
                self.assertNotIn("ip addr add", log.read_text())

    def test_unallowlisted_driver_rejected(self) -> None:
        self.replace_driver("ownerusb0", "ax88179_178a")
        result, log = self.run_to_finish()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside the allowlist", log.read_text())
        self.assertNotIn("ip addr add", log.read_text())

    def test_unproven_radxa_ecm_is_excluded(self) -> None:
        """The final default candidate excludes the unproven Radxa ECM path."""
        _, interface = self.interface_links["ownerusb0"]
        self.replace_driver("ownerusb0", "cdc_ether")
        (interface.parent / "idVendor").write_text("1d6b\n")
        (interface.parent / "idProduct").write_text("0104\n")
        result, log = self.run_to_finish()
        self.assertNotEqual(result.returncode, 0)
        commands = log.read_text()
        self.assertNotIn("ip addr add", commands)
        self.assertIn("outside the allowlist", commands)
        source = (self.output / "opt/ioniq-owner/start-owner-ssh").read_text()
        self.assertNotIn("1d6b:0104:cdc_ether", source)
        self.assertNotIn("1d6b:0104", self.manifest["usb_ids"])

    def test_password_hash_enables_fallback_without_exposing_plaintext(self) -> None:
        hashed = self.root / "password.hash"
        hashed.write_bytes(b"$6$fixture$" + b"A" * 86 + b"\n")
        output = self.root / "with-password"
        manifest = MODULE.ioniq5_owner_ssh_generate(
            dropbear=self.binary, public_key=self.public, host_key=self.host,
            output=output, password_hash=hashed,
        )
        self.assertEqual(manifest["authentication"], ["publickey", "password"])
        self.assertEqual((output / "opt/ioniq-owner/keys/owner_password_hash").read_bytes(), hashed.read_bytes())
        source = (output / "opt/ioniq-owner/start-owner-ssh").read_text()
        self.assertIn("printf 'root:%s:0:0:Owner:/run/ioniq-owner:/bin/sh", source)
        invocation = source.split('"$base/bin/dropbear"', 1)[1].split('ssh_pid=', 1)[0]
        self.assertNotIn(' -s ', invocation)
        self.assertNotIn(hashed.read_text().strip(), source)

    def test_blank_plaintext_or_malformed_password_hash_rejected(self) -> None:
        hashed = self.root / "password.hash"
        for value in (b"", b"secret\n", b"*\n", b"$6$salt$short\n",
                      b"$6$fixture$" + b"A" * 86 + b"\nroot::0:0::/:/bin/sh\n"):
            with self.subTest(value=value[:12]):
                hashed.write_bytes(value)
                with self.assertRaises(ValueError):
                    MODULE.ioniq5_owner_ssh_generate(
                        dropbear=self.binary, public_key=self.public, host_key=self.host,
                        output=self.root / "bad-password", password_hash=hashed,
                    )
        self.assertFalse((self.root / "bad-password").exists())

    def test_authentication_failure_does_not_remove_the_ethernet_transport(self) -> None:
        """The browser console retains a link even when the SSH unit cannot start."""
        output = self.root / "independent"
        manifest = MODULE.ioniq5_owner_ssh_generate(
            dropbear=self.binary, public_key=self.public, host_key=self.host,
            output=output, independent_access=True, web_console=True,
        )
        network = output / "opt/ioniq-owner/start-owner-ethernet"
        auth = output / "opt/ioniq-owner/start-owner-ssh"
        auth_source = auth.read_text()
        self.assertIn('mount --bind "$run/passwd" /etc/passwd', auth_source)
        self.assertNotIn("ip addr", auth_source)
        self.assertNotIn("iptables", auth_source)
        self.assertNotIn("authorized_keys", network.read_text())
        self.assertIn("--dport 8443", network.read_text())
        self.assertIn("--sport 8443", network.read_text())
        for script in (network, auth):
            result = subprocess.run(["/bin/sh", "-n", str(script)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        for name in ("ioniq-owner-auth.service", "ioniq-owner-ethernet.service"):
            self.assertIn(f"etc/systemd/system/{name}", manifest["files"])
        self.assertNotIn("etc/systemd/system/ioniq-owner-ssh.service", manifest["files"])
        self.assertIn("ioniq-owner-ethernet.service", (output / MODULE._RULE_FILE).read_text())
        # Reuse the sysfs/firewall fixture while replacing only its entrypoint.
        auth.write_bytes(network.read_bytes())
        self.output = output
        script, log, stub_bin = self.runtime_script()
        systemctl = stub_bin / "systemctl"
        systemctl.write_text('#!/bin/sh\nprintf "systemctl %s\\n" "$*" >>"$OWNER_STUB_LOG"\nexit 1\n')
        systemctl.chmod(0o755)
        process = subprocess.Popen(["/bin/sh", str(script)], env=os.environ | {
            "OWNER_STUB_LOG": str(log), "OWNER_SYSROOT": str(self.sysroot)})
        self.addCleanup(self.stop_runtime, process)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and "remains ready" not in log.read_text():
            if process.poll() is not None:
                self.fail(log.read_text())
            time.sleep(0.02)
        before = log.read_text()
        self.assertIn("remains ready", before)
        self.assertIn("ioniq-owner-auth.service ioniq-owner-web.service", before)
        self.assertIsNone(process.poll())
        self.assertNotIn("ip addr del", before)
        self.stop_runtime(process)
        self.assertIn("ip addr del", log.read_text())

    def test_generated_standalone_auth_service_starts_with_clean_environment(self) -> None:
        """Exercise the exact split script, including its module-owned interface."""
        output = self.root / "standalone-auth"
        MODULE.ioniq5_owner_ssh_generate(
            dropbear=self.binary, public_key=self.public, host_key=self.host,
            output=output, independent_access=True, web_console=True,
        )
        self.output = output
        script, log, _ = self.runtime_script()
        environment = {name: os.environ[name] for name in ("PATH", "TMPDIR") if name in os.environ}
        environment.update(OWNER_STUB_LOG=str(log), OWNER_SYSROOT=str(self.sysroot))
        process = subprocess.Popen(["/bin/sh", str(script)], env=environment)
        self.addCleanup(self.stop_runtime, process)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            observed = log.read_text()
            if "dropbear -F -m -l ownerusb0 -p 10.42.0.1:22" in observed:
                break
            if process.poll() is not None:
                self.fail(observed)
            time.sleep(0.02)
        else:
            self.fail("Standalone authentication service did not launch Dropbear")
        self.assertIsNone(process.poll())
        self.assertNotIn("ip addr", observed)
        self.assertNotIn("iptables", observed)
        self.stop_runtime(process)

    def test_smsc_setup_guard_rejects_activation(self) -> None:
        self.replace_driver("ownerusb0", "smsc95xx")
        (self.owner_home / "ip_setup.sh").write_text("#!/bin/sh\nexit 0\n")
        result, log = self.run_to_finish()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside the allowlist", log.read_text())
        self.assertNotIn("ip addr add", log.read_text())

    def test_address_or_route_conflict_rejected(self) -> None:
        for variable, message in (
            ("OWNER_ADDRESS_CONFLICT", "already has an IPv4 address"),
            ("OWNER_ROUTE_CONFLICT", "subnet conflicts"),
        ):
            with self.subTest(variable=variable):
                result, log = self.run_to_finish(environment={variable: "1"})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, log.read_text())
                self.assertNotIn("ip addr add", log.read_text())

    def test_name_reuse_never_removes_replacement_address(self) -> None:
        process, log, _ = self.start_runtime(
            environment={"OWNER_MUTATE_IFINDEX": "999"},
        )
        self.stop_runtime(process)
        commands = log.read_text()
        self.assertIn("ip addr add 10.42.0.1/24 dev ownerusb0", commands)
        self.assertNotIn("ip addr del 10.42.0.1/24 dev ownerusb0", commands)
        self.assertEqual(commands.count("ip link set ownerusb0 down"), 1)

    def test_existing_connman_config_is_preserved(self) -> None:
        second_output = self.root / "merged-overlay"
        existing = self.root / "existing-main.conf"
        existing.write_text(
            "[General]\n"
            "NetworkInterfaceBlacklist=acme0\n"
            "OtherOption=keep-me\n"
        )
        MODULE.ioniq5_owner_ssh_generate(
            dropbear=self.binary,
            public_key=self.public,
            host_key=self.host,
            connman_config=existing,
            output=second_output,
        )
        parser = configparser.ConfigParser(interpolation=None)
        parser.read_string((second_output / "etc/connman/main.conf").read_text())
        values = set(parser["General"]["NetworkInterfaceBlacklist"].split(","))
        self.assertIn("acme0", values)
        self.assertTrue({"ownerusb0"} <= values)
        self.assertEqual(parser["General"]["OtherOption"], "keep-me")

    def test_usb_ids_and_fixed_network_inputs_are_validated(self) -> None:
        """Only the exact alias-backed IDs and fixed interface/address are accepted."""
        arguments = dict(dropbear=self.binary, public_key=self.public, host_key=self.host)
        for index, override in enumerate((
            {"usb_ids": ()}, {"usb_ids": "0bda:8153"}, {"usb_ids": 1},
            {"usb_ids": ("0b95:1790",)}, {"usb_ids": ("0424:9e00",)},
            {"usb_ids": ("*:*",)}, {"usb_ids": ("0bda:8153\nRUN+=bad",)},
            {"interface": "eth0"}, {"interface": "ownerusb0;id"},
            {"address": "::1/64"}, {"address": "10.42.0.1/24\nid"},
        )):
            output = self.root / f"invalid-{index}"
            with self.subTest(override=override), self.assertRaises(ValueError):
                MODULE.ioniq5_owner_ssh_generate(**arguments, output=output, **override)
            self.assertFalse(output.exists())
            self.assertFalse(output.with_name(output.name + ".manifest.json").exists())
        output = self.root / "one-id"
        manifest = MODULE.ioniq5_owner_ssh_generate(
            **arguments, output=output, usb_ids=("0BDA:8153", "0bda:8153"))
        self.assertEqual(manifest["usb_ids"], ["0bda:8153"])
        rules = (output / MODULE._RULE_FILE).read_text()
        self.assertEqual(rules.count('ACTION=="add"'), 1)
        self.assertIn('ATTRS{idVendor}=="0bda", ATTRS{idProduct}=="8153"', rules)
        self.assertIn('NAME="ownerusb0", TAG+="systemd"', rules)
        self.assertNotIn(":=", rules)
        self.assertEqual((output / "etc/modules-load.d/ioniq-owner-usb.conf").read_text(), "r8152\n")
        cdc_output = self.root / "cdc-id"
        with self.assertRaises(ValueError):
            MODULE.ioniq5_owner_ssh_generate(
                **arguments, output=cdc_output, usb_ids=("1d6b:0104",))

    def test_manifest_modes_and_builder_compatible_links(self) -> None:
        """Target ownership is explicit; host staging modes protect credentials."""
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        self.assertEqual((self.output / "opt/ioniq-owner/keys").stat().st_mode & 0o777, 0o700)
        for name, entry in self.manifest["files"].items():
            path = self.output / name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"])
            self.assertEqual(path.stat().st_mode & 0o777, int(entry["mode"], 8))
            self.assertEqual((entry["uid"], entry["gid"]), (0, 0))
        for name, target in self.manifest["symlinks"].items():
            self.assertFalse(Path(target).is_absolute())
            self.assertNotIn("..", Path(target).parts)
            self.assertEqual(os.readlink(self.output / name), target)
        self.assertEqual(len(self.manifest["symlinks"]), 3)
        self.assertEqual((self.output / "usr/bin/scp").read_text(),
                         '#!/bin/sh\nexec /opt/ioniq-owner/bin/dropbearmulti scp "$@"\n')
        second = self.root / "second"
        self.assertEqual(MODULE.ioniq5_owner_ssh_generate(
            dropbear=self.binary, public_key=self.public, host_key=self.host, output=second), self.manifest)

    def test_unreviewed_binary_and_inconsistent_host_key_are_rejected(self) -> None:
        """Banners cannot admit different build flags or a mismatched host seed."""
        arguments = dict(dropbear=self.binary, public_key=self.public, host_key=self.host)
        with mock.patch.object(MODULE, "_PINNED_BINARY_SHA256", self.original_digest):
            with self.assertRaisesRegex(ValueError, "digest"):
                MODULE.ioniq5_owner_ssh_generate(**arguments, output=self.root / "bad-binary")
        self.host.write_bytes(ssh_string(b"ssh-ed25519") + ssh_string(bytes(range(64))))
        with self.assertRaisesRegex(ValueError, "public half"):
            MODULE.ioniq5_owner_ssh_generate(**arguments, output=self.root / "bad-host")

    def test_output_failures_preserve_foreign_files_and_rollback(self) -> None:
        """No failed write publishes an incomplete pair or removes foreign bytes."""
        arguments = dict(dropbear=self.binary, public_key=self.public, host_key=self.host)
        foreign = self.output / "sentinel"
        foreign.write_text("keep")
        with self.assertRaises(ValueError):
            MODULE.ioniq5_owner_ssh_generate(**arguments, output=self.output)
        self.assertEqual(foreign.read_text(), "keep")
        output = self.root / "failed"
        real_write = Path.write_bytes
        def fail_config(path, value):
            if path.name == "main.conf":
                raise OSError("simulated disk failure")
            return real_write(path, value)
        with mock.patch.object(Path, "write_bytes", fail_config), self.assertRaises(OSError):
            MODULE.ioniq5_owner_ssh_generate(**arguments, output=output)
        self.assertFalse(output.exists())
        self.assertFalse(output.with_name(output.name + ".manifest.json").exists())
        self.assertEqual(list(self.root.glob(".ioniq-owner-*")), [])
        with mock.patch.object(Path, "rename", side_effect=OSError("rename failure")), self.assertRaises(OSError):
            MODULE.ioniq5_owner_ssh_generate(**arguments, output=output)
        self.assertFalse(output.exists())
        self.assertFalse(output.with_name(output.name + ".manifest.json").exists())
        self.assertEqual(list(self.root.glob(".ioniq-owner-*")), [])

    def test_target_cli_exposes_repeatable_usb_id(self) -> None:
        """CLI accepts exact repeated IDs without a network credential argument."""
        output = self.root / "cli"
        argv = ["--dropbear", str(self.binary), "--public-key", str(self.public),
                "--host-key", str(self.host), "--usb-id", "0bda:8153", "--usb-id", "0b95:772a",
                "--output", str(output)]
        with mock.patch("builtins.print"):
            self.assertEqual(MODULE.ioniq5_owner_ssh_main(argv), 0)
        manifest = json.loads(output.with_name(output.name + ".manifest.json").read_text())
        self.assertEqual(manifest["usb_ids"], ["0b95:772a", "0bda:8153"])

    def test_failure_cleanup_and_firewall_collision_preserves_foreign_state(self) -> None:
        """Failures before/after mutation exercise the ownership-safe unwind."""
        for variable in ("OWNER_CHILD_FAIL", "OWNER_FIREWALL_FAIL", "OWNER_FIREWALL_COLLISION", "OWNER_IP_PROBE_FAIL"):
            with self.subTest(variable=variable):
                result, log = self.run_to_finish(environment={variable: "1"})
                self.assertNotEqual(result.returncode, 0)
                commands = log.read_text()
                if variable in ("OWNER_FIREWALL_COLLISION", "OWNER_IP_PROBE_FAIL"):
                    self.assertNotIn("ip link set", commands)
                    self.assertNotIn(" -X IONIQ5_OWNER_", commands)
                elif variable == "OWNER_FIREWALL_FAIL":
                    self.assertIn("iptables -X IONIQ5_OWNER_INPUT", commands)
                    self.assertNotIn("iptables -X IONIQ5_OWNER_OUTPUT", commands)
                    self.assertNotIn("dropbear -F", commands)
                else:
                    self.assertIn("ip addr del 10.42.0.1/24 dev ownerusb0", commands)
                    self.assertIn("ip6tables -X IONIQ5_OWNER_FORWARD", commands)

    def test_unplug_exits_cleanly_without_touching_replacement_name(self) -> None:
        """Removing USB closes the daemon and removes owned firewall rules."""
        process, log, _ = self.start_runtime()
        self.interface_links["ownerusb0"][0].unlink()
        process.wait(timeout=5)
        self.assertEqual(process.returncode, 0)
        commands = log.read_text()
        self.assertIn("Owner USB removed", commands)
        self.assertNotIn("ip addr del", commands)
        self.assertIn("iptables -D INPUT -j IONIQ5_OWNER_INPUT", commands)

    def test_unlisted_usb_identity_is_rejected_before_network_changes(self) -> None:
        """A supported driver alone cannot admit a different USB product."""
        _, interface = self.interface_links["ownerusb0"]
        (interface.parent / "idProduct").write_text("ffff\n")
        result, log = self.run_to_finish()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Owner USB identity rejected", log.read_text())
        self.assertNotIn("ip link set", log.read_text())


class RetainedTargetEvidenceTests(unittest.TestCase):
    """Check exact retained target evidence without executing target programs."""

    def test_exact_build_authentication_and_option_contract(self) -> None:
        build = REPOSITORY / "work/dropbear-build-2026.94-access"
        parser_source = REPOSITORY / "work/dropbear-2026.94/src/svr-runopts.c"
        if not (build / "dropbearmulti").is_file() or not parser_source.is_file():
            self.skipTest("retained private build evidence unavailable")
        MODULE._validate_binary((build / "dropbearmulti").read_bytes())
        self.assertIn("#define DISABLE_SYSLOG 1", (build / "config.h").read_text())
        local = (build / "localoptions.h").read_text()
        for name in ("DROPBEAR_SVR_PAM_AUTH", "DROPBEAR_SVR_LOCALTCPFWD",
                     "DROPBEAR_SVR_REMOTETCPFWD", "DROPBEAR_SVR_LOCALSTREAMFWD", "DROPBEAR_SVR_REMOTESTREAMFWD",
                     "DROPBEAR_SVR_AGENTFWD", "DROPBEAR_X11FWD"):
            self.assertIn(f"#define {name} 0", local)
        self.assertIn("#define DROPBEAR_SVR_PUBKEY_AUTH 1", local)
        self.assertIn("#define DROPBEAR_SVR_PASSWORD_AUTH 1", local)
        parser = parser_source.read_text()
        self.assertIn("#ifndef DISABLE_SYSLOG\n\t\t\t\tcase 'E':", parser)
        for option in "FmlpDrP":
            self.assertIn(f"case '{option}':", parser)
        invocation = MODULE._STARTUP.split('"$base/bin/dropbear"', 1)[1].split('ssh_pid=', 1)[0]
        for option in (" -E ", " -x ", " -X "):
            self.assertNotIn(option, invocation)

    def test_module_aliases_and_dependencies_exist(self) -> None:
        rootfs = REPOSITORY / "work/decrypted-eu-260128/extracted-safe/mango-rootfs"
        modules = rootfs / "lib/modules/4.1.27-abl"
        if not (modules / "modules.alias").is_file():
            self.skipTest("retained private rootfs unavailable")
        aliases = (modules / "modules.alias").read_text()
        dependencies = (modules / "modules.dep").read_text()
        for value in MODULE.ioniq5_owner_ssh_usb_ids():
            vendor, product = value.upper().split(":")
            if MODULE._USB_DRIVERS[value] == "cdc_ether":
                self.assertIn("alias usb:v*p*d*dc*dsc*dp*ic02isc06ip00in* cdc_ether",
                              aliases)
            else:
                self.assertIn(f"usb:v{vendor}p{product}", aliases)
        for line in dependencies.splitlines():
            if line.startswith((
                "kernel/drivers/net/cdc_ether.ko:",
                "kernel/drivers/net/usb/asix.ko:",
                "kernel/drivers/net/usb/r8152.ko:",
            )):
                for name in line.replace(":", "").split():
                    self.assertTrue((modules / name).is_file(), name)
        self.assertTrue((rootfs / "etc/shells").is_symlink())
        self.assertIn("touch /tmp/shells", (rootfs / "lib/systemd/esinit").read_text())
        config = (REPOSITORY / "work/eu-260128/kernel.config").read_text()
        for required in ("CONFIG_NF_CONNTRACK=y", "CONFIG_NETFILTER_XT_MATCH_CONNTRACK=y",
                         "CONFIG_IP_NF_FILTER=y", "CONFIG_IP6_NF_FILTER=y"):
            self.assertIn(required, config)


if __name__ == "__main__":
    unittest.main()
