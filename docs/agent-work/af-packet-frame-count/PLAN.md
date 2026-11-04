# AF_PACKET frame-count residual audit plan

## Objective

Resolve the remaining static-analysis gap around the absent upstream
`frames_per_block > UINT_MAX / tp_block_nr` guard in the exact recovered
`af_packet.ko`. Determine whether an accepted wrapped `tp_frame_nr` can make
TPACKET_V1/V2 allocation, frame lookup, progression, polling, transmit, receive,
or mmap consumers address outside the allocated ring.

## Non-goals and safety boundary

- No packet socket, ring, namespace, capability, packet, mmap, allocation-pressure,
  race, crash, or target execution.
- No trigger values, exploit procedure, heap grooming, payload, shellcode, or
  privilege-transition code.
- Do not infer installed-device reachability, `CAP_NET_RAW`, root, SMACK escape,
  or persistence from static arithmetic.
- Keep full downloaded source and generated work under ignored `work/`; track only
  reviewed excerpts, deterministic numeric/Boolean models, tests, and evidence.

## Exact artifact

- `/lib/modules/4.1.27-abl/kernel/net/packet/af_packet.ko`
- SHA-256 `c810265b3c22f95d2b90494cc206abd6b4e67b7710bff2adcb177ee4867f467b`
- Required exact functions: `packet_set_ring`, `packet_lookup_frame`,
  `packet_mmap`, and the V1/V2 frame-progression consumers in `tpacket_rcv` and
  transmit/poll paths where relevant.

## Proof obligations

Let `F = floor(tp_block_size / tp_frame_size)`, `N = tp_block_nr`,
`R = (F*N) mod 2^32`, and let accepted positions be bounded by stored
`frame_max = R-1` with unsigned wrap.

1. Confirm exact field bindings and 32-bit multiplication/equality in
   `packet_set_ring`, followed by allocation by `N` blocks and storage of `R-1`.
2. Confirm allocation vector length, per-block size/order, cleanup, and successful
   allocation requirements; do not treat allocation attempt as success.
3. Trace every V1/V2 consumer of `head`, `frame_max`, `frames_per_block`,
   `frame_size`, `pg_vec`, `pg_vec_len`, and `pg_vec_pages` that can affect an
   address or mapping.
4. Prove or disprove for every accepted logical position `p`:
   - `floor(p/F) < N` (block index in range), and
   - `(p mod F) * frame_size < tp_block_size` (offset in block).
   Cover `R=0`/`frame_max=UINT_MAX` explicitly rather than excluding it.
5. Analyze mmap expected-size arithmetic separately. Distinguish arithmetic wrap,
   VMA-size mismatch, `vm_insert_page` rejection, partial mapping cleanup,
   resource exhaustion, and an actual out-of-VMA or out-of-vector access.
6. Distinguish TPACKET_V1/V2 from V3. The V3 block path cannot be used to hide
   an unresolved V1/V2 consequence.
7. Compare exact effects with upstream commits
   `8f8d28e4d6d815a391285e121c3a53a0b6cb9e7b` and
   `fc62814d690cf62189854464f4bd07457d5e9e50` without treating commit intent as
   standalone impact proof.

## Deliverables

- Complete or branch-complete retained disassembly covering the affected producer
  and all address-sensitive V1/V2 consumers.
- `evidence/vendor-kernel-af-packet-frame-count.md` with exact addresses, field
  bindings, proof/counterexample reasoning, and narrow classification.
- `tools/uk_fw/af_packet_frame_geometry_model.py`: bounded, deterministic,
  non-operational arithmetic classifier. It must emit no socket parameters,
  packet material, command, target path, race schedule, or trigger recipe.
- `tests/test_af_packet_frame_geometry_model.py` with boundary/property coverage,
  including zero wrapped count and fail-closed CLI validation.
- Update only directly related indexes, handover, vulnerability summary, and
  changelog after independent acceptance.

## Acceptance criteria

- Machine-code claims cite exact instructions and relocations where needed.
- The arithmetic model uses explicit 32-bit semantics and independently checks
  index and offset bounds; it does not claim binary verification.
- Every security classification separates accepted configuration, successful
  allocation, successful mmap, OOB access, corruption, privilege transition,
  root, and persistence.
- Focused and complete tests pass with `python3`.
- Independent semantic/model review returns ACCEPT.
