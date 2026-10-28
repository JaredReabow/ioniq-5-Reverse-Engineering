# Official European package acquisition state

The Navigation Updater selected IONIQ 5 model code `101489` and package
`NE_E.EUR.S5W_L.001.001.260128` into the local `IONIQ5_EU` cache.

At the first verified checkpoint, 17 of 35 payloads were complete and all 17
recomputed signed CRC-32 values matched. The European map was partial at
10,001,005,399 of 17,916,293,755 bytes. Parts `.z01` through `.z964` existed;
`.z935` onward contained interrupted concurrent writes.

The repaired updater was subsequently registered and launched through macOS
LaunchServices. It reused `/Users/researcher/Downloads/NaU/IONIQ5_EU`, rewrote the
interrupted segment range, and produced new parts through at least `.z975`.
That is direct filesystem proof of a resumed download rather than a fresh or
wrong-region selection.

The download subsequently completed. All 35 payloads now match their declared
sizes and signed CRC-32 values. The 17,916,293,755-byte European map matches
its supplied MD5 `6eec3dd58295b1e94aafe65f9c0ee14b`; the `vrau` and
`vreu` fixed voice archives match their supplied MD5 values
`8fa479c97e752b43c907c7838a7856ed` and
`6303095ad812cef04e245a5d0aa9ac08` respectively. The complete SHA-256
inventory contains the 35 payloads plus `IONIQ5_EU.ver`; its sorted inventory
digest is `f06752ea7cbf296ef7d7d7482f5ba96a3349161fc7ad0d60b36b042f62ef5b51`.

The completed package contains 25,224,055,331 declared payload bytes. The
newly arrived `mango-rootfs.tar.gz`, `appnavi.tar`, `new_gui.tar.gz`,
`.lge.upgrade.xml`, and `.whatsnew.tar.gz` remain opaque encrypted envelopes:
their filenames do not describe directly extractable tar, gzip, XML or ELF
bytes at offset zero. Completion removes the acquisition blocker but does not
provide the device-derived decryption material required by published Gen5W_L
post-entry tooling. No update medium or vehicle operation was used.

Direct signature parsing found all 16,377 executable pages correct and the CMS
cdhash attributes consistent. The earlier local failure was a LaunchServices
registration problem, not evidence that the completed payloads were corrupt.
