# Community field evidence: downgrade, CRC patching, and API availability

Status: review of the public issue trackers of the Gen5 Wide-Open projects
(`gitlab.com/g4933/gen5w/*`) plus direct availability probes. This is anecdotal
evidence from third parties, not controlled testing. It is recorded because it
constrains the plan and, in one case, weakens a hypothesis of this programme.

## 1. Downgrade is unsolved in public

`navi_extended` issue **#2, "[Question] How do I downgrade?"** (2022-10-30,
still open, no answer):

> "I tried modifying `update.info` and things but it didn't work. also, I don't
> see the `.lge.update` thing. My car is a Korean variant."

Consequences:

- The documented "downgrade your HU" remedy in the `navi_extended` README has no
  published procedure that the community has confirmed.
- Editing `update.info` was attempted and failed.
- The `>=` version check therefore appears to be doing its job.

This does not prove downgrade is impossible; it proves nobody has published a
working, confirmed method.

## 2. Correcting the `.ver` CRC and size is not sufficient

`navi_extended` issue **#3, "gen5w standard (Ev6) update_info"** (2023-09-23,
open):

> "I have been updating the 2022_EV6_USA.ver file with the updated CRC and file
> size and still will not install."

This is the most useful single data point in the tracker. It is a direct field
attempt at exactly the attack that `tools/uk_fw/crc32_forge.py` makes possible:
change content, repair the manifest's size and CRC-32, install.

It failed. So in practice the upgrader is **not** gated on the `.ver` CRC alone.
Something else — a signature over the descriptor or the package, or an integrity
check inside the encrypted container — rejects the modified package.

**Effect on our hypothesis.** `evidence/eu-ota-container-structure.md` recorded
that CRC-32 is forgeable, and that *if* the upgrader relied on those values, a
modified payload would pass. The arithmetic part stands: CRC-32 is not an
integrity control. The exploitable part is now **weakened by field evidence** and
should be treated as unlikely on its own. Note also that the signing subject may
be the Android/EV6 variant rather than this Linux unit, so it constrains the
hypothesis without closing it.

## 3. Newer packages changed filenames but not procedure

`navi_extended` issue **#4, "new firmware, new filename"** (2024-08-29):

> "…is not a .tar.gz, it's just a `appnavi.tar` … It's the same procedure?"

Confirmed in our own package: EU `260128` ships `HU/images/navi_eu/appnavi.tar`,
not `appnavi.tar.gz`. The toolchain's assumption of a `.tar.gz` name is stale;
the container type is the one that matters. Any script that globs for
`appnavi.tar.gz` will silently do nothing on a 2026 package.

## 4. The update API is unavailable

- Direct probe of `https://apieu.map-care.com/api/ChkRegistV2` and
  `https://api.map-care.com/api/ChkRegistV2` with a locally generated token
  (the scheme the public tool uses) returns **HTTP 503**.
- `http://oem-euupload.map-care.com/EU_update_data/EU_INF/` returns 404, and the
  HTTPS variant fails to connect.
- `update_fetcher` issues **#1** and **#2** (2023-11-15) both report *"there is
  no cars available on any region"*.

Consequences:

- `update_fetcher` and `nudl` may not currently be able to enumerate or download
  older builds from this network. The downgrade path loses its feedstock if that
  holds generally.
- The official Navigation Updater (which we already used successfully to fetch
  `260128`) remains the working acquisition route, and it fetched the current
  build — not necessarily an older one.

## 5. What this changes

| Question | Previous status | Now |
|---|---|---|
| Can the unit be downgraded? | Documented remedy, unverified | **No published confirmed method**; `update.info` edits failed |
| Is the `.ver` CRC the integrity gate? | Plausible weakness | **Weakened** — a field attempt with repaired CRC+size was rejected |
| Can older builds be fetched? | Assumed available | **At risk** — API returns 503 and has done so since 2023 per reports |
| Does `appnavi.tar` change the procedure? | Unknown | Same procedure, different filename (confirmed in our package) |

## 6. The gate is still the gate

None of this opens the unit. It narrows the search:

1. The entry remains "code execution on an unpatched build", and the build
   cannot currently be downgraded by any published method.
2. The integrity gate is stronger than the `.ver` CRC, so the interesting target
   is the **footer descriptor** and the upgrader's own checks — both encrypted.
3. The most promising pre-auth surface is unchanged: the filesystem and archive
   parsers consumed before any signature check.

## 7. Next evidence

- On the bench, capture the exact rejection message when a CRC-repaired package is
  offered. The wording identifies which check failed.
- Determine whether the unit's own Navigation Updater can request an older build
  for model `101489`; the server-side history may differ from what the public API
  exposes.
- Read the `.lge.upgrade.xml` plaintext (needs the key) to see whether it carries
  per-file digests in addition to the version.

## Sources

- `https://gitlab.com/g4933/gen5w/navi_extended/-/issues/2`, `/3`, `/4`
- `https://gitlab.com/g4933/gen5w/update_fetcher/-/issues/1`, `/2`
- Direct HTTP probes, 2026-10-19
