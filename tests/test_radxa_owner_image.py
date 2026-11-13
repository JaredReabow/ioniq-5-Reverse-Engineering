#!/usr/bin/env python3
"""Regression tests for the Radxa owner-image first-boot policy."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
INNER = REPO / "work/radxa-os/customize-owner-image-inner.sh"
BUILDER = REPO / "work/radxa-os/build-owner-image.sh"


FIRST_BOOT_FIXTURE = """\
log "Running before.txt as first boot configuration"
disable_service ssh
disable_service ssh.socket
regenerate_ssh_hostkey
if headless enable_service ssh
remove_packages rsetup-config-first-boot
"""


def _extract_patch_function() -> str:
    """Extract the exact shell function used by the image build."""
    source = INNER.read_text(encoding="utf-8")
    begin = "# BEGIN RADXA_OWNER_FIRST_BOOT_PATCH\n"
    end = "# END RADXA_OWNER_FIRST_BOOT_PATCH\n"
    if source.count(begin) != 1 or source.count(end) != 1:
        raise AssertionError("first-boot patch markers are not unique")
    return source.split(begin, 1)[1].split(end, 1)[0]


def _run_patch(contents: str) -> tuple[subprocess.CompletedProcess[str], str]:
    """Execute the production patch function against one fixture file."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        config = root / "before.txt"
        config.write_text(contents, encoding="utf-8")
        helper = root / "patch.sh"
        helper.write_text(
            "#!/bin/bash\nset -euo pipefail\n"
            + _extract_patch_function()
            + '\nradxa_owner_patch_first_boot_config "$1"\n',
            encoding="utf-8",
        )
        result = subprocess.run(
            ["bash", str(helper), str(config)],
            check=False,
            capture_output=True,
            text=True,
        )
        return result, config.read_text(encoding="utf-8")


def _ssh_service_active(contents: str, *, headless: bool) -> bool:
    """Evaluate only the SSH-related rsetup operations in file order."""
    active = False
    for raw in contents.splitlines():
        line = raw.strip()
        if line == "disable_service ssh":
            active = False
        elif line == "enable_service ssh":
            active = True
        elif line == "if headless enable_service ssh" and headless:
            active = True
    return active


class RadxaOwnerImageTests(unittest.TestCase):
    """Pin the first-boot and systemd safety rules in the image recipe."""

    def test_patch_enables_ssh_with_or_without_hdmi(self) -> None:
        result, patched = _run_patch(FIRST_BOOT_FIXTURE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(patched.count("disable_service ssh\n"), 1)
        self.assertIn("disable_service ssh.socket", patched)
        self.assertNotIn("if headless enable_service ssh", patched)
        self.assertLess(
            patched.index("disable_service ssh"),
            patched.index("regenerate_ssh_hostkey"),
        )
        self.assertLess(
            patched.index("regenerate_ssh_hostkey"),
            patched.index("enable_service ssh"),
        )
        for headless in (False, True):
            with self.subTest(headless=headless):
                self.assertTrue(_ssh_service_active(patched, headless=headless))

    def test_patch_refuses_unknown_vendor_recipe_without_mutation(self) -> None:
        changed = FIRST_BOOT_FIXTURE.replace("disable_service ssh\n", "", 1)
        result, after = _run_patch(changed)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unexpected Radxa SSH first-boot recipe", result.stderr)
        self.assertEqual(after, changed)

    def test_update_service_is_supervised_manual_and_preset_disabled(self) -> None:
        source = INNER.read_text(encoding="utf-8")
        wrapper = (REPO / "tools/uk_fw/radxa_update_media.sh").read_text(encoding="utf-8")
        self.assertIn(
            "ConditionPathExists=/opt/ioniq5-update/config/serve-plan.json",
            source,
        )
        self.assertIn(
            "ConditionPathExists=/run/ioniq5-update/manual-arm",
            source,
        )
        self.assertIn("Type=notify", source)
        self.assertIn("NotifyAccess=main", source)
        self.assertIn("ExecStart=/usr/local/sbin/ioniq-update-media internal-arm", source)
        self.assertIn("KillMode=mixed", source)
        self.assertIn("Restart=no", source)
        self.assertIn("TimeoutStartSec=infinity", source)
        self.assertNotIn("ExecStop=/usr/local/sbin/ioniq-update-media teardown", source)
        self.assertIn("install -m 0755 /workspace/tools/uk_fw/radxa_update_media.sh", source)
        self.assertIn('systemctl reset-failed "$service" 2>/dev/null || true', wrapper)
        self.assertIn('python3 "$tool" arm --serve-plan "$plan" --execute --hold', wrapper)
        self.assertIn('systemctl stop "$service"', wrapper)
        self.assertNotIn('if systemctl is-active --quiet "$service"; then\n            systemctl stop', wrapper)
        self.assertIn('exec python3 "$tool" status', wrapper)
        self.assertIn('--validation-cache "$cache"', wrapper)
        self.assertIn("enable ssh.service", source)
        self.assertIn("disable ioniq-update-media.service", source)
        self.assertIn('"$rootfs/etc/ioniq5-update/allow-auto-arm"', source)

    def test_image_version_is_bumped_and_console_printed(self) -> None:
        inner = INNER.read_text(encoding="utf-8")
        outer = BUILDER.read_text(encoding="utf-8")
        self.assertIn("owner_image_version=1.1.1", inner)
        self.assertIn("/etc/issue.d/ioniq-owner.issue", inner)
        self.assertIn("radxa-zero3-owner-update-v1.1.1.img", outer)

    def test_recreation_keeps_selected_owner_firmware_and_prebuilt_helper(self) -> None:
        """Recreating media cannot silently restore the superseded v2 firmware."""
        inner = INNER.read_text(encoding='utf-8')
        outer = BUILDER.read_text(encoding='utf-8')
        self.assertNotIn('owner_usb_ssh_v2_260128', inner + outer)
        self.assertIn('owner_access_v4.0.2_260128.te2', inner)
        self.assertIn('owner_access_v4.0.2_260128.te2', outer)
        self.assertIn('94323aa3d05b4cf2e1a894ca445f4bf8a85f9341c0a879d2cdbbc338304123c6', inner)
        self.assertIn('build-nbdfuse-direct.sh', inner)
        self.assertLess(inner.index('chroot "$rootfs" /bin/bash /opt/ioniq5-update/tools/uk_fw/build-nbdfuse-direct.sh'),
                        inner.index('rm -f "$rootfs/etc/resolv.conf"\ncase "$resolv_kind"'))
        self.assertIn('/usr/local/libexec/ioniq-nbdfuse-direct', inner)

    def test_builder_pins_the_controller_installed_in_the_image(self) -> None:
        """The image recipe must fail if the reviewed Radxa tool changes."""
        builder = BUILDER.read_text(encoding="utf-8")
        match = re.search(r"^expected_radxa_usb=([0-9a-f]{64})$", builder, re.M)
        self.assertIsNotNone(match)
        actual = hashlib.sha256(
            (REPO / "tools/uk_fw/radxa_usb.py").read_bytes()
        ).hexdigest()
        self.assertEqual(match.group(1), actual)

    def test_builder_supports_a_secret_dedicated_psk_descriptor(self) -> None:
        """Automated builds can supply the PSK without an argv or log secret."""
        source = BUILDER.read_text(encoding="utf-8")
        self.assertIn("RADXA_OWNER_WIFI_PSK_FD", source)
        self.assertIn('read -r -s wifi_psk <&"$wifi_psk_fd"', source)
        self.assertIn('unset wifi_psk_fd RADXA_OWNER_WIFI_PSK_FD', source)
        self.assertNotRegex(source, r"(?m)^\s*(?:psk|wifi_psk)=[\"'][^$\"']{8,63}[\"']")


if __name__ == "__main__":
    unittest.main()
