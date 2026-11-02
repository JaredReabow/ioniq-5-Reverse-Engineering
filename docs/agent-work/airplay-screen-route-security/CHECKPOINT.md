# AirPlay screen route security checkpoint

Status: implementation, exact-static analysis, and validation complete.

## Bound results

- Screen stream type `0x6e` and a nonzero `streamConnectionID` select the
  recovered screen setup branch.
- Pair verify selects a 32-byte stream key and ChaCha20-Poly1305; the tag is
  verified before parser dispatch.
- Null pair verify derives an AES-CTR screen key from the 16-byte session base
  key and stream connection ID; no body authentication check appears in that
  branch before parser dispatch.
- A fresh session explicitly zeros the base key at `+0x260`.
- Missing encryption type and comparative None value `0x01` reach session setup
  without calling the base-key setter.
- The screen branch does not test the base-key initialized marker before using
  `+0x260`. This is an exact-static no-MFi fallback candidate for a fresh
  missing/None session, not proof of upstream authorization or delivery.
- The secondary TCP listener binds wildcard addresses, may fall back from
  preferred port 6030 to a dynamic port, and advertises `dataPort` in the setup
  response.
- The screen-thread accept call requests no peer address and gives the accepted
  socket to `AirPlayReceiverSessionScreen_ProcessFrames`.

## Deliverables

- `tools/uk_fw/airplay_screen_route_security_audit.py`
- `tests/test_airplay_screen_route_security_audit.py`
- `evidence/airplay-screen-route-security.md`
- `evidence/artifacts/projection-candidates/airplay-screen-route-security.json`

## Artifact

- schema: `ioniq-airplay-screen-route-security-audit/v1`
- size: 16,458 bytes
- file SHA-256: `aae4dcec49e0e0a36c86f34cb721cf1f97e4883b656bf2ec5c36ce5fb4433166`
- canonical SHA-256: `9e69506830676153ca09737ae86cc28ce88cf4db151e953fa5a57683419cb447`

## Validation

- focused route tests: 5 passed;
- projection-focused tests: 20 passed;
- canonical suite: 1,090 passed and 352,357 subtests passed in 161.57 s;
- canonical log SHA-256:
  `41633edf1836def9551a721507935e2bd2ac60330241a0aeb130e15b1e2d946a`;
- `py_compile`, deterministic reproduction, exclusive no-overwrite behavior,
  strict ASCII JSON decode, and path-limited `git diff --check` passed.

## Boundaries

No recovered target code ran and no protocol input was created. Upstream
authorization, live setup/session start, listener/interface exposure, port
discovery, socket delivery, process behavior, exploitation, root, persistence,
CVE identity, and installed-unit applicability remain unproved.
