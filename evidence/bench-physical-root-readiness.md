# Passive physical-root readiness assessment

Status: host-side implementation complete; synthetic validation only. No physical device, target network, hardware helper, uevent, service activation, virtual-terminal switch, or exploit input was used.

## Purpose

`tools/uk_fw/bench_physical_root_readiness.py` consumes the canonical JSON produced by `tools/uk_fw/bench_state_bundle.py parse`. It answers one bounded question: does a future disconnected owner-bench capture show the exact installed prerequisites for the recovered CVE-2026-40225 hardware-property chain and dormant root debug console?

It does **not** generate a malicious SCSI serial or V4L product string. It does not execute `scsi_id` or `v4l_id`, request `SYSTEMD_WANTS`, start `debug-shell.service`, access `/dev/tty9`, or claim root.

## Newly captured passive facts

The existing emitted state probe now records metadata and SHA-256 for:

- `/lib/systemd/systemd`;
- `/lib/systemd/systemd-udevd`;
- `/lib/udev/scsi_id` and `/lib/udev/v4l_id`;
- `50-udev-default.rules`;
- `60-persistent-storage.rules`;
- `60-persistent-v4l.rules`;
- `99-systemd.rules`;
- `debug-shell.service`.

It also records `/dev/tty9` metadata and the read-only `systemctl show` fields `LoadState`, `ActiveState`, `SubState`, and `UnitFileState` for `debug-shell.service`. These additions only read existing state and write framed evidence to stdout.

## Exact recovered references

| Object | SHA-256 |
|---|---|
| PID 1 systemd | `a7f5290180223def9e09570edac76f50a1bfe40b63480153daad1f22d54032b5` |
| systemd-udevd | `f32f6296ea20d959ac046ae80724f39e317aaaf492a5c7eedd9270b5b2abab0d` |
| scsi_id | `85aa83a73d44f19f6b60162a53ee896854b71e7882848819aad20c1ccf079b32` |
| v4l_id | `afb756b457284578c29960d4abd57f9612020fb45a14fbc285f5061da90a7125` |
| 50-udev-default.rules | `c90d7b298f009b82995fdcb288cd717e6d196640b0c8d3d1505b9cb402de7039` |
| 60-persistent-storage.rules | `5757bc1da0b3e07ee1769faa266af7720b8eef21006212051a8720c02eab5a8e` |
| 60-persistent-v4l.rules | `219eb6b4c0df4d8701cc5a316b2ddf63797d4c1b689bc0b289d5cb8063a7034e` |
| 99-systemd.rules | `87799b92929bed3766a2c6f7a186035886043e62f93fa3bf9995cc8ca66fdd5c` |
| debug-shell.service | `b277d7ffcfdbc9198af6935b64c167c8f7d50ec9ec9acb93b5f7b5d815cfe518` |

These identities bind the exact files previously reviewed in `evidence/systemd-udev-cve-2026-40225.md`. A version string alone is not accepted.

## Gates

The assessor emits pass/fail/unknown gates for:

1. complete, warning-free canonical capture;
2. systemd and systemd-udevd identities;
3. SCSI helper and storage-import rule identities;
4. systemd block-device tag rule identity;
5. exact debug-shell unit identity;
6. `LoadState=loaded` for the debug-shell unit;
7. `/dev/tty9` as character device `4:9`;
8. V4L helper, import rule, and generic `REMOVE_CMD` rule identities.

An inactive or disabled but loaded debug-shell unit passes only the load-state prerequisite. It does not become activation evidence: explicit hardware-derived unit requests are the behavior under assessment, while default enablement is not required by the recovered path.

An observed mismatch is `fail`. An absent or unavailable observation is `unknown`. An incomplete capture prevents either prerequisite verdict from becoming true.

## Verdict boundaries

The output contains two positive prerequisite booleans:

- `scsi_root_console_prerequisites_observed`;
- `v4l_property_injection_prerequisites_observed`.

The following values are always false because the passive capture cannot establish them:

- hardware control bytes observed;
- property injection observed;
- debug-shell activation observed;
- interactive console observed;
- root access demonstrated;
- persistence demonstrated.

Even a fully passing report does not prove that a physical USB/SCSI bridge preserves control characters into the shipped helper, that the production port exposes the required device class, that a generated property reaches PID 1, that tty9 is visible/selectable on the production display, or that keyboard input reaches it.

## Input hardening

The assessor:

- caps input at 64 MiB;
- decodes strict UTF-8;
- rejects duplicate object keys and non-finite constants;
- requires exact schema `ioniq-bench-state/v1`;
- verifies lowercase SHA-256 fields and the input canonical digest;
- validates typed facts and unit/file records;
- writes deterministic UTF-8/LF JSON through `sys.stdout.buffer`;
- creates an output file exclusively and refuses overwrite.

## Use

```sh
PY="${PYTHON:-$HOME/.platformio/penv/bin/python3}"
"$PY" tools/uk_fw/bench_state_bundle.py parse work/bench/state.log \
  --json work/bench/state.json
"$PY" tools/uk_fw/bench_physical_root_readiness.py \
  work/bench/state.json -o work/bench/physical-root-readiness.json
```

Review the JSON gates before any active experiment. The next physical step remains a benign hardware-delivery characterization on an isolated bench, not a root-shell request.
