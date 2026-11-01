from __future__ import annotations
import importlib.util,json,stat,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TOOL=ROOT/"tools/uk_fw/eu260128_boot_container_matrix.py";INPUT=ROOT/"work/appfumo-iasimage-eu260128/encrypted";REPORT=ROOT/"evidence/artifacts/update-candidates/eu260128-boot-container-matrix.json"
s=importlib.util.spec_from_file_location("eu260128_boot_container_matrix",TOOL);assert s and s.loader;m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_filename_contract(self):self.assertEqual(len(m.FILES),12);self.assertEqual(sum(v[3] for v in m.FILES.values()),6)
 def test_deterministic_utf8(self):
  b=m.encode({"z":"ipk.","a":None});self.assertEqual(b,m.encode({"z":"ipk.","a":None}));self.assertTrue(b.endswith(b"\n"));self.assertNotIn(b"\r",b);json.loads(b)
 def test_exclusive_output(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"r";m.write_exclusive(p,b"{}\n");self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
   with self.assertRaises(m.Failure):m.write_exclusive(p,b"{}\n")
 def test_te2_integrity_mutation_rejected(self):
  raw=b"x"*32+b"TE2\x01"+b"\0"*(m.META-4)
  with self.assertRaisesRegex(m.Failure,"metadata integrity"):m.decrypt_te2("iasImage",raw)
 @unittest.skipUnless(INPUT.is_dir(),"ignored package inputs unavailable")
 def test_exact_matrix(self):
  r=m.analyze(INPUT);self.assertEqual(r["package"]["filenames"],12);self.assertEqual(r["package"]["te2_wrapped"],6)
  self.assertTrue(r["conclusions"]["all_embedded_signatures_verify"]);self.assertTrue(r["conclusions"]["all_twelve_decompress_to_recovered_vmlinux"])
  self.assertIsNone(r["conclusions"]["bootloader_pins_embedded_modulus"]);self.assertFalse(r["conclusions"]["custom_image_acceptance_proved"])
 @unittest.skipUnless(INPUT.is_dir(),"ignored package inputs unavailable")
 def test_root_and_console_matrix(self):
  rows={x["name"]:x for x in m.analyze(INPUT)["rows"]}
  self.assertEqual(rows["iasImage_1920_12"]["ipk"]["root_target"],"/dev/mmcblk0p3")
  self.assertEqual(rows["iasImage_1920_12_sub"]["ipk"]["root_target"],"/dev/mmcblk0p5")
  self.assertFalse(rows["iasImage_p5_1280"]["ipk"]["serial_console"]);self.assertTrue(rows["iasImage_p5_1280_sub"]["ipk"]["serial_console"])
 @unittest.skipUnless(INPUT.is_dir() and REPORT.is_file(),"exact artifacts unavailable")
 def test_report_reproduces_path_privately(self):
  b=m.encode(m.analyze(INPUT));self.assertEqual(b,REPORT.read_bytes());self.assertNotIn(str(INPUT).encode(),b)
 def test_unexpected_directory_shape_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/"unexpected").write_bytes(b"x")
   with self.assertRaisesRegex(m.Failure,"filename set mismatch"):m.analyze(p)
if __name__=="__main__":unittest.main()
