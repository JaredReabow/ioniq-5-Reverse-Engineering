#!/usr/bin/env python3
"""One-shot local experiment: adapt SDHCI matching in guest RAM, retain logs."""
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
QEMU = '/opt/homebrew/bin/qemu-system-x86_64'
BREAK = 0xffffffff81b24bac  # sdhci_driver_init
ENTRY = 0xffffffff8164c960 + 61 * 32
EXPECTED = struct.pack('<6IQ', 0x1022, 0xffffffff, 0xffffffff, 0xffffffff,
                       0x080500, 0xffff00, 0xffffffff8164d140)
REPLACEMENT = struct.pack('<6IQ', 0x1b36, 7, 0xffffffff, 0xffffffff,
                          0x080500, 0xffff00, 0)

class RSP:
    def __init__(self, path):
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.s.settimeout(60)
        self.s.connect(str(path))
    def send(self, command):
        b = command.encode()
        self.s.sendall(b'$' + b + b'#' + f'{sum(b) & 255:02x}'.encode())
        return self.recv()
    def recv(self):
        while self.s.recv(1) != b'$':
            pass
        b = bytearray()
        while True:
            c = self.s.recv(1)
            if c == b'#': break
            if not c: raise EOFError()
            b.extend(c)
        checksum = self.s.recv(2)
        if int(checksum,16) != sum(b)&255: raise ValueError('RSP checksum')
        self.s.sendall(b'+')
        # Run-length encoding appears in memory responses.
        decoded = bytearray()
        i = 0
        while i < len(b):
            if b[i] == ord('*'):
                i += 1
                decoded.extend(decoded[-1:] * (b[i]-29))
            elif b[i] == ord('}'):
                i += 1
                decoded.append(b[i] ^ 0x20)
            else: decoded.append(b[i])
            i += 1
        return decoded.decode()

run = OUT / time.strftime('probe-%Y%m%d-%H%M%S')
run.mkdir()
# Relative socket paths keep macOS sockaddr_un below its path limit.
cmd = [QEMU, '-machine', 'q35', '-accel', 'tcg', '-cpu', 'max,vendor=GenuineIntel',
       '-m', '1024', '-smp', '2', '-nic', 'none',
       '-kernel', str(OUT/'bzImage'),
       '-device', f'loader,file={ROOT}/work/vm/manifest.bin,addr=0x20000000',
       '-device', f'loader,file={ROOT}/work/vm/seed_dev.bin,addr=0x21000000',
       '-device', f'loader,file={ROOT}/work/vm/seed_user.bin,addr=0x21000040',
       '-device', 'sdhci-pci,id=sdhci0',
       '-drive', f'if=none,id=sd0,format=raw,file={OUT}/rootfs-compatible.img,snapshot=on',
       '-device', 'sd-card,drive=sd0',
       '-append', 'root=/dev/mmcblk0 rootwait rootdelay=2 rootfstype=ext4 rw init=/init '
                  'console=ttyS0,115200 panic=-1 loglevel=8 initcall_debug '
                  'ABL.oemkm=40@20000000 ABL.seed=21000000,21000040',
       '-display', 'none', '-serial', 'stdio', '-monitor', 'none',
       '-qmp', 'unix:qmp.sock,server=on,wait=off',
       '-gdb', 'unix:gdb.sock,server=on,wait=off', '-S', '-no-reboot']
(run/'command.json').write_text(json.dumps(cmd,indent=2)+'\n')
print(run, flush=True)
with (run/'serial.log').open('wb') as log:
    p = subprocess.Popen(cmd,cwd=run,stdout=log,stderr=subprocess.STDOUT,
                         stdin=subprocess.PIPE,env={**os.environ, 'TMPDIR':str(run)})
    try:
        for _ in range(100):
            if (run/'gdb.sock').exists(): break
            if p.poll() is not None: raise RuntimeError('QEMU exited')
            time.sleep(.1)
        os.chdir(run)
        r = RSP('gdb.sock')
        print('initial',r.send('?'),flush=True)
        print('break',r.send(f'Z1,{BREAK:x},1'),flush=True)
        print('stop',r.send('c'),flush=True)
        actual = bytes.fromhex(r.send(f'm{ENTRY:x},20'))
        print('entry',actual.hex(),flush=True)
        assert actual == EXPECTED, (actual.hex(),EXPECTED.hex())
        print('patch',r.send(f'M{ENTRY:x},20:{REPLACEMENT.hex()}'),flush=True)
        assert bytes.fromhex(r.send(f'm{ENTRY:x},20')) == REPLACEMENT
        (run/'patch.json').write_text(json.dumps(dict(address=hex(ENTRY),expected=EXPECTED.hex(),replacement=REPLACEMENT.hex()),indent=2)+'\n')
        print('unbreak',r.send(f'z1,{BREAK:x},1'),flush=True)
        print('detach',r.send('D'),flush=True)
        r.s.close()
        for _ in range(300):
            serial=(run/'serial.log').read_bytes()
            if b'IONIQ_VM_USERSPACE_READY' in serial or p.poll() is not None: break
            time.sleep(.1)
        if p.poll() is not None: raise RuntimeError('QEMU exited before userspace')
        if b'IONIQ_VM_USERSPACE_READY' not in serial: raise RuntimeError('userspace timeout')
        p.stdin.write(b"echo IONIQ_VM_INTERACTION_OK; /bin/busybox id; /bin/busybox uname -r; /bin/busybox cat /sys/bus/pci/devices/0000:00:02.0/vendor; /bin/busybox cat /proc/partitions; echo IONIQ_VM_COMMAND_DONE\n")
        p.stdin.flush()
        time.sleep(2)
        q = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        q.settimeout(5); q.connect('qmp.sock')
        f=q.makefile('rwb',buffering=0)
        responses=[json.loads(f.readline())]
        for command in ['qmp_capabilities','query-pci','query-status']:
            f.write((json.dumps({'execute':command})+'\n').encode())
            while True:
                response=json.loads(f.readline()); responses.append(response)
                if 'return' in response or 'error' in response: break
        (run/'qmp.json').write_text(json.dumps(responses,indent=2)+'\n')
        f.close(); q.close()
    finally:
        if p.poll() is None:
            p.terminate()
            try: p.wait(timeout=5)
            except subprocess.TimeoutExpired: p.kill(); p.wait()
print('saved',run)
