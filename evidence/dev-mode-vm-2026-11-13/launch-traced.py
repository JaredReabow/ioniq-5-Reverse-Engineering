from pathlib import Path
import sys, hashlib, json
P=Path.cwd()
sys.path.insert(0,str(P/'tools/uk_fw'))
import vm_boot as vb
ws=P/'work/vm/kbuild/ws-dev-mode-probe'
vb.KERNEL_SHA256=hashlib.sha256((ws/'bzImage').read_bytes()).hexdigest()
vb.INIT_CHOICES=tuple(vb.INIT_CHOICES)+('/init-dev-probe.sh',) if hasattr(vb,'INIT_CHOICES') else ('/init-dev-probe.sh',)
orig=vb.qemu_command
def command(*a,**k):
 argv=orig(*a,**k)
 i=argv.index('-append'); argv[i+1]=argv[i+1].replace('root=/dev/mmcblk0 ','root=/dev/mmcblk0p5 ',1)
 argv += ['-chardev','file,id=devprobe,path=dev-probe-trace.txt','-device','isa-serial,chardev=devprobe,index=3']
 return argv
vb.qemu_command=command
(ws/'launch-identities.json').write_text(json.dumps({str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ws/'launch-traced.py',ws/'init-dev-probe.sh',P/'tools/uk_fw/guest/dev-mode-probe.sh',P/'tools/uk_fw/vm_boot.py']},indent=2)+'\n')
sys.exit(vb.run(ws,False,'echo IONIQ_VM_USERSPACE_READY',timeout=360,memory_mib=2048,init='/init-dev-probe.sh',serial_completion_marker='DEV_MODE_PROBE_COMPLETE'))
