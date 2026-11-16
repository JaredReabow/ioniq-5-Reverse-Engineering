# AppLauncher app-ID-300 option and process-start boundary

## Scope

This package binds the recovered EU `260128` canonical-rootfs `AppLauncher` to
the ordinary dynamic-process path used by app ID 300. It answers four narrow
static questions:

1. where the process program and generated `QStringList` are stored;
2. how the generated list reaches `QProcess::start`;
3. how the embedded vehicle-option table and external override are selected;
4. which static predicate uniquely identifies the recovered NE/EUR fallback row.

It does **not** execute the launcher or prove owner-unit runtime selection,
D-Bus delivery, child creation, privilege, update acceptance, writes, boot
acceptance, or persistence.

## Canonical identities

The analyzer binds one stable no-follow descriptor for the canonical archive:

- archive size: `879109759` bytes;
- archive SHA-256:
  `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`;
- member count: `66836`;
- normalized inventory SHA-256:
  `c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c`;
- selected member: `./app/bin/AppLauncher`;
- canonical external `app/bin/CarOption.csv` member: absent.

The selected executable is:

- size: `407720` bytes;
- SHA-256:
  `c8d6d56bc254ad0731e81f40bd83aa9b3be6b49bcbd8efb291157a06c4a84268`;
- Build ID: `0452df1033bd1bbae15727a83d4d56576d8b9444`.

Canonical absence is not promoted to an owner-unit runtime fact. An installed
unit can differ or provide generated, overlaid, alternate, or updated data.

## Whole-program instruction and unwind binding

Using identity-bound Homebrew LLVM 23.1.3 with raw instruction bytes suppressed:

- decoded instructions: `59259`;
- canonical instruction SHA-256:
  `a83cf95ee11850142b5c6b37d7a2d861f48452521aa1d8b4f57fd74c08faa168`;
- FDE records: `436`;
- canonical FDE SHA-256:
  `b7d430bbf6dedd5285ffdabe84188d7eb404909550ffc3aaf1f7380a30a664c5`.

The earlier strict-parser failure came from feeding `llvm-objdump` output that
included raw-byte columns to a parser whose grammar intentionally expects
address, mnemonic, and operands. The package retains strict malformed-line and
malformed-mnemonic rejection and invokes `--no-show-raw-insn`; it does not skip
or weaken malformed records.

Relevant FDEs are:

- process-start control flow: `[0x163f0,0x1854d)`;
- option-loader caller: `[0x19860,0x19a3e)`;
- dynamic process construction: `[0x1fd30,0x1ffcf)`;
- option builder: `[0x34510,0x36a74)`;
- table-map builder: `[0x37530,0x378c9)`;
- external-option loader: `[0x378d0,0x37d54)`;
- embedded-table constructor: `[0x37d60,0x3809e)`;
- selector: `[0x380a0,0x3987a)`.

The retained manifest binds 127 machine anchors and the complete direct-call
inventories for seven relevant targets.

## Table-source behavior

The constructor creates a UTF-8 QString from the exact byte range
`[0x4ba10,0x523c5)`:

- size: `27061` bytes;
- SHA-256:
  `d56aaf6fff599e4b26afa8a845a6afb54e8726d166c535fb5ca379c56bb1c358`;
- delimiter occurrences: `128`;
- split components: `129`.

It stores that string as the active source at loader-object `+0x18`, copies it
to the embedded fallback field at `+0x20`, then calls the external loader.

The external loader checks the fixed external pathname. If the file exists and
read-open succeeds, it reads the complete file, decodes it as UTF-8, and
replaces active source `+0x18`. If it is absent or open fails, the embedded
source remains active.

If selection from an external source leaves the selected-option list empty and
the selector's fallback-mode argument is zero, the selector copies embedded
fallback `+0x20` back to active source `+0x18` and reinvokes itself at `0x38df0`
with fallback mode one. This permits at most one external-to-embedded fallback
transition. It does not prove that arbitrary malformed input is safely handled;
no malformed file was created or executed.

## Constructor inputs and recovered-row predicate

The caller at `0x19925` forwards 12 logical values from its source object,
followed by initial fallback mode zero. Their source offsets, in logical order,
are:

`+0x60`, `+0x3f`, four bytes at `+0x1d`, `+0x3e`, `+0x32`, `+0xad`,
`+0xc0`, `+0xc1`, Boolean-from-`+0x84`, `+0x3d`, `+0x3a`, and `+0x83`.

The selector copies these to loader fields `+0x41`, `+0x42`, `+0x44`, `+0x48`,
`+0x49`, `+0x51`, and `+0x53..+0x58` respectively.

For the normal, non-performance-one branch, the matching keys are:

- logical argument 4 formatted as a lowercase `0x`-prefixed two-digit vehicle
  value; and
- logical argument 7 formatted as the energy-type option.

The branch is selected when logical argument 12 does not format to the
performance-one token. Matching uses case-folded vehicle equality and exact
energy-token equality. In the embedded table, vehicle value role `0x26` plus
energy value role `8` uniquely identifies split component 50. Its region column
contains EUR, but that region column is **not** a selector predicate. Therefore
EUR is recovered row data, not proof of the owner unit's runtime region input.

The selected component has 38 comma-split fields including its terminal empty
field. Its 17 ordered option fields have normalized line-list SHA-256:

`4a265a6c887376163f37544abec770074afe3ec63d063eaf9bdf28a87010d04a`.

The update-mode option is ordinal 14 (zero-based) in that ordered list and has
value role zero. The report deliberately retains roles and hashes rather than a
callable argument list.

## AppProcess and `QProcess::start` binding

The dynamic helper `[0x1fd30,0x1ffcf)` accepts app IDs 1 through 1024, so ID 300
uses this ordinary path. It:

- allocates the process object at `0x1fe28`;
- stores app ID at `AppProcess+0x20` (`0x1fe43`);
- stores the requested executable at `AppProcess+0x58` (`0x1fe61`);
- calls option builder `0x34510` at `0x1fec8` with mode zero;
- stores the generated `QStringList` at `AppProcess+0x60`
  (`0x1fed2..0x1feef`).

Inside `[0x34510,0x36a74)`, the ordered selected-option list at loader `+0x28`
is appended at `0x35c8e..0x35cd2`. Therefore, if the recovered row is selected,
its 17 options are appended in table order.

That does not make the *whole* runtime argv statically fixed: the builder also
uses runtime fields, runtime file state, and conditional options. The exact
bounded result is the ordered selected-row contribution and its transfer into
the generated list, not a fabricated complete owner-unit argv.

In `[0x163f0,0x1854d)`:

- `0x16679` binds `AppProcess+0x60` as the `QStringList` address later passed in
  `%rdx`;
- `0x17430` obtains `AppProcess+0x58`, later passed as the program in `%rsi`;
- `0x1745d` calls `QProcess::start(program, arguments, openMode)` with open-mode
  immediate 3 and the process object as receiver.

Static construction and register binding do not prove `QProcess` accepts the
request or that a child is created or successfully execs.

## Runtime unknowns

The report keeps these values null:

- owner-unit binary/data identity and external-option-file state;
- owner-unit vehicle/model inputs and satisfaction of the recovered predicate;
- complete runtime argument list;
- D-Bus delivery;
- `QProcess` acceptance, child creation, and successful `exec`;
- resulting credentials and SMACK label;
- update acceptance, partition writes, boot acceptance, and persistence.

## Reproduction

```sh
<platformio-env>/bin/python3 tools/uk_fw/applauncher_app300_argv.py \
  --rootfs <canonical-rootfs.tar.gz> \
  --applauncher <canonical-AppLauncher> \
  --manifest evidence/artifacts/application-candidates/applauncher-app300-argv-manifest.json \
  --objdump <identity-bound-llvm-objdump> \
  --readelf <identity-bound-llvm-readelf>
```

The deterministic output must equal
`evidence/artifacts/application-candidates/applauncher-app300-argv-report.json`
byte for byte. Supplied filesystem paths and raw target instruction bytes are
not retained.
