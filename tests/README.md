# Ioniq 5 research validation harness

Read-only checks over the research ledger, evidence artifacts, frozen Council
packages, and pre-push Git scope. The harness never writes project files, never
runs anything from the ledger, and never mutates Git state (`git status` is
invoked with `--no-optional-locks`).

## Run

```bash
python3 tests/run_all.py              # human-readable report
python3 tests/run_all.py --json       # deterministic JSON report
python3 tests/run_all.py --only json,artifacts
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The suite is 231 cases: 45% statement coverage over `tools/uk_fw` and `tests/harness`
(measured with `coverage run --branch`), and 49% over the VM/vendor toolchain
(`vm_boot`, `vendor_rootfs`, `vm_display`, `decompile`). The number is low by design in
the heavy paths: QEMU boots, image assembly and Ghidra runs happen in child processes,
so line coverage cannot see them — their behaviour is pinned by the end-to-end tests
below instead. Untested modules remain `dump_survey`, `elf_reader`, `kallsyms_*`,
`net_surface`, `ota_structure`, `bench_*` and `compare_eu_aus`.

Exit codes: `0` all checks pass or report expected state (`info`/`pending`),
`1` a validation failure or blocked Ioniq push, `2` the harness itself could not
run (missing tool or bad root).

## Checks

| Check | What it proves |
| --- | --- |
| `ledger` | `workflow.py validate --json` exits 0 with no errors (warnings report as `info`) |
| `artifacts` | every ledger artifact re-hashes to its declared SHA-256; missing, stale, unsafe, or malformed entries fail |
| `json` | the ledger and every council packet, task, receipt, and manifest parse as JSON |
| `council` | each `council/review-batch-*/` with a packet is checked against its frozen directory: unusable packets, unsafe or mismatched artifacts, and fingerprint mismatches fail; a verified package with a non-`COMPLETE` history reports as `info` |
| `privacy` | scoped files contain no live secrets or private-key containers; identifiers are reported as private-repository information, and raw firmware/archive/capture files are permitted; findings name only file, line, and category |
| `docs` | dedicated Ioniq history/changelog exist once `T6` leaves the queued states; earlier it reports `pending` |
| `gitscope` | staged `kona_research/**` paths block; otherwise an Ioniq push passes only when an explicit `ioniq` remote resolves exactly to `JaredReabow/Ioniq-5` or its renamed form `JaredReabow/ioniq-5-Reverse-Engineering`, `remote.pushDefault` is `ioniq`, and no branch `pushRemote`, push URL, or URL rewrite redirects it |

`council/`, `evidence/`, and the root documents are in privacy scope.
`kona_research/` and `tests/` are excluded so Kona work stays untouched and
fixture strings cannot self-flag.

## Decompilation tooling

`tests/test_decompile.py` covers the Ghidra wrapper without running Ghidra: a stub
`analyzeHeadless` verifies the command it builds (import, `-process` reuse,
`-analysisTimeoutPerFile`, `-max-cpu`, `-deleteProject`), the output guard and the
error paths. `tests/test_decompiled_artifacts.py` checks the decompiled output against
the published claim in `vm/evidence/vendor-userspace-260128/ivi-shell-input-audit.txt`
and is skipped when `work/decompiled/` is absent, like the Ghidra run itself.

```bash
python3 tools/uk_fw/decompile.py --binary work/.../ivi-shell.so --select ALL
python3 tools/uk_fw/decompile.py --binary work/.../AppNavi --select 0x2d6611 \
    --analysis-timeout 2700 --max-cpu 2
python3 -m unittest discover -s tests -p 'test_decompiled_artifacts.py' -v
```

## VM end-to-end test

`tests/test_vm_e2e.py` is the only test that needs hardware-level inputs. It
boots the prepared EU 260128 workspace (`work/vm/bootable-eu260128`) in QEMU and
asserts the whole chain from the host's point of view: the measured `4.1.27-abl`
kernel starts, the ext4 root is mounted through the guest-RAM-only SDHCI patch,
the shell runs as root, the ABL loader arguments are readable from sysfs, the run
artifacts match the reported result, and a guest command's exit status comes back
over the serial console.

It is skipped, never failed, when QEMU or the workspace is missing. QEMU is
resolved from `IONIQ_VM_QEMU`, then `work/tools/qemu/bin/qemu-system-x86_64`
(what `setup_eu260128.py --setup-qemu` creates), then `PATH`; the other inputs
come from the same setup command.

```bash
python3 tools/uk_fw/setup_eu260128.py --setup-qemu --boot-test
python3 -m unittest discover -s tests -p 'test_vm_e2e.py' -v
```

## Vendor end-to-end test

`tests/test_vm_vendor_e2e.py` boots the recovered vendor root instead of the
BusyBox shell and asserts eight facts from the host: dynamic loader, system and
session D-Bus, the weston Wayland socket, `AppLauncher` with `ApplicationManager`
and `AppHomeScreen`, `AppNavi` started through the manager with the observer mapped
into it, and — the interposition proof — that the observer's `wl_proxy_marshal` hook
is the definition the guest resolves (`shared=0`, `interposed=1`) and that a real
client's null attach and commits reach it (`verdict=observed complete=1`).

The vendor library exports no `wl_surface_commit` symbol at all (`PROBE
surface_symbol=0`), which is why the hook is on `wl_proxy_marshal`.

```bash
pip install --user ziglang                    # cross-build the guest helpers
python3 tools/uk_fw/vendor_rootfs.py prepare \
    --container work/firmware/IONIQ5_EU/HU/images/iasImage_1280_sub
python3 -m unittest discover -s tests -p 'test_vm_vendor_e2e.py' -v
```

The image is 8 GiB because QEMU accepts only power-of-two SD card sizes, and
`mkfs` over the 5.2 GiB vendor root takes about ten minutes once. Afterwards
`tools/uk_fw/vendor_rootfs.py refresh` patches the harness-owned files inside the
image and the manifest hashes in seconds, so chain edits do not force a rebuild.
`tests/test_vendor_rootfs.py` covers the assembly rules without any image.

## Git scope acceptance

This public repository keeps both `origin` and the explicit `ioniq` remote
on the same destination. The older shared private checkout may keep `origin`
on `kona-EV` so Kona fetch and tracking keep working; that historical
configuration does not block an Ioniq push here. Either way the guard reads
one `git config --list -z` snapshot and only echoes the destination fields it
verifies, with any embedded credentials redacted.

A push passes only when all of these hold:

- `remote.ioniq.url` (and every `remote.ioniq.pushurl`, if any) is exactly
  `JaredReabow/Ioniq-5` or its renamed form
  `JaredReabow/ioniq-5-Reverse-Engineering` on `github.com`, over HTTPS or SSH;
  GitHub redirects the old name to the new one, so both name the same
  repository;
- `remote.pushDefault` is `ioniq`;
- the current branch has no `pushRemote` or `pushurl` that overrides that
  destination, and no other branch pushes to Kona;
- no `url.*.insteadOf` or `url.*.pushInsteadOf` rule rewrites the Ioniq URL;
- no `kona_research/**` path is staged.

Blocking reason codes: `staged-kona-path`, `missing-ioniq-remote`,
`ioniq-remote-mismatch`, `insecure-ioniq-remote`, `ioniq-pushurl-mismatch`,
`push-default-not-ioniq`, `push-remote-kona-ev`, `branch-push-remote-overrides`,
`branch-push-remote-kona-ev`, `branch-push-remote-insecure`,
`branch-pushurl-mismatch`, `effective-push-mismatch`, `url-rewrite-redirect`,
`config-unavailable`, `status-unavailable`, and `branch-unavailable`.
Near matches (a fork, another owner, `Ioniq5`, a plain HTTP URL) all block. A
successful report exposes `verified_destination`; when the Kona `origin` is
present but inert it is flagged by `origin_kona` and `origin_kona_ignored`.

## Ioniq document ownership

The root `HISTORY.md` and `CHANGELOG.md` belong to the parallel Kona project.
The `docs` check therefore requires a dedicated Ioniq pair:
`Ioniq5-HISTORY.md` and `Ioniq5-CHANGELOG.md` by default, or explicitly
Ioniq-named paths declared in `T6.write_paths` (for example
`ioniq5/HISTORY.md`). Root Kona documents reported through the ledger are
recorded in `details.kona_owned_rejected` and never count as Ioniq proof; a
dedicated file that is a symlink to a Kona root document is rejected as
`details.kona_owned_alias`.

## Tool paths

The harness calls the installed skill CLIs:

- `IONIQ_WORKFLOW_VALIDATOR` (default `$HOME/.codex/skills/parallelism/scripts/workflow.py`)
- `IONIQ_COUNCIL_CHECKER` (default `$HOME/.codex/skills/the-council/scripts/council.py`)

`--workflow` and `--checker` override them per run.

## Expected live state

With the explicit `ioniq` remote and `remote.pushDefault=ioniq` configured,
`gitscope` passes when both remotes point at this public repository, or while
`origin` still points at `kona-EV` for Kona fetches with the explicit remote on
either name of the Ioniq repository.
Removing or mismatching the explicit remote, overriding the push destination on
a branch, or staging `kona_research/**` reports `blocked`. Frozen Council
generations reviewed before a final reconciliation report `info` with
`BLOCKED`/`CHANGES_NEEDED` histories while their artifact bytes verify; only a
defective package or fingerprint mismatch fails.

## Public snapshot mode

When `PUBLIC-RELEASE.md` exists, the private ledger and frozen Council packets are excluded. The runner marks those checks `info`, validates the published history and changelog directly, and applies stricter public privacy checks. This is not a validation of the original private acceptance hashes.

## Running the full suite

The suite needs **`pytest`** and **`cryptography`**. Homebrew's Python is externally managed (PEP 668), so install
them in a virtual environment rather than against the system interpreter:

```sh
python3.13 -m venv /tmp/ptvenv
/tmp/ptvenv/bin/pip install pytest cryptography
/tmp/ptvenv/bin/python -m pytest tests -q
```

Expected result on a healthy checkout: **782 passed, 351,486 subtests passed**.

Five modules (`test_asf_stream_probe`, `test_gen5w_decrypt`, `test_ipk_tool`, `test_public_rsa_probe`,
`test_appfumo_usb_pathname_model`) import `pytest` directly, so with `unittest discover` alone they fail to
import and report as errors rather than being skipped. That is a missing dependency, not a defect in the code
under test — all five tool modules are present and pass once the dependencies exist.
