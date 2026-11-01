AppFUMO post-write finalization — selected exact-static decoded instructions
Exact ELF SHA-256: 464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7
Build ID: 863a8730e66a1c5245a1bf458fe2554adee0351a
Instruction authority: Homebrew LLVM llvm-objdump, raw VAs, bytes suppressed
Ghidra project addresses for these raw VAs are raw VA + 0x100000.

Virtual dispatch binding (.rela.dyn)
  relocation slot 0x6ce350: R_X86_64_RELATIVE addend 0xd1e70
  finish FDE: [0xd1e70, 0xd327f)
  fstab helper FDE: [0xd0c80, 0xd1e6c)

Selected update-record admission in the fstab helper
  d0c82  lea  0x21ffa7("root"), %rsi
  d0cc4  call 0xbe1a0
  d0cd3  lea  0x21648e("vr"), %rsi
  d0ce8  call 0xbe1a0
  d0cf8  lea  0x2163a0("foldervr"), %rsi
  d0d0d  call 0xbe1a0
  d0d1c  test %bpl, %bpl
  d0d1f  jne  0xd0d70
  d0d21  ... skip helper body and retain true result

Selected VR partition-path derivation
  d0d9b  lea  0x2163a0("foldervr"), %rsi
  d0dbf  call 0xa0e10    ; active pathname helper
  d0dfb  call 0xa14c0    ; inactive pathname helper
  d0ee8  lea  0x21648e("vr"), %rsi
  d0f0c  call 0xa0e10    ; active pathname helper
  d0f48  call 0xa14c0    ; inactive pathname helper

Supported inactive-root configuration paths
  d0e10  lea  0x21a8f6("/mnt/root/etc/fstab_emmc"), %rsi
  d16ec  lea  0x21a90f("/mnt/root/etc/fstab_emmc_fde"), %rsi
  d0f7d  lea  0x21a92c("/mnt/root/etc/fstab"), %rsi

Replacement and durability sequences
  d1286  call QString::replace
  d12ff  call QIODevice::write
  d1365  call QFileDevice::flush
  d1374  call fsync
  d137c  call QFileDevice::close

  d15d9  call QString::replace
  d165a  call QIODevice::write
  d16c8  call QFileDevice::flush
  d16d7  call fsync
  d16df  call QFileDevice::close

  d19b4  call QString::replace
  d1a37  call QIODevice::write
  d1a9d  call QFileDevice::flush
  d1aac  call fsync
  d1ab4  call QFileDevice::close

finish: inactive-root maintenance before the fstab helper
  d1eb0  call sync
  d1eba  call sleep
  d1ee4  lea  0x21a140("mount | grep /mnt/root | awk '{print $1}'"), %rsi
  d1f1d  lea  0x21ffa7("root"), %rsi
  d1f47  call 0xa14c0    ; inactive root pathname
  d1fd0  call QString::compare
  d1fe3  je   0xd23fd    ; already mounted device matches inactive root
  d2189  lea  0x21a96f("-t"), %rsi
  d216d  lea  0x211123("ext4"), %rsi
  d20dc  lea  0x21e79e("mount"), %rsi
  d22e4  call 0x13bba0  ; process helper

finish: helper result and completion-flow rejoin
  d2400  call 0xd0c80   ; fstab helper
  d2405  test %al, %al
  d2407  je   0xd2c08
  d2429  movb $1, 0x10(%rsp)
  d245c  movl $99, %ecx
  d246a  call 0x168570  ; progress/reporting helper
  ...
  d2c08  ... log helper failure
  d2c28  movb $0, 0x10(%rsp)
  d2c2d  jmp  0xd242e   ; rejoins immediately before progress 99

finish: bounded post-write maintenance
  d28cd  lea  0x210e66("/sbin/fstrim"), %rsi
  d2889  lea  0x216476("/rw_data/mnt/root"), %rsi
  d28ea  call 0x13bfd0
  d2920  call umount

  d29b1  lea  0x210e66("/sbin/fstrim"), %rsi
  d296d  lea  0x21a8b0("/rw_data/mnt/app"), %rsi
  d29ce  call 0x13bfd0
  d2a04  call umount

  d2b9c  lea  0x210e66("/sbin/fstrim"), %rsi
  d2b58  lea  0x21649e("/rw_data/mnt/vr"), %rsi
  d2bb9  call 0x13bfd0
  d2bef  call umount

finish: resume-marker cleanup, progress 100 and preserved result
  d2a51  lea  0x21a361("/update/resumeBlockNumber"), %rsi
  d2a6b  call 0x13feb0
  d2a80  lea  0x21a3ab("/tmp/resume_mode_block_number"), %rsi
  d2a9a  call 0x13feb0
  d2aaf  lea  0x21a988("System Update Complete!!"), %rsi
  d2ac6  lea  0x21a9a1("System"), %rsi
  d2add  movl $100, %ecx
  d2aeb  call 0x168570  ; progress/reporting helper
  d2b0a  movzbl 0x10(%rsp), %ebp
  d2b34  movl %ebp, %eax
  d2b4d  ret

Boundary
  These instructions establish inactive-root post-write maintenance and a
  completion-reporting/return-value split. They do not establish final partition
  integrity, persistent boot-slot activation, boot acceptance, mark-good,
  rollback, root, or persistence.
