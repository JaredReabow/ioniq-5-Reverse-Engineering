# Intel TXE 3.1.50 advisory applicability

## Scope

This note compares the exact Intel firmware identity recovered from the EU
`260128` ABL image with Intel's public security advisories. It is an offline
applicability assessment. It does not establish installed-unit identity,
Linux-to-TXE reachability, a usable MEI client, or an exploitation procedure.
No MEI endpoint or recovered firmware module was executed.

## Exact recovered identity

The canonical 8 MiB ABL is SHA-256
`f6fc0373042c27f36e601fe957544582f3b1bd4be3c36659105322304b2dc7ac`.
Its exact signed FTPR partition manifest contains:

- firmware version components at manifest `+0x24`: `3, 1, 50, 2222`;
- version: **Intel TXE 3.1.50.2222**;
- manifest date field at `+0x14`: `0x20170926` (`2017-09-26`);
- TCB Security Version Number at `+0x2c`: `3`.

The exact execution layout independently agrees with public TXE v3 research:
BUP uses non-kernel-module base `0x26000`, and the signed FTPR syslib is called
at base `0x6000`. This identity is now emitted and tested by
`tools/uk_fw/abl_ias_key_provenance.py`.

## Intel-SA-00086: resolved by the recovered version

Official source:

- <https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00086.html>
- downloaded HTML SHA-256
  `df5e2e77660c45a6703daaaadf6cb5a206c3e1493c7e7e062cfceeb909536c50`.

Intel-SA-00086 identifies TXE 3.0 kernel issues including:

- CVE-2017-5707: multiple TXE-kernel buffer overflows allowing local arbitrary
  code execution;
- CVE-2017-5710: TXE-kernel privilege escalations allowing unauthorized access
  to privileged content.

Intel's resolved-version table lists **TXE 3.1.50.2222** as the production
release for Apollo Lake Atom E3900, Pentium, Celeron N, and Celeron J families.
The recovered FTPR version exactly equals that resolved release. Therefore
CVE-2017-5707/CVE-2017-5710 must not be promoted as candidates merely because
the platform uses TXE v3. Exact instruction-level backport identity was not
independently reconstructed, but Intel's own product/version classification is
direct negative applicability evidence.

## Intel-SA-00125: the recovered version is in the affected range

Official source:

- <https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00125.html>
- downloaded HTML SHA-256
  `e922a381b06eacf4e59ac7e9910d7651ca0713b22a4d155a913f586b23636e2f`.

Intel-SA-00125 states that TXE versions **3.0 through 3.1.50** are affected and
that TXE **3.1.55 or higher** is not affected. Its update table explicitly says
TXE 3.1.55 replaces **3.1.50.2222**. The recovered artifact is therefore an
exact version match for the advisory's superseded TXE release.

The relevant CVEs have materially different prerequisites:

- **CVE-2018-3655**: a subsystem flaw before TXE 3.1.55 may allow an
  unauthenticated user to modify or disclose information with **physical
  access**. Intel additionally states that a physical attacker may bypass CSME
  anti-replay protection, tamper with CSME/SPS/TXE data-file integrity, and
  potentially roll firmware back to a release affected by the earlier
  SA-00086 issues. Those consequences make persistent `/snowball` policy and
  provisioning-state rollback high-priority questions. The advisory does not
  identify the subsystem, object, transaction, or required electrical/debug
  interface, however; exact version applicability is established but an
  actionable route is not.
- **CVE-2018-12147**: insufficient input validation in the HECI subsystem before
  TXE 3.1.55 may allow a **privileged local user** to escalate privileges. This
  is a host-root/privileged-to-TXE lead, not an unprivileged Linux-root path.
  The exact rootfs ships MEI/TXE kernel modules and passive module-load
  configuration, but runtime device nodes, permissions, SMACK labels, client
  identities, transport binding, and installed bytes remain unknown.

Neither CVE by itself proves a way to replace `ipub_key`, UEP, `rot.key`, the
persistent `/snowball` policy objects, or a signed boot manifest. Those
consequences require exact client/protocol and write-authority evidence.

## Practical research consequence

For a future disconnected bench, the safe order is:

1. passively confirm installed TXE/ABL identity and whether it still reports
   `3.1.50.2222` rather than a different board or service update;
2. record `/dev/mei*`, `/dev/tpm0`, and `/dev/tpmrm0` metadata without opening
   the nodes;
3. hash the MEI/TXE and TPM/CRB/TIS modules, and record the bound transport plus
   `/sys/class/mei/*` and `/sys/class/tpm/tpm*` identities;
4. determine host credentials, DAC, capabilities, and SMACK policy required to
   reach any client;
5. identify the exact client UUID and message grammar from recovered bytes or
   authoritative public material before considering any active request;
6. obtain separate authorization for active MEI/HECI interaction, and begin
   with read-only identity operations rather than storage, provisioning, or
   update commands.

The strongest current interpretation is:

- SA-00086 is a rejected version-only lead for this exact artifact;
- SA-00125 is an exact advisory-version match and a high-priority future bench
  lead;
- CVE-2018-12147 does not solve initial Linux root because it requires a
  privileged local caller;
- CVE-2018-3655 is directly relevant to a physically isolated bench because
  Intel names anti-replay bypass, TXE data-file tampering, and rollback as
  consequences, but the public text is insufficient to derive a safe or
  reproducible interface or to equate generic TXE data files with the exact
  `/snowball` objects;
- no TXE exploit, HECI message, malformed request, flash operation, or trust
  replacement has been generated or executed.
