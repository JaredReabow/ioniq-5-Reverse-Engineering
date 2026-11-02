# Intel IPU4 QUERYCAP metadata provenance checkpoint

## Status

Implemented, generated, and focused-validation complete. Exact recovered bytes prove the enabled IPU4 driver's `v4l2_capability.card` is fixed PCI-selected driver identity, not camera media or USB-descriptor content.

## Findings

- Complete `intel_ipu4_isys_vidioc_querycap` range: `0xffffffff81432125..0xffffffff814321cd`, size `0xa8`, SHA-256 `ecdb0fb41f9152ba713928857ca552e9645baaf94be49b20657624d7abae9a35`.
- Querycap copies isys `+0x320` into `card` and isys `+0x368` into `bus_info`.
- Registration producer prefix: `0xffffffff8142b35e..0xffffffff8142b427`, size `0xc9`, SHA-256 `ff54919e0ebea913c993f7ef499a634a1cdd387824aa459f7954d60ddc922193`.
- Registration writes fixed `ipu4/Broxton B` or `ipu5/A` at `+0x320` according to masked PCI device ID `0x1a88`.
- Registration formats `pci:%s` at `+0x368`.
- Camera pixels, sensor-stream metadata, and USB descriptors do not control this exact card field.
- Combined with generic USB V4L not being built, no stock external V4L product-injection route is demonstrated.

## Deliverables

- `tools/uk_fw/ipu4_querycap_provenance.py`;
- `tests/test_ipu4_querycap_provenance.py`;
- `evidence/ipu4-querycap-provenance.md`;
- `evidence/artifacts/udev-candidates/ipu4-querycap-provenance.json`;
- updated transport and primary CVE evidence.

## Artifact identity

- schema `ioniq-ipu4-querycap-provenance/v1`;
- size `3,760` bytes;
- file SHA-256 `f969f811855a28ca2c019837ff7e09956b4963e16b1b83893fb0ea2d22195edc`;
- canonical SHA-256 `e550192a8f6d48267b0931d57267d2bdce236f49b20aab5073570f99c84139dc`.

## Validation

- focused phase scope: `37 passed, 6 subtests passed in 0.64s`;
- exact input identities, symbol boundaries, range hashes, unique instruction patterns, and rodata resolved;
- normal and `PYTHONIOENCODING=utf-16` stdout byte-identical in focused tests;
- canonical: `1062 passed, 352357 subtests passed in 160.02s (0:02:40)`;
- canonical log SHA-256: `53f89ca6c1becfb67d2833037b2535e5e2746a37414c819f69c1ab05dd0036f8`.

## Safety

No kernel, module, VM, device, ioctl, helper, property, unit, network, target executable, root transition, or persistence mechanism was executed.

## Resume action

Audit non-USB SCSI producers that can create an `sd*`, `sr*`, `st*`, or `cciss*` udev event without `ID_SERIAL` and determine whether their `scsi_id` serial data can be externally influenced on the recovered hardware configuration. Confirm all identities on a future disconnected owner bench.
