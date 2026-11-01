from __future__ import annotations
import importlib.util,json,stat,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TOOL=ROOT/"tools/uk_fw/appfumo_system_swap_completion.py";ELF=ROOT/"work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf";REPORT=ROOT/"evidence/artifacts/update-candidates/appfumo-system-swap-completion.json"
s=importlib.util.spec_from_file_location("appfumo_system_swap_completion",TOOL);assert s and s.loader;m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_helper_identity(self):self.assertEqual(m.BASE_HASH,"c0edbbe93df218192f315437132764549453e78f7a93fec350540637312a1e82")
 def test_deterministic_utf8(self):
  b=m.encode({"z":"complete","a":None});self.assertEqual(b,m.encode({"z":"complete","a":None}));self.assertTrue(b.endswith(b"\n"));self.assertNotIn(b"\r",b);json.loads(b)
 def test_exclusive_output(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"r";m.write_exclusive(p,b"x\n");self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
   with self.assertRaises(m.Failure):m.write_exclusive(p,b"x\n")
 @unittest.skipUnless(ELF.is_file(),"exact ignored ELF unavailable")
 def test_exact_flow(self):
  r=m.analyze(ELF);x=r["exact_static"];c=r["conclusions"]
  self.assertTrue(x["swap_result_flow"]["swap_false_returns_to_current_latch_log"]);self.assertFalse(x["swap_result_flow"]["swap_false_aborts_handler"])
  self.assertFalse(x["downstream_flow"]["system_completed_marker_helper_requires_0x240"]);self.assertTrue(c["system_swap_latch_is_not_a_mandatory_gate_for_downstream_marker_handling"])
  self.assertFalse(c["completion_log_proves_successful_boot_partition_bytes"]);self.assertFalse(c["root_or_persistence_proved"])
 @unittest.skipUnless(ELF.is_file(),"exact ignored ELF unavailable")
 def test_call_inventory(self):
  x=m.analyze(ELF)["exact_static"];self.assertEqual(x["direct_calls"]["swap_system"]["target"],0x148E70);self.assertEqual(x["controller_fields"]["system_swap_complete_handler_offset"],0x240)
 @unittest.skipUnless(ELF.is_file() and REPORT.is_file(),"exact artifacts unavailable")
 def test_report_reproduces_without_path(self):
  b=m.encode(m.analyze(ELF));self.assertEqual(b,REPORT.read_bytes());self.assertNotIn(str(ELF).encode(),b)
 @unittest.skipUnless(ELF.is_file(),"exact ignored ELF unavailable")
 def test_mutation_rejected(self):
  raw=bytearray(ELF.read_bytes());raw[0x120044]^=1
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"m";p.write_bytes(raw)
   with self.assertRaises(m.Failure):m.analyze(p)
if __name__=="__main__":unittest.main()
