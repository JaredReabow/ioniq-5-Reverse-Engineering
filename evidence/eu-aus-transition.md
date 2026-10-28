# European-to-Australian package comparison and transition feasibility

The vehicle-correct source package is European
`NE_E.EUR.S5W_L.001.001.260128`. The Australian comparison package is
`NE_E.AUS.S5W_L.001.001.260319`. The latter is comparison evidence, not a
vehicle-approved conversion package.

## Complete byte comparison

Each package contains 36 files. Thirty-two relative paths are common without
normalising the four region-specific paths:

- Six are byte-identical: the front-key checksum, both front-key binaries,
  `mustwithcopy`, and the `vrau` and `vreu` fixed voice archives.
- Nineteen have equal size but different SHA-256 values. This set includes all
  twelve `iasImage*` variants, showing that equal layout does not mean equal
  signed boot content.
- Seven differ in both size and bytes: `.lge.upgrade.xml`,
  `.whatsnew.tar.gz`, `AppUpgrade`, `update.tar.gz`,
  `mango-rootfs.tar.gz`, `mango-rwdata.tar.gz`, and `new_gui.tar.gz`.
- Four paths exist only in each region-specific set, covering the manifest,
  regional map, map sidecar and AppNavi path.

The European declared payload total is 25,224,055,331 bytes. Most of the gross
EU/AUS size difference is map data, but functional differences are plainly not
confined to maps.

The matching `iasImage_1280_sub` targets confirm a common platform. Both
recover as ELF64 x86-64 Linux `4.1.27-abl`, and their extracted kernel
configuration SHA-256 is the same:
`987268a1a4b333d67c219c63b690c3828811136a7a3b203eb6f20552e82dad56`.
Their kernel and signed-container bytes differ. The EU kernel was built on
28 January 2026; the AUS kernel was built on 19 March 2026. Common architecture
and hardening posture therefore do not establish artifact interchangeability.

The complete 32-row common-path SHA-256 matrix and both four-path region-only
sets are preserved in
`evidence/eu-package-metadata/eu-aus-comparison.json`. The read-only generator
is `tools/uk_fw/compare_eu_aus.py`; corresponding kernel metadata is reproduced
with `tools/uk_fw/inspect_ipk_kernel.py`.

## Feasibility decision

The shared `NE_E` and `S5W_L` identifiers establish a common broad head-unit
family. They do not prove cross-region install compatibility. Differences in
the updater, rootfs/rwdata, AppNavi, modem envelopes and kernel containers show
that an Australian package cannot be treated as a map-only substitution.

A region transition remains unproven until all of the following are resolved:

1. exact head-unit part number, board revision and bootloader policy;
2. complete EU/AUS payload hashes and decrypted component comparison;
3. update signature, version and region enforcement, including the kernel LG
   keystore and OEM-key usage policy;
4. modem, carrier, radio and telematics provisioning dependencies;
5. navigation licensing, map and AppNavi coupling;
6. recoverable stock restore and dealer recovery routes; and
7. isolated bench validation before any vehicle use.

No media creation, cross-region installation or vehicle action is authorised by
this comparison.
