# Custom firmware build path: repacking the rootfs

Status: deterministic construction of a plaintext rootfs archive in the format
documented by the public `update-patcher`. Offline only. This is a build tool,
not a demonstrated update-acceptance path. Exact recovered routing and marker
semantics are in `evidence/appupgrade-update-trust.md`.

## Recovered routing correction

The recovered `260128` outer `AppUpgrade` contains two updater executables. Its
selection is controlled by AppLauncher's model argument, not directly by the
marker:

| Model argument | Selected child | `/update/disableEncryptionUpdate` at startup |
|---|---|---|
| exact `-un:1` present | SCOMO | explicitly ignored in recovered MASS_PRODUCT/PENETRATION startup |
| `-un:0` or no `-un:1` | FUMO | changes the FUMO mode byte from `1` to `0` |

AppLauncher attaches its normal global/model argument list even when it creates
app ID 300 dynamically. The recovered embedded NE/EUR row contains `-un:0`, so
that row selects FUMO. This is conditional on the runtime row and installed
binary matching the recovered artifacts.

The FUMO zero-valued mode is logged as `Unencryption Update` and controls many
decryption/archive branches. It is therefore a real plaintext-mode selector on
that route, but it is not accurately called an **unchecked** path. Exact code
does not establish that the marker removes version, model/region, package
signature, payload digest, target, write, slot, boot, or health checks.

The custom-firmware problem therefore has distinct boundaries:

1. **route and encryption mode** — recovered for the outer wrapper and startup
   selectors;
2. **eligibility** — exact version/model/region owner and comparisons remain
   unresolved;
3. **authentication and integrity** — package/payload binding remains
   unresolved;
4. **installation and boot** — inactive-slot writes, slot selection, boot trust,
   userspace health, and mark-good remain separate.

## Format constraints

The vendor archive is old-style tar. The public patcher's own instructions are:

```
tar --format=ustar --numeric-owner -cf - ./ -P | gzip > name_of_output.tar.gz
```

Two details matter and both are easy to get wrong:

- **`--format=ustar`** — the reader rejects pax/GNU extensions;
- **`--numeric-owner`** — ownership must be numeric, not name-resolved.

`tools/uk_fw/rootfs_patch.py` enforces both, stages the tree in a temporary
directory, emits numeric-owner USTAR directly, preserves each retained member's
uid/gid/mode/mtime independently of host ownership, and never modifies the input
package.

## What the tool does

```
python3 tools/uk_fw/rootfs_patch.py list   mango-rootfs.tar.gz
python3 tools/uk_fw/rootfs_patch.py inject mango-rootfs.tar.gz -o out/mango-rootfs.tar.gz \
    --unit-file wideopen.service --unit-name wideopen.service \
    --ssh-key ~/.ssh/id_ed25519.pub
python3 tools/uk_fw/rootfs_patch.py meta   out/mango-rootfs.tar.gz \
    --manifest IONIQ5_EU.ver --write-manifest out/IONIQ5_EU.ver
```

- `list` reports members, modes, ownership and sizes.
- `inject` installs a systemd unit, appends an SSH key to
  `/etc/dropbear/authorized_keys` (creating it mode 0600), optionally installs
  the public-key installer, and copies arbitrary `SRC:DEST` payloads. This does
  **not** create SSH on recovered EU `260128`: that image lacks the server/
  multi-call executable, socket unit, host-key service/key, and enablement. A
  complete independently supplied service chain would be required.
- `meta` computes the rebuilt file's size and **signed CRC-32** and rewrites the
  matching `.ver` record.

The staging boundary is now fail-closed rather than relying on Python's version-
specific `tarfile.extractall()` behavior. Input archives containing absolute or
parent-traversal paths, duplicate regular files, symlinks, hardlinks, FIFOs, or
device nodes are rejected before repacking. Injection destinations receive the
same path validation. Package and manifest outputs must be new paths; existing
outputs, symlink/hard-link aliases, and in-place overwrite of any input are
rejected. This is build-tool safety; it does not make a result installable, select FUMO
on a target, or change the unit's acceptance checks.

Verified end to end on synthetic packages; twelve unit tests cover injection,
key appending with the right mode, manifest rewriting, size reporting, archive
traversal/link/duplicate rejection, injection-destination confinement, hard-link
alias protection, read-only directory handling, numeric ownership/mode/mtime
preservation, and original-input preservation.

## What still has to be true for the result to install

1. The installed AppLauncher/updater route must select FUMO (`-un:0` or no exact
   `-un:1`). Recovered NE/EUR data supports that route, but the owner's installed
   hash and effective arguments are unknown.
2. `/update/disableEncryptionUpdate` must already exist when FUMO starts. Creating
   it requires prior privileged execution and therefore does not solve first
   entry.
3. The package must pass the exact descriptor version/model/region checks. The
   public `>=` description has not yet been bound to the responsible recovered
   function, and reusing a manifest does not prove acceptance.
4. Package and payload authentication/integrity must still pass. The shared
   high-entropy suffix is observed structure, not an established descriptor or
   signature schema; see `evidence/eu-ota-container-structure.md`.
5. Archive extraction, payload writing, target selection, slot selection,
   boot-time trust, userspace health, and mark-good must all succeed.

## Safety

- Public documentation describes an inactive-partition write followed by an
  `/etc/fstab` switch, but that mechanism and its recovery behavior are not yet
  proven for the owner's installed build. Before any bench experiment, capture
  both system partitions, current mount/slot state, boot configuration, and a
  tested console recovery route.
- Do not combine a rootfs edit with a boot-image edit in one experiment.
- Keep the original `mango-rootfs.tar.gz` and `.ver` unmodified as the control.
- No active update experiment is authorized by this build document.

## Honest status

This closes only the archive-construction portion: given a decrypted rootfs, a
modified, correctly formatted rootfs archive can be produced and its manifest
size/CRC values computed. It does not produce a complete authenticated update
package or close route selection, eligibility, authentication, installation,
boot, or health acceptance.

## Side note

The `navi_extended` release binaries are the fastest way to learn the exact
`AppNavi` interface, but GitLab returned HTTP 429 (rate limit) during this
session. Worth retrying later with a lower request rate.

#### From the parallel repository

The parallel lineage describes the `disableEncryptionUpdate` path as an
**unchecked** path and treats the build problem as crypto-plus-acceptance. Its
statement of both update paths, its prerequisites and its safety ordering are
preserved verbatim below.

##### Status and the two update paths (parallel version)

Status: implementation of the documented `disableEncryptionUpdate` path, with the
format constraints taken from the public `update-patcher` README and the
operating model in `evidence/gen5w-public-operating-model.md`. Offline only.

| Path | Payloads | Decryption | Version check |
|---|---|---|---|
| Normal | AES-encrypted envelopes | `DecryptToPipe` on the unit | `.lge.upgrade.xml`, `>=` current |
| Unchecked | **plaintext** | none | `.lge.upgrade.xml`, `>=` current |

The unchecked path is selected by the presence of `/update/disableEncryptionUpdate`
on the unit. It removes the cipher, not the version gate. That is why the
custom-firmware problem decomposes into two independent problems:

1. **crypto** — solved by obtaining the unit's key material, or bypassed entirely
   by the unchecked path;
2. **acceptance** — the version gate plus whatever binds the manifest to the
   payload, which is the part still in question.

<!-- disagreement: the parallel version calls the marker-selected route the "Unchecked" path and says it "removes the cipher, not the version gate", decomposing the problem into (1) crypto and (2) acceptance. The newer text records that the recovered outer AppUpgrade selects FUMO vs SCOMO by AppLauncher's model argument, that the FUMO mode byte is a real plaintext-mode selector on the NE-style `-un:0` route but "is not accurately called an **unchecked** path", and that exact code does not establish that the marker removes version, model/region, package signature, payload digest, target, write, slot, boot or health checks. Both statements are kept. -->

##### Repackaging and tool behaviour (parallel version)

Shared by both lineages: `tools/uk_fw/rootfs_patch.py` enforces
`--format=ustar` plus `--numeric-owner`, stages the tree in a temporary
directory, and never modifies the input package.

- Parallel verification claim (verbatim):

```
Verified end to end on synthetic packages; four unit tests cover injection,
key appending with the right mode, manifest rewriting and size reporting.
```

<!-- disagreement: the parallel version reports four unit tests; the newer text reports twelve, adding archive traversal/link/duplicate rejection, injection-destination confinement, hard-link alias protection, read-only directory handling, numeric ownership/mode/mtime preservation and original-input preservation. Both counts are kept as reported. -->

##### What still has to be true, as written in the parallel version

1. `/update/disableEncryptionUpdate` exists on the unit — this requires code
   execution first, which is the same entry problem as before.
2. The `.lge.upgrade.xml` version is `>=` the installed version. Reusing the
   manifest from the current official package satisfies this if the manifest is
   not bound to the payload contents (see `evidence/community-field-evidence.md`
   for the evidence on both sides of that question).
3. Any package-level descriptor still verifies. The 14,059-byte footer
   (`evidence/eu-ota-container-structure.md`) is the likely binding, and its
   contents are encrypted.
4. The unit's own integrity check of the decrypted payload — unknown.

<!-- disagreement: the parallel prerequisite 3 calls the 14,059-byte footer "the likely binding" whose "contents are encrypted", and prerequisite 2 allows reusing the current official manifest to satisfy the version check. The newer text says the shared high-entropy suffix "is observed structure, not an established descriptor or signature schema", that the public `>=` description has not been bound to a responsible recovered function, and that reusing a manifest does not prove acceptance. Both statements are kept. -->

##### Safety ordering (parallel version)

- Take a full dump of both A/B system partitions first. The update writes to the
  inactive partition and switches `/etc/fstab`, so a rootfs failure is
  recoverable from a console; a boot-image failure is not.

##### Honest status (parallel version)

This closes the *build* half of custom firmware: given a decrypted rootfs, a
modified, correctly formatted package can be produced and its manifest values
computed. It does not close the *acceptance* half, which depends on the footer
descriptor and on the entry precondition.

<!-- disagreement: the parallel status says this "closes the *build* half of custom firmware" and that only "the *acceptance* half" remains, depending on the footer descriptor and the entry precondition. The newer text says it closes "only the archive-construction portion" and enumerates route selection, eligibility, authentication, installation, boot and health as still open. Both statements are kept. -->
