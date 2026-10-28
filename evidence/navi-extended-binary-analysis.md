# `navi_extended` entry binary: static analysis

Status: static analysis of a public release artifact. The binary was **not
executed**. Obtained from the public `g4933/gen5w/navi_extended` release after a
GitLab rate limit cleared.

## Artifact identity

| Field | Value |
|---|---|
| File | `AppNavi` (release asset, tag 0.2.0) |
| Size | 35,201,155 bytes |
| SHA-256 | `9198abf2d8d98867a5fb55900e4acfe3a4d7c4df232cde6e86650abe83c285c7` |
| Type | ELF 64-bit x86-64 PIE, dynamically linked, stripped |
| Runtime | **.NET 6 self-contained single-file bundle** (`RPATH $ORIGIN/netcoredeps`) |
| App assembly | `navi_extended.dll`, 5,632 bytes uncompressed (2,558 deflate) |
| Assembly SHA-256 | `dc2ef0dc859de38b1ce697d1e444393e18d740639428b90398c73968d9684bc7` |

The 35 MB is almost entirely the bundled .NET runtime (151 runtime assemblies
plus `deps.json`). The application itself is 5.6 KB.

## Bundle extraction method

The bundle is a .NET single-file app: a native apphost followed by a file table
at the end of the file. Each entry is
`int64 offset, int64 size, int64 compressedSize, byte type, 7-bit-prefixed name`,
with type `1` = compressed assembly (raw deflate), `3`/`4` = uncompressed JSON.

The application assembly is the entry named `navi_extended.dll` whose header sits
in the trailing table; the same name also occurs inside `deps.json`, so an entry
must be validated by the length byte and header position before use.

## What the application does — exact logic from IL

The assembly was disassembled with `dnfile` + `dncil` (installed into a local venv
under `work/`, nothing global). Every token was resolved. The program is a single
loop and one helper:

**`<Main>$`** — an infinite loop:

1. `Directory.GetFiles("/media/usb", "install_wideopen_service.sh",
   SearchOption.AllDirectories)` → `Enumerable.FirstOrDefault<string>()`;
2. `Directory.GetFiles("/media/usb", "main_loop.sh",
   SearchOption.AllDirectories)` → `FirstOrDefault<string>()`;
3. if the first result is non-null: `ExecuteBash(install_wideopen_service.sh)`,
   then `ExecuteBash(main_loop.sh)`;
4. `Thread.Sleep(5000)` and repeat.

**`<<Main>$>g__ExecuteBash|0_0`** — takes the script **path**:

1. `script.Replace("\"", "\\\"")` — escapes double quotes only;
2. builds a `ProcessStartInfo` with `FileName = "/bin/bash"` and
   `Arguments = "-c \"" + escaped + "\""`;
3. `RedirectStandardOutput = true`, `UseShellExecute = false`,
   `CreateNoWindow = true`;
4. `Start()`, `StandardOutput.ReadToEnd()`, `WaitForExit()`, returns the output
   (which the caller discards).

### What that means operationally

- The unit re-scans the USB **every five seconds** for as long as `AppNavi` runs.
  A script left on the stick is re-executed repeatedly; a script that blocks keeps
  the helper inside `ReadToEnd()` until it exits.
- **`install_wideopen_service.sh` takes precedence** and runs before
  `main_loop.sh` — that is the documented persistence step.
- Only the **first** match of each name is used (`FirstOrDefault`), with a
  recursive search, so directory depth does not matter but duplicate names do.
- The argument passed to bash is the **file path**, not the file's contents.
- Quote escaping handles `"` but not backticks or `$(...)`. That is a command
  injection seam in the tool, but it is moot in practice: the operator already
  supplies the script.

There is **no memory-corruption exploit here and no vulnerability in the binary**.
It is a small, deliberately written trampoline: a drop-in `AppNavi` replacement
that runs a script from an attached USB stick.

## Why this matters

**The entry primitive is a legitimate app substitution, not an exploit.** The
binary only becomes reachable because the unit's own update path replaces
`AppNavi` with a file supplied on a USB stick. Everything therefore depends on
that installation path being available — Engineering Mode → Config → "Update
AppNavi from USB" — which is exactly the gate this programme already identified.

**The USB layout is now known precisely:** the unit mounts the stick at
`/media/usb` and the payload script is `main_loop.sh`. This is required for any
custom application, and it is the kind of detail that otherwise costs bench time.

**A replacement app is trivial to write.** The whole program is a file scan plus
a shell invocation. An owner-supplied `AppNavi` replacement could instead copy
`DecryptToPIPE` and the key file, install a systemd unit, or seed SSH keys. The
barrier is never the software — it is installing it once.

## Consequences for this programme

- The "exploit" phase is smaller than assumed: there is nothing to develop beyond
  a script runner, because the stock update path performs the privilege step.
- The two files needed for decryption (`DecryptToPIPE`, key material) are copied
  by a shell script from an ordinary USB stick once that script runs. The
  published tooling does exactly this.
- The remaining problem is unchanged and singular: **make the unit accept the
  AppNavi replacement**. On a patched build the option is hidden, which returns
  the plan to downgrade or to a pre-auth bug.

## Provenance and limits

- Public release asset; no device was contacted and nothing was executed.
- The behaviour above is derived from a **full IL disassembly with every token
  resolved**, not from strings. The only inference is that the two `call spec`
  instructions are `Enumerable.FirstOrDefault<string>`; that is what the generic
  MethodSpec shape and the following `brfalse`/`stloc` pattern require.
- `navi_extended.dll` is retained only as a hash reference in this note; the
  binary is not committed to the repository.
