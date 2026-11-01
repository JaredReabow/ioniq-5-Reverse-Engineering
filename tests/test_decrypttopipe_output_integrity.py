from __future__ import annotations
import importlib.util,json,stat,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TOOL=ROOT/"tools/uk_fw/decrypttopipe_output_integrity.py";ROOTFS=ROOT/"work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz";APP=ROOT/"work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf";BOOT=ROOT/"work/appfumo-iasimage-eu260128/encrypted";REPORT=ROOT/"evidence/artifacts/update-candidates/decrypttopipe-output-integrity.json"
s=importlib.util.spec_from_file_location("decrypttopipe_output_integrity",TOOL);assert s and s.loader;m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_canonical_name(self):self.assertEqual(m.canon("./app/share/AppUpgrade/DecryptToPIPE"),m.MEMBER);self.assertEqual(m.canon(m.MEMBER),m.MEMBER)
 def test_unsafe_names_rejected(self):
  for n in ["/app/share/AppUpgrade/DecryptToPIPE","./app/./share/AppUpgrade/DecryptToPIPE","./app/../share/AppUpgrade/DecryptToPIPE","./app//share/AppUpgrade/DecryptToPIPE","."]:
   with self.subTest(n=n),self.assertRaises(m.Failure):m.canon(n)
 def test_deterministic_utf8(self):
  b=m.encode({"z":"TE2","a":None});self.assertEqual(b,m.encode({"z":"TE2","a":None}));self.assertTrue(b.endswith(b"\n"));self.assertNotIn(b"\r",b);json.loads(b)
 def test_exclusive_output(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"r";m.write_exclusive(p,b"{}\n");self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
   with self.assertRaises(m.Failure):m.write_exclusive(p,b"{}\n")
 def test_symlink_rootfs_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);target=p/"x";target.write_bytes(b"x");link=p/"l";link.symlink_to(target)
   with self.assertRaises(m.Failure):m.archive_member(link)
 @unittest.skipUnless(ROOTFS.is_file() and APP.is_file() and BOOT.is_dir() and REPORT.is_file(),"exact ignored inputs unavailable")
 def test_exact_report_reproduces(self):
  r=m.analyze(ROOTFS,APP,BOOT);b=m.encode(r);self.assertEqual(b,REPORT.read_bytes());self.assertNotIn(str(ROOTFS).encode(),b);self.assertNotIn(str(BOOT).encode(),b)
  self.assertEqual(sum(x["parser_classification"]=="te2_decrypt" for x in r["boot_sources"]),6);self.assertEqual(sum(x["parser_classification"]=="minus404_magic" for x in r["boot_sources"]),6)
  x=r["exact_static"];self.assertTrue(x["all_sub_images_select_minus404_fallback"]);self.assertEqual(x["main_exit_status_after_stream_call"],0);self.assertFalse(x["short_nonnegative_write_is_fully_accounted"])
  c=r["conclusions"];self.assertFalse(c["process_zero_exit_proves_complete_output"]);self.assertFalse(c["final_boot_partition_bytes_or_durability_proved"])
 @unittest.skipUnless(REPORT.is_file(),"tracked report unavailable")
 def test_report_call_inventory(self):
  r=json.loads(REPORT.read_text("utf-8"));calls=r["decrypttopipe"]["direct_calls"];self.assertEqual(calls["main_stream"]["target"],0x82D0);self.assertEqual(calls["stream_parse_envelope"]["target"],0x9080);self.assertEqual(calls["fallback_stdout_write"]["target"],0x7FD0)
 def test_wrong_boot_shape_rejected(self):
  if not ROOTFS.is_file() or not APP.is_file():self.skipTest("exact ignored binaries unavailable")
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(m.Failure,"filename set mismatch"):m.analyze(ROOTFS,APP,Path(d))
if __name__=="__main__":unittest.main()
