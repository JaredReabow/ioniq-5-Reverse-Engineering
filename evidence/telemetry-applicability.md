# Telemetry applicability assessment

Date assessed: 2026-10-21

Scope: IONIQ 5 repository at `/Users/researcher/Documents/ChatGPT/reverse engineering/ioniq research`

Outcome: **not applicable — no owned distributable companion application exists in this repository**

## Decision

Do not add telemetry, crash reporting, an install identifier, a network sender,
or a consent interface to this repository. The repository is an internal
research workspace, not a consumer application. Adding a producer here would
create collection where none is needed and would not satisfy the instruction to
instrument actual owned distributable applications.

This assessment does not classify Hyundai's Navigation Updater, Bluelink, or
software recovered from official firmware as project-owned applications. They
are vendor software and are evidence or analysis targets only.

## Source inventory

The repository was searched for common application and packaging roots,
including:

- Apple projects and bundles: `*.xcodeproj`, `*.xcworkspace`, `Info.plist`;
- Android applications: `AndroidManifest.xml`, Gradle application projects;
- JavaScript/Electron applications: `package.json`;
- Flutter applications: `pubspec.yaml`;
- Rust and .NET applications: `Cargo.toml`, `*.csproj`, `*.sln`;
- application identifiers, store metadata, privacy manifests, telemetry
  producers, crash reporters, analytics SDKs, and companion-app references.

No owned app project, app target, store package, privacy manifest, telemetry
producer, analytics SDK, or crash-reporting integration was found.

The owned executable material consists of Python research tools under
`tools/uk_fw/**` and their local tests under `tests/**`. Those utilities perform
offline package inspection, comparison, emulation support, evidence generation,
and harness validation. They are not distributed through an application store
and are not a consumer-facing companion app.

Other repository content consists of research evidence, Council review
packages, ledgers, exported tables, and local analysis workspaces. Firmware and
official Hyundai application references are analysis inputs, not owned
products.

## Shared-service contract reviewed

The shared contract and per-app handoff were reviewed from:

- `/Users/researcher/Documents/LEOVPS/TELEMETRY.md`;
- `/Users/researcher/Documents/LEOVPS/TELEMETRY-COVERAGE.md`;
- `/Users/researcher/Documents/LEOVPS/telemetry/adapters/HANDOFFS.md`.

The contract supports schema-2 pings and fingerprint-only crashes, requires an
explicit app identity and consent state, excludes crash messages, stacks,
paths, breadcrumbs, vehicle identifiers and user content, and requires bounded
best-effort delivery. Its presence does not create a reason to instrument a
non-app research repository.

The live service documentation also states that public crash intake is
withdrawn and `/crash` is loopback-only. Therefore even a future app adapter
must remain disabled until an approved operational intake and its release
privacy gates exist.

## Store-policy boundary

Current official policy was checked on 2026-10-21:

- Apple App Review Guidelines 5.1.1 require a privacy policy identifying data
  collection and uses, consent for user or usage-data collection, an accessible
  withdrawal mechanism, and data minimisation. Apple also makes the developer
  responsible for analytics services and third-party SDKs.
- Google Play's User Data policy requires transparent disclosure of collection,
  use, handling and sharing, accurate Data safety declarations, and compliance
  by included SDKs. Google Play prohibits combining persistent device
  identifiers with sensitive data outside narrow exceptions.

Sources:

- <https://developer.apple.com/app-store/review/guidelines/>
- <https://support.google.com/googleplay/android-developer/answer/10144311>
- <https://support.google.com/googleplay/android-developer/answer/18258653>

These policies do not require creating telemetry for a project that has no
distributable app. They define release obligations if such an app is later
created.

## Future trigger and minimum acceptance gates

Reassess this decision only if an owned distributable IONIQ companion app is
added. Before enabling any collection, that app must have all of the following:

1. a fixed, reviewed app identifier and an approved operational endpoint;
2. explicit opt-in consent, default off, with an accessible revocation control;
3. fingerprint-only crash reports with no message, stack, path, breadcrumb,
   VIN, location, diagnostic data, bus capture, firmware data, vehicle content,
   user content, credentials, or other free text;
4. minimal, purpose-bound usage counters rather than raw events;
5. privacy policy, store declarations and platform privacy manifests that match
   actual behaviour;
6. disabled-state, revocation, redaction, bounded-queue, offline and failure
   tests proving that disabled collection sends nothing;
7. a synthetic end-to-end receipt only after intake is specifically authorised.

Until all gates are met, collection remains absent and disabled. A shared
secret embedded in a public client must not be represented as an anti-forgery
or authentication guarantee.

## Excluded actions

This assessment made no vehicle connection, boot, diagnostic request, firmware
change, flash, USB write, VIN lookup, location collection, vehicle-content
collection, endpoint deployment, credential change, store submission, or
external release.
