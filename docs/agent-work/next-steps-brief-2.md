# FROZEN BRIEF 2 — next best steps, after the Blocker-1 instrument proof

Supersedes `next-steps-brief.md` only where it conflicts. Everything in brief 1 still stands unless
changed below. Frozen 2026-11-06.

## Newly measured since brief 1

**A. Blocker 1's instrument now proves it reaches its target.** `gl_draw_trace.c` previously wrote
nothing on load, so "shim never loaded" and "shim loaded but `glShaderSource` never called" were
indistinguishable — both left zero dump files, and a no-op variant would have read as a falsified
hypothesis. A constructor now writes `/tmp/gl-draw-trace.active`, and each `glShaderSource` appends
to `/tmp/gl-draw-trace.calls` with `frag_needle` / `vtx_needle` / `fix_mode`. Verified in the guest
without weston, GL or a GPU by loading the shim and driving it directly:

```
loaded pid=708
pid=708 shader=1 count=1 len=319 frag_needle=yes vtx_needle=yes fix_mode=0
pid=708 shader=2 count=1 len=85  frag_needle=no  vtx_needle=yes fix_mode=0
pid=708 shader=3 count=1 len=54  frag_needle=no  vtx_needle=no  fix_mode=0
```

So the needle discriminator works. **Still unproven:** that the vendor app's real fragment shader
contains the needle. That needs one authentic-HMI run with no fix marker.

**B. The USB-swap question narrowed.** The updater stage wipes and recreates its own staging tree
before installing:

```
rm -rf /update/HU /update/HU.tar* /update/micom /update/gps /update/S5W_*.tar;
mkdir -p /update/HU/firmware /update/HU/images;
```

with `cp -r %1 %2`, `cp -ar %1 %2`, `cp -vf %1 %2`, `tar -xzvm -C`, `unzip -o %1 -d %2` alongside.
The install very likely consumes `/update/HU`, not the medium. **The open question is therefore no
longer "does the consumer read the medium" but "is the copy made before or after signature
verification?"** Copy-then-verify refutes the published swap technique; verify-then-copy still
permits it, because the swap would only need to precede the copy. Verdict remains AMBIGUOUS but
leans refuted.

**C. No unprivileged local principal.** Across `lib/systemd/system/` the only `User=` directive is
`dropbear@.service`'s `User=%i`; everything else runs as root by default. A local-privesc framing has
no attacker context to escalate from unless a media parser first manufactures one.

**D. `/tmp`-based auth tampering is blocked.** Someone proposed racing whatever writes `/tmp/shadow`;
`esinit` mounts `/tmp` as tmpfs (default `01777`) and the entry is a root-owned symlink, so the
sticky bit prevents replacement.

## Unchanged constraints

No physical device (QEMU VM only, shared with another thread). Identify and test exploits; build no
payloads, no flashing procedures, no operational signature bypass. Conclusions bind to exact bytes.
The guest cannot reproduce the USB gadget stack (`lge_usb_adapter` oopses in `sbi_apl_commit`).

## The question

1. **Single highest-value next action now**, given A-D. One recommendation, not a menu. Say whether it
   is the VM side or the security side, and why it beats the alternatives.
2. Is the newly narrowed ordering question (copy-before-verify vs verify-before-copy) worth pursuing
   next, and what is the cheapest exact test?
3. What should be abandoned now?
4. Anything in A-D you think is wrong or over-claimed?

Cite §A-§D. Be decisive. Under 700 words. No preamble.
