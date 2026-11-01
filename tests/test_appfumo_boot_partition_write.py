from __future__ import annotations
import importlib.util
import json
import stat
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/"tools/uk_fw/appfumo_boot_partition_write.py"
ELF=ROOT/"work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf"
REPORT=ROOT/"evidence/artifacts/update-candidates/appfumo-boot-partition-write.json"
spec=importlib.util.spec_from_file_location("appfumo_boot_partition_write",TOOL)
assert spec and spec.loader
mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)

class Tests(unittest.TestCase):
    def test_malformed_elf_rejected(self):
        with self.assertRaises(mod.Failure): mod.parse_elf(b"\x7fELF"+b"\0"*100)
    def test_deterministic_utf8_lf(self):
        value={"z":"swapSystem","a":[None,False,1]}
        a=mod.encode(value);b=mod.encode(value)
        self.assertEqual(a,b);self.assertTrue(a.endswith(b"\n"));self.assertNotIn(b"\r",a)
        self.assertEqual(json.loads(a.decode("utf-8")),value)
    def test_exclusive_output(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"r.json";mod.write_exclusive(p,b"{}\n")
            self.assertEqual(p.read_bytes(),b"{}\n");self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
            with self.assertRaises(mod.Failure):mod.write_exclusive(p,b"{}\n")
    def test_symlink_input_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);target=root/"target";target.write_bytes(b"x");link=root/"link";link.symlink_to(target)
            with self.assertRaises(mod.Failure):mod.stable_read(link)
    @unittest.skipUnless(ELF.is_file(),"exact ignored ELF unavailable")
    def test_exact_contract(self):
        r=mod.analyze(ELF);x=r["exact_static"];c=r["conclusions"]
        self.assertEqual(r["artifact"]["sha256"],mod.EXPECTED_SHA256)
        self.assertEqual(x["common_tail"]["mode_zero_tail_result"],True)
        self.assertTrue(x["pipeline_contract"]["pclose_called"])
        self.assertFalse(x["pipeline_contract"]["pclose_status_checked"])
        self.assertFalse(x["mount_contract"]["exit_code_checked"])
        self.assertFalse(c["true_return_proves_mount_success"])
        self.assertFalse(c["true_return_proves_direct_copy_success"])
        self.assertFalse(c["true_return_proves_pipeline_exit_success"])
    @unittest.skipUnless(ELF.is_file(),"exact ignored ELF unavailable")
    def test_mutated_elf_rejected(self):
        raw=bytearray(ELF.read_bytes());raw[0x149585]^=1
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"mutated.elf";p.write_bytes(raw)
            with self.assertRaisesRegex(mod.Failure,"identity mismatch"):mod.analyze(p)
    @unittest.skipUnless(ELF.is_file() and REPORT.is_file(),"exact artifacts unavailable")
    def test_report_reproduces_with_bounded_claims(self):
        payload=mod.encode(mod.analyze(ELF));self.assertEqual(payload,REPORT.read_bytes())
        text=payload.decode("utf-8");self.assertNotIn(str(ELF),text)
        r=json.loads(text);c=r["conclusions"]
        self.assertTrue(c["caller_success_latch_can_follow_bounded_weak_true_return"])
        self.assertIsNone(c["persistent_boot_selector_changed"])
        self.assertFalse(c["root_or_persistence"])
    @unittest.skipUnless(ELF.is_file(),"exact ignored ELF unavailable")
    def test_call_and_latch_inventory(self):
        r=mod.analyze(ELF)["exact_static"]
        self.assertEqual(r["direct_calls"]["copy_normal_direct"]["target"],0x1413F0)
        self.assertEqual(r["direct_calls"]["copy_sub_direct"]["target"],0x1413F0)
        self.assertEqual(r["direct_calls"]["pipeline_pclose"]["target"],0x21FE0)
        self.assertEqual([x["latch_offset"] for x in r["caller_latches"]],[0x240,0x240])

if __name__=="__main__":unittest.main()
