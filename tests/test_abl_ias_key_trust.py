import hashlib,importlib.util,io,json,os,subprocess,sys,tarfile,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'tools/uk_fw/abl_ias_key_trust.py'
REPORT=ROOT/'evidence/artifacts/update-candidates/abl-ias-key-trust.json'
UPDATE=ROOT/'work/decrypted-eu-260128/HU/firmware/update.tar.gz'
ROOTFS=ROOT/'work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz'
BOOT=ROOT/'work/appfumo-iasimage-eu260128/encrypted'
SBL=ROOT/'work/online-slimbootloader-20261110'
IAS=ROOT/'work/online-intel-iasimage-20261110'
SPEC=importlib.util.spec_from_file_location('abltrust',TOOL);M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
class AblIasKeyTrustTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  missing=[str(x) for x in (UPDATE,ROOTFS,BOOT,SBL,IAS) if not x.exists()]
  if missing:raise unittest.SkipTest('private/public analysis inputs absent: '+', '.join(missing))
  p=subprocess.run([sys.executable,str(TOOL),'--update-archive',str(UPDATE),'--rootfs',str(ROOTFS),'--boot-dir',str(BOOT),'--sbl-repo',str(SBL),'--iasimage-repo',str(IAS)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,timeout=300)
  if p.returncode:raise AssertionError(p.stderr.decode())
  cls.raw=p.stdout;cls.r=json.loads(p.stdout)
 def test_report_is_frozen_and_deterministic(self):
  self.assertEqual(self.raw,REPORT.read_bytes());self.assertEqual(hashlib.sha256(self.raw).hexdigest(),'2e6096d14d54d06af4ddd2989e80de1558ff8de081b64e64306ada123658f3b7')
  self.assertEqual(self.raw,M.encode(self.r))
 def test_exact_target_conclusion_remains_bounded(self):
  c=self.r['conclusions'];self.assertIsNone(c['exact_target_abl_key_pin_proved']);self.assertFalse(c['exact_target_abl_accepts_arbitrary_embedded_key_proved']);self.assertFalse(c['custom_signed_image_acceptance_proved']);self.assertFalse(c['boot_acceptance_root_or_persistence_proved'])
 def test_public_source_semantics_are_separate(self):
  s=self.r['public_intel']['slim_bootloader'];self.assertTrue(s['embedded_key_digest_checked_first']);self.assertTrue(s['payload_signature_checked_after_key_digest']);self.assertEqual(s['component_type'],'COMP_TYPE_PUBKEY_OS (6)');self.assertEqual(s['commit'],M.SBL_COMMIT)
 def test_exact_flash_and_key_identities(self):
  self.assertEqual(self.r['exact_update']['abl']['sha256'],M.ABL_SHA);self.assertFalse(self.r['exact_update']['abl']['candidate_os_key_hash_present_verbatim']);self.assertEqual(self.r['package_key']['modulus_sha256'],M.MOD_HASH);self.assertEqual(self.r['package_key']['public_sbl_candidate_digest'],'437008c1b26fd821a7c7c0ec855aaba5587f62deaaa98d9b2fcbf6ad4179aa06')
 def test_unsafe_archive_spellings_fail_closed(self):
  for x in ('','/x','././x','a/./b','a/../b','a//b','a\\b'):
   with self.subTest(x=x),self.assertRaises(M.Failure):M.canon(x)
  self.assertIsNone(M.canon('.'));self.assertEqual(M.canon('./a/b'),'a/b')
 def test_archive_alias_link_and_ownership_drift_fail_closed(self):
  def check(entries):
   with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'a.tar.gz'
    with tarfile.open(p,'w:gz',format=tarfile.PAX_FORMAT) as t:
     for name,kind,uid in entries:
      x=tarfile.TarInfo(name);x.uid=uid;x.gid=0;x.mode=0o644;x.size=1 if kind=='file' else 0
      if kind=='symlink':x.type=tarfile.SYMTYPE;x.linkname='target';t.addfile(x)
      else:t.addfile(x,io.BytesIO(b'x'))
    b=p.read_bytes()
    with self.assertRaises(M.Failure):M.archive_one(p,len(b),hashlib.sha256(b).hexdigest(),'x',1,0o644,0,0)
  check([('x','file',0),('./x','file',0)])
  check([('./x','symlink',0)])
  check([('./x','file',1)])
 def test_public_source_drift_fails_closed(self):
  with tempfile.TemporaryDirectory() as td:
   q=Path(td)/'repo';subprocess.run(['git','init','-q',str(q)],check=True)
   with self.assertRaises(M.Failure):M.git_blob(q,M.SBL_COMMIT,next(iter(M.SBL_FILES)),next(iter(M.SBL_FILES.values())))
 def test_serialization_ignores_pythonioencoding(self):
  env=os.environ.copy();env['PYTHONIOENCODING']='utf-16'
  p=subprocess.run([sys.executable,'-c','import importlib.util; s=importlib.util.spec_from_file_location("m",r"'+str(TOOL)+'");m=importlib.util.module_from_spec(s);s.loader.exec_module(m);import json,sys;sys.stdout.buffer.write(m.encode('+repr(self.r)+'))'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,check=False,timeout=30)
  self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(p.stdout,self.raw)
if __name__=='__main__':unittest.main()
