# Custom firmware build path: repacking the rootfs

Status: implementation of the documented `disableEncryptionUpdate` path, with the
format constraints taken from the public `update-patcher` README and the
operating model in `evidence/gen5w-public-operating-model.md`. Offline only.

## The two update paths

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

## Format constraints

The vendor archive is old-style tar. The public patcher's own instructions are:

```
tar --format=ustar --numeric-owner -cf - ./ -P | gzip > name_of_output.tar.gz
```

Two details matter and both are easy to get wrong:

- **`--format=ustar`** — the reader rejects pax/GNU extensions;
- **`--numeric-owner`** — ownership must be numeric, not name-resolved.

`tools/uk_fw/rootfs_patch.py` enforces both, stages the tree in a temporary
directory, and never modifies the input package.

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
  the public-key installer, and copies arbitrary `SRC:DEST` payloads.
- `meta` computes the rebuilt file's size and **signed CRC-32** and rewrites the
  matching `.ver` record.

Verified end to end on synthetic packages; four unit tests cover injection,
key appending with the right mode, manifest rewriting and size reporting.

## What still has to be true for the result to install

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

## Safety

- Take a full dump of both A/B system partitions first. The update writes to the
  inactive partition and switches `/etc/fstab`, so a rootfs failure is
  recoverable from a console; a boot-image failure is not.
- Do not combine a rootfs edit with a boot-image edit in one experiment.
- Keep the original `mango-rootfs.tar.gz` and `.ver` unmodified as the control.

## Honest status

This closes the *build* half of custom firmware: given a decrypted rootfs, a
modified, correctly formatted package can be produced and its manifest values
computed. It does not close the *acceptance* half, which depends on the footer
descriptor and on the entry precondition.

## Side note

The `navi_extended` release binaries are the fastest way to learn the exact
`AppNavi` interface, but GitLab returned HTTP 429 (rate limit) during this
session. Worth retrying later with a lower request rate.
