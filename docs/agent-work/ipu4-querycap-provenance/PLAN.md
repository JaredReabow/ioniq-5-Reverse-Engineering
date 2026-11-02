# Intel IPU4 QUERYCAP metadata provenance

## Objective

Trace the exact producer consumed by recovered `intel_ipu4_isys_vidioc_querycap` for `v4l2_capability.card`. Determine whether camera pixels, sensor metadata, a USB descriptor, or fixed PCI-driver identity supplies the `v4l_id` product string on the only enabled recovered camera stack.

## Inputs

- hash-bound recovered `vmlinux`;
- hash-bound recovered kallsyms table;
- accepted deterministic CVE-2026-40225 transport report.

## Method

Build a deterministic host-only reviewer that:

1. validates exact file identities and kallsyms addresses/boundaries;
2. extracts the complete querycap function and bounded registration producer prefix;
3. verifies exact range hashes and critical instruction encodings;
4. resolves referenced rodata strings by virtual address;
5. binds querycap's card copy from object offset `+0x320` to registration's write at the same offset;
6. binds the only two source strings and the PCI-ID conditional selecting them;
7. binds bus-info separately to `pci:%s` and driver to `intel-ipu4-isys`;
8. combines this with the accepted absence of generic USB V4L support.

## Safety

No kernel, module, device, ioctl, helper, VM, network, descriptor, injected property, or target executable is run. The tool only reads and hashes local files with stable no-follow descriptors.

## Acceptance

- Exact bytes prove the IPU4 card field is selected from fixed driver strings by PCI identity.
- Pixels, sensor stream data, and USB descriptors are not claimed to control the card field.
- Generic USB V4L remains separately not built.
- The output distinguishes closure of the public USB-V4L transport from unknown vendor/internal alternatives.
- Focused and canonical tests pass.

## Routing

The installed Fable route remains unavailable for native v2 subagents. No substitute provider or paid-route probe is permitted; Astra handles this host-only static phase.
