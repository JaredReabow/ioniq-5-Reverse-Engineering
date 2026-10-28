"""Offline tests for the VM harness; live boot checks are run separately."""
from __future__ import annotations

import importlib.util
import io
import struct
import unittest
from pathlib import Path

TOOL = Path(__file__).parents[1] / "tools/uk_fw/vm_boot.py"
SPEC = importlib.util.spec_from_file_location("vm_boot", TOOL)
VM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VM)


def container_fixture():
    raw = bytearray(0x4000 + 0x304)
    raw[:4] = b"ipk."
    struct.pack_into("<III", raw, 0x0c, 0x4000 - 0x34, 0x34, 0x4000 - 0x34)
    struct.pack_into("<I", raw, 0x1c, 953)
    start = 1008
    raw[start + 0x1f1] = 4
    raw[start + 0x1fe:start + 0x200] = b"\x55\xaa"
    raw[start + 0x202:start + 0x206] = b"HdrS"
    struct.pack_into("<H", raw, start + 0x206, 0x20d)
    return raw


class FakeRSP:
    def __init__(self, contents=VM.EXPECTED_ENTRY):
        self.contents = contents
        self.commands = []

    def request(self, command):
        self.commands.append(command)
        if command in ("?", "c"):
            return "T05thread:01;"
        if command.startswith("m"):
            return self.contents.hex()
        if command.startswith("M"):
            self.contents = bytes.fromhex(command.split(":")[1])
        return "OK"


class FakeSocket:
    def __init__(self, packet):
        self.packet = bytearray(packet)
        self.sent = []

    def recv(self, count):
        # Deliberately fragment two-byte checksum reads.
        out = bytes(self.packet[:1])
        del self.packet[:1]
        return out

    def sendall(self, data):
        self.sent.append(data)


class BootImageTests(unittest.TestCase):
    def test_extracts_validated_boot_image_without_trailer(self):
        raw = container_fixture()
        self.assertEqual(VM.extract_boot_image(bytes(raw)), raw[1008:0x4000])

    def test_rejects_non_ipk(self):
        with self.assertRaises(ValueError):
            VM.extract_boot_image(b"\x7fELF" + bytes(512))

    def test_rejects_truncated_container(self):
        with self.assertRaisesRegex(ValueError, "bounds"):
            VM.extract_boot_image(bytes(container_fixture()[:-1]))

    def test_rejects_mismatched_size_fields(self):
        raw = container_fixture()
        struct.pack_into("<I", raw, 0x14, 12)
        with self.assertRaisesRegex(ValueError, "bounds"):
            VM.extract_boot_image(bytes(raw))

    def test_rejects_missing_boot_flag(self):
        raw = container_fixture()
        raw[1008 + 0x1fe] = 0
        with self.assertRaisesRegex(ValueError, "got 0"):
            VM.extract_boot_image(bytes(raw))

    def test_rejects_ambiguous_boot_image(self):
        raw = container_fixture()
        raw[8192:8192 + 0x210] = raw[1008:1008 + 0x210]
        with self.assertRaisesRegex(ValueError, "got 2"):
            VM.extract_boot_image(bytes(raw))


class DriverPatchTests(unittest.TestCase):
    def test_table_address_and_layout(self):
        self.assertEqual(VM.TABLE_ENTRY, 0xffffffff8164c960 + 61 * 32)
        v, d, sv, sd, cl, mask, quirks = struct.unpack("<6IQ", VM.COMPAT_ENTRY)
        self.assertEqual((v, d, cl, mask, quirks), (0x1b36, 7, 0x80500, 0xffff00, 0))
        self.assertEqual((sv, sd), (0xffffffff, 0xffffffff))

    def test_checks_then_writes_then_reads_back(self):
        rsp = FakeRSP()
        result = VM.adapt_sdhci(rsp)
        writes = [c for c in rsp.commands if c.startswith("M")]
        self.assertEqual(len(writes), 1)
        self.assertEqual(rsp.contents, VM.COMPAT_ENTRY)
        self.assertEqual(rsp.commands[-1], "D")
        self.assertEqual(result["address"], hex(VM.TABLE_ENTRY))

    def test_wrong_build_does_not_get_patched(self):
        rsp = FakeRSP(bytes(32))
        with self.assertRaisesRegex(ValueError, "refusing"):
            VM.adapt_sdhci(rsp)
        self.assertFalse(any(c.startswith("M") for c in rsp.commands))
        self.assertNotIn("D", rsp.commands)

    def test_bad_readback_fails_closed(self):
        class BadReadback(FakeRSP):
            def request(self, command):
                result = super().request(command)
                if command.startswith("M"):
                    self.contents = bytes(32)
                return result
        with self.assertRaisesRegex(ValueError, "readback"):
            VM.adapt_sdhci(BadReadback())


class ProtocolTests(unittest.TestCase):
    def test_decode_repeat_and_escape(self):
        self.assertEqual(VM.decode_rsp(b"0* "), b"0000")
        self.assertEqual(VM.decode_rsp(b"a}\x03b"), b"a#b")
        self.assertEqual(VM.decode_rsp(b"A}\x0a"), b"A*")

    def test_invalid_encoding_rejected(self):
        for data in (b"* ", b"a}", b"a*", b"a*\x01"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                VM.decode_rsp(data)

    def test_packet_checksum_with_fragmented_socket(self):
        sock = FakeSocket(b"+$OK#9a")
        self.assertEqual(VM.RSP(sock).request("?"), "OK")
        self.assertEqual(sock.sent, [b"$?#3f", b"+"])

    def test_bad_packet_checksum_rejected(self):
        with self.assertRaisesRegex(ValueError, "checksum"):
            VM.RSP(FakeSocket(b"+$OK#00")).request("?")

    def test_closed_socket_does_not_spin(self):
        with self.assertRaises(EOFError):
            VM.RSP(FakeSocket(b"+$O")).request("?")


class CommandTests(unittest.TestCase):
    def test_no_initramfs_network_or_writable_base_image(self):
        cmd = VM.qemu_command(VM.PROJECT / "work/vm/example", "qemu", False)
        self.assertNotIn("-initrd", cmd)
        self.assertNotIn("-gdb", cmd)
        self.assertNotIn("-S", cmd)
        self.assertEqual(cmd[cmd.index("-nic") + 1], "none")
        self.assertIn("snapshot=on", cmd[cmd.index("-drive") + 1])
        self.assertIn("rootwait", cmd[cmd.index("-append") + 1])
        self.assertIn("init=/init", cmd[cmd.index("-append") + 1])

    def test_compat_debug_interface_is_local_and_explicit(self):
        cmd = VM.qemu_command(VM.PROJECT / "work/vm/example", "qemu", True)
        self.assertEqual(cmd[cmd.index("-gdb") + 1], "unix:gdb.sock,server=on,wait=off")
        self.assertIn("-S", cmd)

    def test_memory_is_explicit_and_bounded(self):
        cmd = VM.qemu_command(VM.PROJECT / "work/vm/example", "qemu", False,
                              memory_mib=3072)
        self.assertEqual(cmd[cmd.index("-m") + 1], "3072")
        for invalid in (255, 8193):
            with self.assertRaisesRegex(ValueError, "memory"):
                VM.qemu_command(VM.PROJECT / "work/vm/example", "qemu", False,
                                memory_mib=invalid)

    def test_micom_serial_is_project_local_and_has_no_network(self):
        cmd = VM.qemu_command(VM.PROJECT / "work/vm/example", "qemu", False,
                              micom_serial=True)
        self.assertIn("socket,id=micom,path=micom.sock,server=on,wait=off", cmd)
        self.assertIn("isa-serial,chardev=micom,index=1", cmd)
        self.assertEqual(cmd[cmd.index("-nic") + 1], "none")

    def test_micom_capture_drains_until_nonblocking_boundary(self):
        class SerialSocket:
            def __init__(self):
                self.chunks = [b"abc", b"def"]

            def recv(self, _count):
                if self.chunks:
                    return self.chunks.pop(0)
                raise BlockingIOError

        output = io.BytesIO()
        self.assertEqual(VM.drain_available(SerialSocket(), output), 6)
        self.assertEqual(output.getvalue(), b"abcdef")

    def test_ext4_features_are_an_allowlist(self):
        self.assertTrue(VM.EXT4_FEATURES.startswith("none,"))
        for feature in ("metadata_csum", "metadata_csum_seed", "orphan_file", "64bit"):
            self.assertNotIn(feature, VM.EXT4_FEATURES.split(","))

    def test_outputs_cannot_escape_project(self):
        with self.assertRaises(ValueError):
            VM.project_output(VM.PROJECT.parent / "other")
        with self.assertRaises(ValueError):
            VM.project_output(VM.PROJECT)
        with self.assertRaises(ValueError):
            VM.project_output(VM.PROJECT / "work/a,b")
        self.assertEqual(VM.project_output(VM.PROJECT / "work/vm/example"),
                         VM.PROJECT / "work/vm/example")


if __name__ == "__main__":
    unittest.main()
