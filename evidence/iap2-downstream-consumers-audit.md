# iAP2 Downstream Consumer Audit — Exact Evidence

**Schema**: `ioniq-iap2-downstream-consumers-audit/v1`
**Tool Version**: `1.0.0`
**Artifact**: `evidence/artifacts/projection-candidates/iap2-downstream-consumers-audit.json`
**Artifact SHA-256**: `6981a834f27644216b36c7db8bbc9b517bf9b16b85a06621eaabca4eada4b7cf`

## Binary Identities

- **iAP2Service-2.0**: 633216 bytes, SHA-256 `38419131df82ec7e3c3b29a68ecc1a078c7f0b403051f137fe9f46f82b99f26e`, Build ID `2c720231c0b44bb049bee87feb3531077bd86154`
- **libiAP2AppFramework-2.0.so**: 190272 bytes, SHA-256 `d4d0558c9c53f02ee14024c081ccd83a02ca29404ef400131e2951f68a388120`, Build ID `b6a6e2f2879ada6ea7e5d329d33c3c731cf365a6`

## Transaction-Tail Over-Read (Root Cause)

- **Initializer**: `iAp2MarshalInitFromTxn` at `0x210ff..0x21175`
- **Overstatement Anchor**: `0x21126..0x2115e` — `remaining = *(uint32_t*)(txn + 0x38)` (total size, not payload size); **no `remaining -= 0x40`**
- **Overstatement**: **64 bytes** — marshal state allows reads 64 bytes past true allocation end
- **Accessor**: `iAp2MarshalGetBytes` at `0x21a56..0x21b21` — bounds check at `0x216ab` uses overstated `remaining`
- **Impact**: Accessor returns interior pointer up to 64 bytes past allocation; NULL returned only when request exceeds overstated remaining

## 31 Direct Call Sites + 22 Wrapper Calls

| Caller | Direct Calls | Wrapper Calls | Total | Immediate Sink Class |
|--------|-------------|---------------|-------|---------------------|
| SessionAppLaunch | 1 | 0 | 1 | CRITICAL: log("%s", ptr) (CWE-134) |
| SessionBTConnection | 2 | 0 | 2 | ParamListBuilder → IPC marshalling chain |
| SessionCommunications | 6 | 0 | 6 | ParamListBuilder → IPC marshalling chain |
| SessionConnection | 0 | 15 | 15 | various |
| SessionExternalAccessoryProtocol | 1 | 0 | 1 | ParamListBuilder → IPC marshalling chain |
| SessionHID | 2 | 0 | 2 | ParamListBuilder → IPC marshalling chain |
| SessionIdentification | 0 | 7 | 7 | various |
| SessionLocation | 7 | 0 | 7 | ParamListBuilder → IPC marshalling chain |
| SessionMediaLibraryUpdates | 3 | 0 | 3 | ParamListBuilder → IPC marshalling chain |
| SessionPlayMediaLibrary | 5 | 0 | 5 | ParamListBuilder → IPC marshalling chain |
| SessionVoiceOver | 1 | 0 | 1 | ParamListBuilder → IPC marshalling chain |
| SessionWiFiInformation | 2 | 0 | 2 | ParamListBuilder → IPC marshalling chain |
| heap_string_materializer | 1 | 0 | 1 | CRITICAL: strncpy (CWE-476, CWE-125) |

## Exploitable Primitives (Exact-Static Candidates)

### Primitive 1: Null-source strncpy DoS (CWE-476): GetBytes returns NULL, len>0 passed to strncpy
- **Source Callers**: heap_string_materializer
- **Sink Classes**: CWE-476:null-source-strncpy-DoS

### Primitive 2: Over-read disclosure (CWE-125): GetBytes returns ptr into 64-byte over-read region, strncpy copies it to heap, later %s discloses
- **Source Callers**: heap_string_materializer
- **Sink Classes**: CWE-476:null-source-strncpy-DoS

### Primitive 3: Over-read/NULL pointer propagated to IPC marshalling chain via SessionBTConnection param list builder
- **Source Callers**: SessionBTConnection
- **Sink Classes**: param-list-builder

### Primitive 4: Over-read/NULL pointer propagated to IPC marshalling chain via SessionLocation param list builder
- **Source Callers**: SessionLocation
- **Sink Classes**: param-list-builder

### Primitive 5: Format-string disclosure/null-crash (CWE-134): log("%s", ptr) where ptr is over-read or NULL
- **Source Callers**: SessionAppLaunch
- **Sink Classes**: CWE-134:format-string-disclosure-null-crash

### Primitive 6: Over-read/NULL pointer propagated to IPC marshalling chain via SessionExternalAccessoryProtocol param list builder
- **Source Callers**: SessionExternalAccessoryProtocol
- **Sink Classes**: param-list-builder

### Primitive 7: Over-read/NULL pointer propagated to IPC marshalling chain via SessionHID param list builder
- **Source Callers**: SessionHID
- **Sink Classes**: param-list-builder

### Primitive 8: Over-read/NULL pointer propagated to IPC marshalling chain via SessionMediaLibraryUpdates param list builder
- **Source Callers**: SessionMediaLibraryUpdates
- **Sink Classes**: param-list-builder

### Primitive 9: Over-read/NULL pointer propagated to IPC marshalling chain via SessionVoiceOver param list builder
- **Source Callers**: SessionVoiceOver
- **Sink Classes**: param-list-builder

### Primitive 10: Over-read/NULL pointer propagated to IPC marshalling chain via SessionWiFiInformation param list builder
- **Source Callers**: SessionWiFiInformation
- **Sink Classes**: param-list-builder

### Primitive 11: Over-read/NULL pointer propagated to IPC marshalling chain via SessionPlayMediaLibrary param list builder
- **Source Callers**: SessionPlayMediaLibrary
- **Sink Classes**: param-list-builder

### Primitive 12: Over-read/NULL pointer propagated to IPC marshalling chain via SessionCommunications param list builder
- **Source Callers**: SessionCommunications
- **Sink Classes**: param-list-builder

### Primitive 13: Null-source strncpy DoS (CWE-476)
- **Source Callers**: SessionConnection
- **Sink Classes**: CWE-476:null-source-strncpy-DoS, CWE-125:overread-disclosure-via-strncpy

### Primitive 14: Over-read disclosure via strncpy + later %s logging (CWE-125)
- **Source Callers**: SessionConnection
- **Sink Classes**: CWE-476:null-source-strncpy-DoS, CWE-125:overread-disclosure-via-strncpy

## Transaction Construction for Trigger

Service receiver framing (`0x2dadd..0x2df7b`):
1. `recv(fd, stack_hdr, 64, MSG_WAITALL)` — accepts any positive return
2. `declared_total = stack_hdr[0x38]` (uint32)
3. `malloc(declared_total)` — attacker controls allocation size
4. **64-byte header copy BEFORE `declared_total <= 64` check** (CWE-787, CWE-457, CWE-400)
5. `recv(fd, alloc+0x40, declared_total-64, MSG_WAITALL)` — body receive
6. `handleClientCmd(alloc)` — dispatches to command handlers

**Over-read trigger condition**:
- Marshaled string field at parse offset `p` declares length `L`
- True payload capacity: `declared_total - 64` bytes
- Accessor permits read if `p + L <= declared_total` (overstated bound)
- True bound: `p + L <= declared_total - 64`
- **Over-read window**: `declared_total - 64 < p + L <= declared_total`
- Request `L` in this window → `GetBytes` returns pointer into over-read region

**Null-source trigger**: `p + L > declared_total` → `GetBytes` returns NULL, but caller uses declared length

## Validation

- Total direct calls: **31** (expected 31)
- Total wrapper calls: **22** (expected 22)
- Total traces: **53**
- Critical sinks (CWE-476, CWE-125, CWE-134): **24**
- IPC marshalling chain sinks: **0**

## Boundaries & Limitations

- **Exact-static only**: No live delivery, no runtime admission, no phone-to-handler reachability proven
- **Over-read disclosure**: Requires heap adjacency with sensitive data; allocator behavior not modeled
- **Null-source DoS**: Requires UID-0 service restart policy to be impactful
- **IPC chain**: Downstream marshalling may validate/limit; not fully traced to final `send()`
- **No CVE attribution**: These are exact-static candidates; CVE identity requires runtime exploitability proof

## Artifacts

- JSON: `evidence/artifacts/projection-candidates/iap2-downstream-consumers-audit.json` (SHA-256: `6981a834f27644216b36c7db8bbc9b517bf9b16b85a06621eaabca4eada4b7cf`)
- This markdown: `evidence/iap2-downstream-consumers-audit.md`
- Decompiled callers: `work/iap2-marshal-callers-20261112/decompiled/` (11 files)
- Decompiled downstream: `work/iap2-downstream-consumers-20261113/`
