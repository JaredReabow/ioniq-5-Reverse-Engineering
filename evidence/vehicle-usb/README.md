# Owner USB log findings (sanitized)

A local USB diagnostic export from the owner's UK-origin 2021 IONIQ 5 was inspected on 2026-10-27. The raw exports, full manifests, compressed core dumps, traces, and driving and location logs are retained outside this public repository.

The export reported installed infotainment software `NE_E.EUR.S5W_L.001.001.250604` and head-unit model `NEAE.S5BLC.AEU`. The `AppUpgrade` record showed an earlier transition from `250226` to `250604`. No non-infotainment ECU version was established.

Hyundai's [official EU software-version table](https://update.hyundai.com/EU/EN/updateNoticeView/software-version) lists the model in the Standard Gen5W European release family for `NE_E.EUR.S5W_L.001.001.260128`. The package relation is a research finding; no vehicle installation or acceptance test was performed.

The owner reported that engineering code `19480717` opened a menu, but the menu identity was not captured.

The original raw files are intentionally absent from the public Git tree and reachable commit history. A former GitHub import commit may remain in GitHub caches until GitHub Support completes server-side cleanup.
