# Disconnected bench state bundle

## Objective

Build a host-side tool that emits a strictly read-only POSIX-shell probe for an
owner-controlled embedded Linux bench and parses the captured stdout offline.
The bundle should close the current activation/identity gaps for the recovered
network, cellular, Bluetooth, SSH, SMACK, and A/B-update findings before any
active testing is considered.

## Non-goals

- no exploit traffic, malformed packets, radio discovery, pairing, or modem I/O;
- no mounts, service starts, process signals, privilege changes, or target writes;
- no credential, private-key, Wi-Fi passphrase, SIM, or message-content capture;
- no claim that recovered firmware matches the owner's installed build;
- no automatic flashing, update installation, or persistence.

## Design

`tools/uk_fw/bench_state_bundle.py` has two host-side subcommands:

1. `emit`: write or print a reviewable POSIX-shell probe. The probe only reads
   procfs/sysfs, selected non-secret files, process labels, unit state, local
   listener tables, local SDP registration when the command exists, and hashes
   of named binaries/modules.
2. `parse`: accept a serial/console transcript, strip the timestamp prefix used
   by `bench_serial.py`, recover framed sections, and write deterministic JSON.

The probe emits versioned begin/end markers and hex-encoded record bodies, so
captured command/file text cannot forge framing. Target command discovery and
stderr are suppressed rather than emitted outside records. Missing commands/
files are records, not fatal errors. The parser enforces the exact section
sequence, one valid schema, zero end statuses, no unframed interior text, a final
completion record, 64 MiB capture and 8 MiB section limits; hashes the capture,
every section, and canonical report; and derives structured hashes, units,
processes, interfaces, files, and warnings without executing transcript content.
Process command lines are
collected only for the allowlisted daemons under review; kernel command-line
output is restricted to boot/trust keys plus a full-line SHA-256.

## Safety contract

The generated probe must not contain file output redirection (stderr suppression
to `/dev/null` is allowed), file-creating commands, mount/remount, package
managers, service start/restart/enable, radio scan/find, network connection
tools, process signals, shell downloaders, or writes to `/proc`/`/sys`. `emit`
may write the generated script on the analyst host only.
The parser treats all input as data.

## Acceptance criteria

- generated script passes a static forbidden-token audit and `sh -n`;
- it covers identity, process credentials/capability masks/effective SMACK
  labels, parent relationships, optional no-new-privileges and required seccomp
  state, unit activation, listeners/interfaces, passive Wi-Fi/P2P state, oFono
  state, local Bluetooth registration, Dropbear completeness, A/B flags, and
  exact binary hashes;
- it records metadata, hashes, `SMACK64`, and `SMACK64EXEC` state for the stock
  direct-transition anchor, shell/interpreter chain, dynamic loader, fixed
  `date` candidates, and the relabel/setup scripts without executing them;
- parser handles hex-framed output, `bench_serial.py` timestamp prefixes,
  duplicate sections, incomplete captures, command/file absence, forged-marker
  text, size limits, and adversarial text;
- tests use synthetic transcripts only and do not require a device or network;
- bench runbook documents capture-before-active-testing use.

## Verification

```sh
/Users/leo/.platformio/penv/bin/python3 -m pytest -q tests/test_bench_state_bundle.py
/Users/leo/.platformio/penv/bin/python3 -m pytest -q tests
/Users/leo/.platformio/penv/bin/python3 tests/run_all.py
```
