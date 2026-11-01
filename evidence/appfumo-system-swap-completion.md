# AppFUMO system-swap completion-latch boundary

## Scope

This execution-free continuation follows the published weak `swapSystem`
Boolean into AppFUMO's production update-info handler. It asks whether successful
boot-partition writing is a mandatory gate for downstream completion handling.

Exact embedded AppFUMO identity remains size `5,066,264`, SHA-256
`464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7`,
Build ID `863a8730e66a1c5245a1bf458fe2554adee0351a`.

The complete handler is raw `[0x11f1b0,0x120a9e)`, SHA-256
`8d8cbd6f13b03f5e744a9419937d37db6390cef7c6022c7e8a4d52ee6fe3b959`.

## Controller fields

Four exact getters return one byte each from the update-state object:

| Getter | Object offset | Meaning from exact log string |
|---|---:|---|
| `0x8ed40` | `+0x44` | navigation extended update |
| `0x8ee00` | `+0x45` | root updated |
| `0x8eec0` | `+0x46` | navigation updated |
| `0x8f100` | `+0x47` | resource updated |

The handler maintains separate completion bytes:

- handler `+0x240`: system-swap complete;
- `+0x241`: navigation completion;
- `+0x242`: resource completion.

These are application bookkeeping fields, not persistent bootloader selectors.

## Root-update and swap result

At `0x11f620`, `getRootUpdated()` controls whether a system swap is requested.
If the flag is true and `+0x240` is zero, the handler calls `swapSystem` at
`0x12003f`.

- A true return stores `1` at `+0x240`.
- A false return branches back to `0x11f631`, logs the current zero latch and
  continues in the handler.
- The false return does not return from, throw from, or otherwise abort this
  handler.

The preceding package established that `swapSystem` itself can return true
without proved mount, direct-copy, pipeline-exit, unmount, or durable-write
success. Consequently `+0x240` is a weak software latch, not evidence of final
boot-partition bytes.

## What the latch gates

The exact directory predicate `[0xedef0,0xee2e3)` checks for one of four
external-unit directories. If such a directory exists **and** `+0x240` is set,
the handler constructs and executes an `ext_units` touch command and performs
related state-report handling.

That is a concrete use of the latch. The `QProcess::execute()` return at
`0x11f6f9` is not used before temporary-object destruction.

## What the latch does not gate

After the root/swap block, control proceeds to navigation and resource handling.
The marker-helper call for `/update/system_update_completed` at `0x11f8b3`
follows those blocks and has no `+0x240` predicate.

Thus, in this exact handler:

- `swapSystem == false` can continue downstream;
- root-updated false also does not require a pre-existing `+0x240` latch;
- system-completion-marker handling is not gated by `+0x240`;
- the later in-handler `UPDATE FINISH` logging path is downstream, although
  additional state, file, and scheduling predicates mean not every invocation
  necessarily reaches it.

This closes a result-propagation boundary: system-swap completion is not a
mandatory gate for downstream marker handling in this function.

## Security and reliability interpretation

The finding is a fail-open completion-accounting weakness, but static evidence
does not establish that it is exploitable by an unprivileged source. It matters
for trust-chain analysis because application-level completion can advance while
boot-partition effects remain unproved.

It does **not** establish:

- a successful or failed update on a real unit;
- control over staged boot-image bytes;
- verifier-to-writer same-byte continuity;
- successful mount, copy, decryption, `dd`, sync, unmount, marker removal, or
  state-report execution;
- a persistent boot selector, reset, MICOM/ABL acceptance, health, mark-good,
  attempts, rollback, root, or persistence.

## Public Android Gen5W route check

A concurrent public-source refresh found a current Android Gen5W project at
commit `419d7e87fc9b96fbe93f50389ff1b9014d5986e8`. Its documented unsigned DSP OTA
hook is specific to Telechips TCC803x, Android 4.4.2, `/system`, Android init,
and `troubleShooter`. The same project explicitly states that `S5W_L` is a
fundamentally different non-Android architecture.

That public route is useful comparative research, but it must not be promoted
for this recovered x86-64 Linux/SMACK firmware merely because both products use
the Gen5W name. A canonical-rootfs name check found none of its defining
Android objects (`troubleShooter`, `otaagentd`, `uagentd`, `qb_runtime.sh`,
`zygote`, or `/system/xbin`). Absence is bounded corroboration, while the exact
OS, architecture, service, and updater mismatch is the primary rejection.

Public-source identities recorded during the refresh:

- `README.md` SHA-256
  `ad0641aaee7cf4d822f177ea221e4c60c93673bc9c21f375dae3d1f5570705bb`;
- `01-DSP-OTA-troubleShooter.md` SHA-256
  `4548a537b03993c5d39a219b6b33240f22928dbc7306bf689ba13354d4b382af`;
- `03-Install-and-Uninstall.md` SHA-256
  `deef5a21f9fa4a9210e90fa6695abe6432c4de89a24c15670f7e74ad353eac50`.

No public payload or update package was copied into the tracked project and no
public exploit was executed.

## Reproduction

```sh
PY="<platformio-env>/bin/python3"
"$PY" tools/uk_fw/appfumo_system_swap_completion.py \
  work/public-vuln-research-20261101/appupgrade-exact-extract/AppUpgrade.embedded-5721c8.elf \
  -o work/appfumo-system-swap-completion.json
"$PY" -m pytest -q tests/test_appfumo_system_swap_completion.py
```
