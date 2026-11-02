# AppLauncher app-ID-300 argv checkpoint

Status: implementation complete; independent acceptance blocked by unavailable
requested Fable route. Not committed or published.

## Exact-static result

- Canonical AppLauncher and rootfs identities are bound.
- Complete instruction inventory: `59259`, SHA-256
  `a83cf95ee11850142b5c6b37d7a2d861f48452521aa1d8b4f57fd74c08faa168`.
- Complete FDE inventory: `436`, SHA-256
  `b7d430bbf6dedd5285ffdabe84188d7eb404909550ffc3aaf1f7380a30a664c5`.
- Strict complete-disassembly parsing is restored with
  `--no-show-raw-insn`; malformed-record rejection remains enabled.
- Embedded table `[0x4ba10,0x523c5)` is `27061` bytes, SHA-256
  `d56aaf6fff599e4b26afa8a845a6afb54e8726d166c535fb5ca379c56bb1c358`.
- Canonical `app/bin/CarOption.csv` is absent, without promotion to an
  owner-unit runtime fact.
- External exists/open/read/replace behavior and one-transition fallback to
  embedded source are bound.
- The normal branch uses formatted vehicle argument 4 and energy argument 7
  when performance argument 12 is not the performance-one value.
- Embedded vehicle role `0x26` plus energy role `8` uniquely identifies split
  component 50; EUR is row data, not a region predicate.
- Its 17 selected options have normalized sequence SHA-256
  `4a265a6c887376163f37544abec770074afe3ec63d063eaf9bdf28a87010d04a`.
- App ID 300 follows dynamic construction, with program at `AppProcess+0x58`,
  generated list at `+0x60`, and `QProcess::start` at `0x1745d`.
- The complete runtime argv remains unknown because builder output also depends
  on runtime fields, runtime files, and conditional branches.

## Validation

- focused: `6 passed in 7.38s`;
- full tests suite: `874 passed, 351661 subtests passed in 121.87s`;
- deterministic report SHA-256:
  `f6e7b1050f01447725c8542740cf7fae0fa741eac48965e8699ec1e97e8c9189`;
- manifest SHA-256:
  `1e92ec33f565b0947f901ff269c195357a5f809f7029922326d0c54a2727d1a7`;
- `git diff --check`: passed.

## Review blocker

The exact requested Fable dispatch failed:

`Unknown child model: openrouter/claude-fable-5.1`

No alternate model was silently substituted. A fresh read-only review remains
required before acceptance, commit, or publication.
