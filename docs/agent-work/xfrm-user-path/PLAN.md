# Plan — exact CVE-2017-7184 XFRM-user path applicability audit

## Objective

Determine whether the exact recovered EU `260128` kernel package contains the
upstream/named `CONFIG_XFRM_USER` update path required by CVE-2017-7184, without
running recovered targets or performing any target/runtime operation.

## Authoritative contract

1. Treat version history as context, not classification evidence. Retain exact
   public records for introducing commit
   `d8647b79c3b7e223ac051439d165bc8e7bbb832f` and historical incomplete
   verifier commit `e2b19125e94124daaeda1ddcf9b85b04575ad86f`. Bind mainline fixes
   `677e806da4d916052585301785d847c3b3e6186a` and required follow-up
   `f843ee6dd019bcece3e74e76ad9df0155655d0df` to the retained public
   patches. Both fix effects, or exact equivalents, would be required to call an
   existing path remediated; verifier presence alone is insufficient. Official
   stable 4.1.y backports `438db92d7f2792e3bad17be70e6edf0f44a081f0`
   and `171a957989c4f398adb41078dbfff73b0821e383` first appear together in
   Linux 4.1.49, released 22 January 2018.
2. Preserve the source-level path boundary:
   `XFRM_MSG_NEWAE -> static xfrm_new_ae -> xfrm_replay_verify_len ->
   xfrm_update_ae_params` in the `CONFIG_XFRM_USER` translation unit.
3. Preserve upstream v4.1 build/interface boundaries: `XFRM_USER` is a tristate
   depending on `INET` and selecting `XFRM_ALGO`; `net/xfrm/Makefile` alone
   gates `xfrm_user.o` on `CONFIG_XFRM_USER`; the receiver owns the
   `NETLINK_XFRM` interface and applies the operation-wide `CAP_NET_ADMIN`
   check.
4. Keep `CONFIG_NET_KEY` separate. It is not the named `xfrm_new_ae`
   implementation and cannot substitute for or be conflated with this verdict.

## Exact-static method

1. Bind `work/eu-260128/vmlinux`, `kernel.config`, and authoritative
   `kallsyms.tsv` by their established SHA-256 values and record the kernel
   Build ID.
2. Verify the exact configuration facts: XFRM core and INET enabled;
   `XFRM_USER`, `NET_KEY`, USER_NS, and XFRM statistics disabled; XFRM subpolicy,
   migration, and `KALLSYMS_ALL` enabled.
3. Preserve the complete queried-name inventory for `xfrm_new_ae`,
   `xfrm_replay_verify_len`, `xfrm_user_rcv_msg`, `xfrm_netlink_rcv`,
   `xfrm_user_net_init`, `xfrm_user_init`, `xfrm_dispatch`, and `xfrm_msg_min`.
   Report their absence only as this bounded inventory, not as proof against
   every inlined or vendor-equivalent route.
4. Regenerate complete `xfrm_init_replay
   [0xffffffff8151979d,0xffffffff815197f6)` from the exact ELF and retain it
   with selected core XFRM symbol identities. These contrary facts prevent a
   whole-XFRM absence or safety claim.
5. Hash and inventory the canonical decrypted stock archive directly and
   read-only: `work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz`, SHA-256
   `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`.
   Record its 163 regular member names ending `.ko`, absence of member names
   ending `xfrm_user.ko` and `af_key.ko`, and exactly the three IPv6 XFRM mode
   module member names. Treat this only as supporting canonical stock-package
   evidence, never installed runtime state or the sole decision basis. Do not
   use the mutable `extracted-safe` staging tree to establish stock identity.
6. Add a schema-v2 Boolean-only classifier with deterministic explicit UTF-8/LF,
   all-or-none fail-closed CLI, tri-state unknown for incomplete absence facts,
   an explicit contrary functional named-path fact, an explicit XFRM-core-
   present scope fact, null runtime/impact outcomes, and exhaustive assertions
   for every emitted classification field.
7. Integrate the narrow rejection into the retained artifact index, exploit
   inventory, handover, and IONIQ changelog.
8. Run only focused tests and bytecode compilation with
   `python3`, then `git diff --check`. Do not run
   or claim the complete suite, public harness, or independent acceptance.

## Acceptance criteria

- Introducing, incomplete-verifier, both mainline-fix, both stable-backport,
  Linux 4.1.49 release, and exact official-changelog records are retained with
  hashes; the two mainline patches are copied byte-for-byte.
- Exact configuration, queried-symbol, complete contrary-function, and canonical
  stock archive/member-inventory facts agree with their authoritative local
  inputs.
- The verdict rejects CVE-2017-7184 only for the upstream/named
  `CONFIG_XFRM_USER` `XFRM_MSG_NEWAE -> xfrm_new_ae` update path because that
  translation unit/interface is neither built into nor shipped with the
  recovered package.
- Version history remains contextual; exact absent-path evidence controls. The
  result does not claim XFRM core absence or safety, every vendor-equivalent
  route absent, installed runtime identity, live interface behavior, capability
  policy, verifier/fix behavior, corruption, privilege gain, root, or
  persistence.
- Incomplete absence inputs yield `null`; an explicit functional named-path fact
  makes the path present and prevents rejection.
- The model report contains classification metadata only and no operational or
  target material prohibited by the task contract.

## Non-goals and safety boundary

No recovered target execution; no endpoint creation; no netlink/XFRM operation;
no message, attribute, packet, namespace, capability request, module action,
trigger, race, payload, or firmware material. Unrelated MICOM source/binary work
is out of scope and must not be staged or modified by this package. This is a
defensive exact-static applicability assessment of one named upstream path, not
a broad XFRM audit.

## Execution status

The installed `astra_terra_builder_deepseek_flash` binding remains only
static-ready for `deepseek/deepseek-v4.1-flash`; no inference request was made,
so runtime routing remains unverified. Generic public research was delegated to
Astra without private target details, while exact package implementation and
review used the approved native exact-binary route.
