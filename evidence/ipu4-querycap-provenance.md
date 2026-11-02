# Intel IPU4 QUERYCAP metadata provenance

## Result

The only enabled recovered camera stack does not derive `v4l2_capability.card` from USB descriptors, camera pixels, or sensor-stream metadata. Exact recovered instructions bind the field to one of two fixed driver strings selected by PCI identity:

- `ipu4/Broxton B` when the masked PCI device ID equals `0x1a88`;
- `ipu5/A` otherwise.

Exact `intel_ipu4_isys_vidioc_querycap` then copies that fixed field into `v4l2_capability.card`, which is what `v4l_id` prints as `ID_V4L_PRODUCT`.

Combined with `CONFIG_MEDIA_USB_SUPPORT=n` and the absence of UVC/usbvideo modules, this closes the public advisory's USB-descriptor V4L route for the recovered camera implementation. It does not prove that every hypothetical vendor camera driver is absent from the owner's installed build.

## Exact identities

- recovered `vmlinux`:
  `f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b`;
- recovered kallsyms:
  `2cfba917c1c8e7444e393e8d94ebfe367e2ba348be4f35ce10fbb331822e3c1f`;
- accepted transport report canonical SHA-256:
  `f4e47bae5b167d154905114a6811388a688c7ee868d6642d9a2908053ceef039`.

Tracked output:

- `evidence/artifacts/udev-candidates/ipu4-querycap-provenance.json`;
- schema `ioniq-ipu4-querycap-provenance/v1`;
- size `3,760` bytes;
- file SHA-256 `f969f811855a28ca2c019837ff7e09956b4963e16b1b83893fb0ea2d22195edc`;
- canonical content SHA-256 `e550192a8f6d48267b0931d57267d2bdce236f49b20aab5073570f99c84139dc`.

## Complete querycap function

Kallsyms binds:

- `intel_ipu4_isys_vidioc_querycap`: `0xffffffff81432125`;
- next symbol `fmt_mp_to_sp`: `0xffffffff814321cd`.

The complete `0xa8`-byte function has SHA-256:

`ecdb0fb41f9152ba713928857ca552e9645baaf94be49b20657624d7abae9a35`

Its exact dataflow is:

1. call `video_drvdata`;
2. copy fixed rodata `intel-ipu4-isys` to capability offset `+0x00` (`driver`), bounded to 16 bytes;
3. load the isys pointer from the video object at `+0x7a8`;
4. copy isys `+0x320` to capability `+0x10` (`card`), bounded to 32 bytes;
5. load the same isys pointer;
6. copy isys `+0x368` to capability `+0x30` (`bus_info`), bounded to 32 bytes;
7. set fixed capability bit fields and return zero.

No read from a frame buffer, sensor packet, USB descriptor, userspace argument content, or dynamic string occurs in the complete function.

## Exact card producer

Kallsyms binds `isys_register_devices` at `0xffffffff8142b35e`. The reviewed producer prefix ends at `0xffffffff8142b427`, immediately after the card and bus-info fields are populated. Its `0xc9` bytes have SHA-256:

`ff54919e0ebea913c993f7ef499a634a1cdd387824aa459f7954d60ddc922193`

The producer:

1. points the card destination to isys `+0x320`;
2. chooses default rodata `ipu5/A`;
3. follows the registered PCI device object;
4. reads its 16-bit device ID;
5. masks the reviewed ID bits and compares with `0x1a88`;
6. conditionally selects rodata `ipu4/Broxton B`;
7. calls `strlcpy` into isys `+0x320` with a 32-byte bound;
8. formats isys `+0x368` as `pci:%s` from the PCI device name.

The query consumer and registration producer are linked by the identical isys offsets `+0x320` and `+0x368`. The card selector is hardware PCI identity, not externally supplied camera media.

## Security interpretation

Exact and established:

- generic USB V4L support is not built;
- the IPU4 querycap driver string is fixed;
- the IPU4 card string is selected from two fixed rodata strings by PCI identity;
- the IPU4 bus-info string is a PCI device-name format;
- camera pixels and sensor-stream metadata do not control the reviewed card field;
- the public USB product-string injection route is not an exact stock route through this driver.

Still open:

- another camera driver in a different installed firmware;
- an alternate external transport not represented by the recovered config/module set;
- owner-unit installed identity;
- any end-to-end physical property injection, root transition, or persistence.

The vulnerable standalone `v4l_id` helper remains present and pre-fix. This result is a reachability correction: the enabled exact producer does not supply attacker-controlled card text.

## Tooling

`tools/uk_fw/ipu4_querycap_provenance.py` uses stable no-follow reads, exact input hashes, exact kallsyms boundaries, complete range hashes, unique critical instruction patterns, virtual-address string resolution, strict transport-report digest validation, and deterministic exclusive JSON output. It does not run a kernel, module, ioctl, helper, VM, device, or target executable.
