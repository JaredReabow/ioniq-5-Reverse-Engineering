# European `260128` root and application-loading applicability

> **Recovery update:** later validated native TE2/xcrypt work recovered rootfs,
> GUI, AppNavi and other userspaces. The older encrypted-userland blocker and
> unit-derived-decryptor-only implication below are superseded for local VM work.
> Decryption still does not prove stock-device initial execution or update/boot
> acceptance. See current `HANDOVER.md` and `community-chat-leads.md`; no current
> physical-unit entry or downgrade is established by the supplied chat summary.

Status: published-method and exact-build static assessment. It is not an
operational live-vehicle exploit procedure.

| Mechanism | Function | Exact-build assessment |
|---|---|---|
| `navi_extended` / AppNavi replacement | Historical initial execution | Platform family matches Linux `S5W_L`; applicability to `260128` is unconfirmed and plausibly blocked by Engineering/SOP-version gating. |
| Engineering/dealer UI | Diagnostic UI | UI access alone is not root or code execution. |
| `update_decryptor` | Extract encrypted update content | Downstream tool requiring a unit-derived `DecryptToPIPE` and key material not shipped publicly. |
| `update-patcher` | Persistent modified update | Post-compromise mechanism requiring prior execution, decrypted rootfs and acceptance of unencrypted updates. |
| Gen5W Wi-Fi/SSH loop | Post-root access | Requires an already-installed replacement/main-loop mechanism. |
| CVE-2023-26243 through CVE-2023-26246 | Key disclosure and update signature/version-check bypasses | Demonstrated on `AE_E_PE_EUR.S5W_L001.001.211214`; patch status on `NE_E.EUR.S5W_L.001.001.260128` remains unknown. |
| NEMESIS | Android/TCC803x root chain | Not directly applicable to this Linux/x86-64 package. |
| Unsigned modules, kexec, devmem/kmem/kcore, debugfs | Kernel post-entry surfaces | Confirmed compiled into `260128`; no reachable unprivileged entry or permissive SMACK policy is established. |

No inspected public source establishes a stock-to-root path for exactly
`260128`. `navi_extended` is the only family-matched published initial-entry
design found, but its prerequisite is not proven on this release. The other
public components are decryption, persistence or remote-access tools used after
execution has already been obtained.

Application loading is native Linux/Qt deployment, not APK installation.
Published examples replace rootfs/application files and create systemd units.
The complete European package now contains `mango-rootfs.tar.gz`,
`appnavi.tar`, `new_gui.tar.gz`, and update metadata, but those payloads are
opaque encrypted envelopes rather than directly extractable archives. Exact
stock launchers, service identities, SMACK rules and application-integrity
checks therefore still require legitimate plaintext recovery or equivalent
passive evidence from the owned unit.

Decisive remaining checks are the AppNavi Engineering/SOP gate, the exact
`DecryptToPIPE` interface, userland installer checks, kernel-keystore
enforcement, SMACK policy and application-integrity checks.

The broader feasibility analysis is recorded in
`evidence/eu-custom-firmware-feasibility.md`. It separates the four required
stages—initial execution, privilege transition, persistence and recoverable
boot/update trust—and records defensive audit surfaces without implementing a
zero-day, bypass, modified image or live procedure.

