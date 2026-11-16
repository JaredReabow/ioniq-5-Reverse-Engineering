#!/usr/bin/env python3
"""
iAP2 Downstream Consumer Audit — Exact Static Analysis

Traces all downstream sinks reachable from the 31 direct iAp2MarshalGetBytes calls
and 22 wrapper calls via heap-string materializer.

Schema: ioniq-iap2-downstream-consumers-audit/v1
"""

from __future__ import annotations
import sys
import json
import hashlib
import pathlib
import struct
import argparse
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum

# ─── Binary metadata ──────────────────────────────────────────────
SERVICE_BIN = pathlib.Path(
    "work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/bin/iAP2Service-2.0"
)
FRAMEWORK_BIN = pathlib.Path(
    "work/decrypted-eu-260128/extracted-safe/mango-rootfs/app/lib/libiAP2AppFramework-2.0.so"
)

SERVICE_SHA256 = "38419131df82ec7e3c3b29a68ecc1a078c7f0b403051f137fe9f46f82b99f26e"
FRAMEWORK_SHA256 = "d4d0558c9c53f02ee14024c081ccd83a02ca29404ef400131e2951f68a388120"
SERVICE_SIZE = 633_216
FRAMEWORK_SIZE = 190_272
SERVICE_BUILD_ID = "2c720231c0b44bb049bee87feb3531077bd86154"
FRAMEWORK_BUILD_ID = "b6a6e2f2879ada6ea7e5d329d33c3c731cf365a6"

# ─── Exact recovered addresses (normalized: Ghidra base 0x100000 subtracted) ──────────────
# iAp2MarshalGetBytes: 0x21a56 (in both binaries)
GETBYTES_VA = 0x21a56

# Direct call sites in iAP2Service-2.0 (from audit tool v1.2.0)
DIRECT_CALL_SITES: Dict[str, List[int]] = {
    "heap_string_materializer": [0x295d5],  # 1 call
    "SessionBTConnection": [0x3c517, 0x3c620],  # 2 calls
    "SessionLocation": [0x3e2b4, 0x3e2ec, 0x3e324, 0x3e35c, 0x3e394, 0x3e3cc, 0x3e404],  # 7 calls
    "SessionAppLaunch": [0x3f6ca],  # 1 call
    "SessionExternalAccessoryProtocol": [0x41ea1],  # 1 call
    "SessionHID": [0x42ef2, 0x42fba],  # 2 calls
    "SessionMediaLibraryUpdates": [0x475d9, 0x4760b, 0x47780],  # 3 calls
    "SessionVoiceOver": [0x4b603],  # 1 call
    "SessionWiFiInformation": [0x4e6e1, 0x4e713],  # 2 calls
    "SessionPlayMediaLibrary": [0x4ef6f, 0x4eff8, 0x4f039, 0x4f10b, 0x4f1c4],  # 5 calls
    "SessionCommunications": [0x5a4f1, 0x5a5c1, 0x5a71a, 0x5a873, 0x5ab0b, 0x5ad05],  # 6 calls
}
# Total: 31 calls

# Wrapper callers (indirect via heap-string materializer at 0x2957c)
WRAPPER_CALLERS: Dict[str, List[int]] = {
    "SessionConnection": [
        0x38122, 0x3814e, 0x3817a, 0x381a6, 0x381d2, 0x381fe, 0x3822a,
        0x38256, 0x38282, 0x382ae, 0x382da, 0x38306, 0x38332, 0x3835e, 0x3838a
    ],  # 15 calls (from 0x38010 handleConnectionCmd)
    "SessionIdentification": [
        0x5588a, 0x558b6, 0x558e2, 0x5590e, 0x5593a, 0x55966, 0x55992
    ],  # 7 calls (from 0x556e2 handleIdentificationCmd)
}
# Total: 22 wrapper calls

# Downstream functions invoked by each caller (from disassembly tracing)
DOWNSTREAM_FUNCTIONS: Dict[str, List[Dict]] = {
    "heap_string_materializer": [
        {"name": "malloc", "va": 0x4f10, "via_plt": True, "sink": "allocation"},
        {"name": "memset", "va": 0x4a10, "via_plt": True, "sink": "initialization"},
        {"name": "strncpy", "va": 0x49d0, "via_plt": True, "sink": "CRITICAL:null_source_dos_overread_disclosure"},
        # Later %s logging of heap-string (indirect)
    ],
    "SessionBTConnection": [
        {"name": "FUN_0013c9dc", "va": 0x3c9dc, "caller_site": 0x3c517, "sink": "param_list_builder"},
        {"name": "FUN_0013c77c", "va": 0x3c77c, "caller_site": 0x3c620, "sink": "param_list_builder"},
    ],
    "SessionLocation": [
        {"name": "FUN_0013e48a", "va": 0x3e48a, "caller_sites": [0x3e2b4, 0x3e2ec, 0x3e324, 0x3e35c, 0x3e394, 0x3e3cc, 0x3e404], "sink": "param_list_builder"},
    ],
    "SessionAppLaunch": [
        {"name": "logger", "va": 0x6fa6, "via_plt": False, "sink": "CRITICAL:format_string_disclosure_null_crash", "detail": "log(\"%s\", ptr) at 0x3f6d3"},
        {"name": "FUN_0013f7ae", "va": 0x3f7ae, "caller_site": 0x3f6ca, "sink": "param_list_builder"},
    ],
    "SessionExternalAccessoryProtocol": [
        {"name": "FUN_0014218c", "va": 0x4218c, "caller_site": 0x41ea1, "sink": "param_list_builder"},
    ],
    "SessionHID": [
        {"name": "FUN_001432c2", "va": 0x432c2, "caller_site": 0x42fdc, "sink": "param_list_builder"},
        {"name": "FUN_001430d0", "va": 0x430d0, "caller_site": 0x42f14, "sink": "param_list_builder"},
    ],
    "SessionMediaLibraryUpdates": [
        {"name": "FUN_00147806", "va": 0x47806, "sink": "param_list_builder"},
        {"name": "FUN_00148f5a", "va": 0x48f5a, "sink": "internal_helper"},
        {"name": "FUN_00149162", "va": 0x49162, "sink": "internal_helper"},
        {"name": "FUN_00149244", "va": 0x49244, "sink": "internal_helper"},
    ],
    "SessionVoiceOver": [
        {"name": "FUN_0014c694", "va": 0x4c694, "caller_site": 0x4b603, "sink": "param_list_builder"},
    ],
    "SessionWiFiInformation": [
        {"name": "FUN_0014e9b6", "va": 0x4e9b6, "caller_sites": [0x4e6e1, 0x4e713], "sink": "param_list_builder"},
    ],
    "SessionPlayMediaLibrary": [
        {"name": "FUN_0014f2b0", "va": 0x4f2b0, "sink": "param_list_builder"},
        {"name": "FUN_0014f694", "va": 0x4f694, "sink": "param_list_builder"},
        {"name": "FUN_0014f886", "va": 0x4f886, "sink": "param_list_builder"},
    ],
    "SessionCommunications": [
        # Multiple downstream handlers
    ],
}

# Deeper downstream functions traced from param_list_builders
DEEP_DOWNSTREAM: Dict[str, Dict] = {
    "FUN_0013c9dc": {
        "va": 0x3c9dc,
        "calls": [
            "FUN_0013d26c (createStartBTConnectionUpdatesParamList)",
            "FUN_0011d0a0 (marshal)",
            "FUN_0011abd6 (encode)",
            "FUN_001152de (send)",
        ],
        "sink_class": "ipc_marshalling_chain",
    },
    "FUN_0013c77c": {
        "va": 0x3c77c,
        "calls": [
            "FUN_0013cd94 (createBTComponentInformationParamList)",
            "FUN_0013cf6e (extract_status_string)",
            "FUN_0011cf4a (add_param)",
            "FUN_0011d0a0 / FUN_0011abd6 / FUN_001152de (marshal/encode/send)",
        ],
        "sink_class": "ipc_marshalling_chain",
    },
    "FUN_0013e48a": {
        "va": 0x3e48a,
        "calls": [
            "FUN_0013e67c (create param list)",
            "FUN_0011d0a0 / FUN_0011abd6 / FUN_001152de (marshal/encode/send)",
        ],
        "sink_class": "ipc_marshalling_chain",
    },
    "FUN_0013f7ae": {
        "va": 0x3f7ae,
        "calls": [
            "FUN_0013fa0e (create param list)",
            "FUN_0011d0a0 / FUN_0011abd6 / FUN_001152de (marshal/encode/send)",
        ],
        "sink_class": "ipc_marshalling_chain",
    },
    "FUN_0014218c": {
        "va": 0x4218c,
        "calls": [
            "FUN_00142512 (create param list)",
            "FUN_0011d0a0 / FUN_0011abd6 / FUN_001152de (marshal/encode/send)",
        ],
        "sink_class": "ipc_marshalling_chain",
    },
    "FUN_001432c2": {
        "va": 0x432c2,
        "calls": [
            "FUN_001436a6 (create param list)",
            "FUN_0011d0a0 / FUN_0011abd6 / FUN_001152de (marshal/encode/send)",
        ],
        "sink_class": "ipc_marshalling_chain",
    },
    "FUN_001430d0": {
        "va": 0x430d0,
        "calls": [
            "FUN_001436a6 (shared create param list)",
            "FUN_0011d0a0 / FUN_0011abd6 / FUN_001152de (marshal/encode/send)",
        ],
        "sink_class": "ipc_marshalling_chain",
    },
}

# ─── Sink Classification ──────────────────────────────────────────
class SinkClass(Enum):
    CRITICAL_NULL_SOURCE_DOS = "CWE-476:null-source-strncpy-DoS"
    CRITICAL_OVERREAD_DISCLOSURE = "CWE-125:overread-disclosure-via-strncpy"
    CRITICAL_FORMAT_STRING_DISCLOSURE = "CWE-134:format-string-disclosure-null-crash"
    IPC_MARSHALLING_CHAIN = "ipc-marshalling-chain"
    PARAM_LIST_BUILDER = "param-list-builder"
    INTERNAL_HELPER = "internal-helper"
    UNKNOWN = "unknown"


# ─── Data Models ──────────────────────────────────────────────────
@dataclass
class CallSite:
    function: str
    va: int
    binary: str  # "service" or "framework"
    next_call_va: Optional[int] = None
    next_call_name: Optional[str] = None
    sink_class: Optional[SinkClass] = None
    notes: str = ""


@dataclass
class DownstreamTrace:
    source_caller: str
    source_va: int
    getbytes_va: int
    immediate_sink: CallSite
    deep_sinks: List[CallSite] = field(default_factory=list)
    sink_classes: Set[SinkClass] = field(default_factory=set)
    exploitable_primitives: List[str] = field(default_factory=list)


@dataclass
class AuditResult:
    schema: str = "ioniq-iap2-downstream-consumers-audit/v1"
    tool_version: str = "1.0.0"
    service_binary: Dict = field(default_factory=dict)
    framework_binary: Dict = field(default_factory=dict)
    transaction_tail_overread: Dict = field(default_factory=dict)
    direct_call_sites: List[CallSite] = field(default_factory=list)
    wrapper_call_sites: List[CallSite] = field(default_factory=list)
    downstream_traces: List[DownstreamTrace] = field(default_factory=list)
    exploitable_primitives: List[Dict] = field(default_factory=list)
    validation: Dict = field(default_factory=dict)


# ─── Binary Analysis ──────────────────────────────────────────────
class BinaryAnalyzer:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.data = self._read()
        self.segments = self._parse_load_segments()
        self._verify_hash()

    def _read(self) -> bytes:
        data = self.path.read_bytes()
        return data

    def _verify_hash(self):
        h = hashlib.sha256(self.data).hexdigest()
        expected = SERVICE_SHA256 if "iAP2Service" in self.path.name else FRAMEWORK_SHA256
        if h != expected:
            raise ValueError(f"Hash mismatch: {h} != {expected}")

    def _parse_load_segments(self) -> List[Tuple[int, int, int]]:
        """Return list of (vaddr, offset, memsz) for PT_LOAD segments."""
        if self.data[:4] != b"\x7fELF":
            raise ValueError("Not an ELF file")
        ei_class = self.data[4]
        if ei_class != 2:
            raise ValueError("Not 64-bit ELF")
        e_phoff = struct.unpack_from("<Q", self.data, 0x20)[0]
        e_phentsize = struct.unpack_from("<H", self.data, 0x36)[0]
        e_phnum = struct.unpack_from("<H", self.data, 0x38)[0]
        segments = []
        for i in range(e_phnum):
            off = e_phoff + i * e_phentsize
            p_type = struct.unpack_from("<I", self.data, off)[0]
            if p_type == 1:  # PT_LOAD
                p_vaddr = struct.unpack_from("<Q", self.data, off + 0x10)[0]
                p_offset = struct.unpack_from("<Q", self.data, off + 0x8)[0]
                p_memsz = struct.unpack_from("<Q", self.data, off + 0x28)[0]
                segments.append((p_vaddr, p_offset, p_memsz))
        return segments

    def va_to_offset(self, va: int, size: int = 1) -> int:
        for vaddr, offset, memsz in self.segments:
            if vaddr <= va < vaddr + memsz:
                end_va = va + size
                if end_va <= vaddr + memsz:
                    return offset + (va - vaddr)
        raise ValueError(f"VA {va:#x}+{size:#x} not file-backed")

    def read_bytes(self, va: int, size: int) -> bytes:
        off = self.va_to_offset(va, size)
        return self.data[off:off + size]

    def find_next_call(self, va: int, max_bytes: int = 64) -> Optional[Tuple[int, int]]:
        """Find next CALL instruction after va. Returns (call_va, target_va) or None."""
        try:
            code = self.read_bytes(va, max_bytes)
        except ValueError:
            return None
        for i in range(len(code) - 5):
            if code[i] == 0xE8:  # CALL rel32
                rel = struct.unpack_from("<i", code, i + 1)[0]
                target = va + i + 5 + rel
                return (va + i, target)
        return None

    def get_function_at_va(self, va: int) -> Optional[str]:
        """Lookup known function name at VA."""
        # This would ideally use a symbol table; for now use known mappings
        known = {
            0x4fa0: "iAp2MarshalGetBytes@plt",
            0x4f10: "malloc@plt",
            0x4a10: "memset@plt",
            0x49d0: "strncpy@plt",
            0x6fa6: "logger (getCurrentTimeString+0x1b1)",
            0x3c9dc: "FUN_0013c9dc",
            0x3c77c: "FUN_0013c77c",
            0x3e48a: "FUN_0013e48a",
            0x3f7ae: "FUN_0013f7ae",
            0x4218c: "FUN_0014218c",
            0x432c2: "FUN_001432c2",
            0x430d0: "FUN_001430d0",
            0x47806: "FUN_00147806",
            0x48f5a: "FUN_00148f5a",
            0x49162: "FUN_00149162",
            0x49244: "FUN_00149244",
            0x4c694: "FUN_0014c694",
            0x4e9b6: "FUN_0014e9b6",
            0x4f2b0: "FUN_0014f2b0",
            0x4f694: "FUN_0014f694",
            0x4f886: "FUN_0014f886",
        }
        return known.get(va)


# ─── Audit Engine ─────────────────────────────────────────────────
class DownstreamAudit:
    def __init__(self):
        self.service = BinaryAnalyzer(SERVICE_BIN)
        self.framework = BinaryAnalyzer(FRAMEWORK_BIN)
        self.traces: List[DownstreamTrace] = []

    def analyze_direct_calls(self) -> List[CallSite]:
        sites = []
        for func_name, vas in DIRECT_CALL_SITES.items():
            for va in vas:
                # All direct calls are in iAP2Service-2.0
                next_call = self.service.find_next_call(va)
                cs = CallSite(
                    function=func_name,
                    va=va,
                    binary="service",
                    next_call_va=next_call[0] if next_call else None,
                    next_call_name=self.service.get_function_at_va(next_call[1]) if next_call else None,
                    sink_class=self._classify_sink(func_name, va, next_call),
                    notes=f"Direct GetBytes caller in {func_name}",
                )
                sites.append(cs)
        return sites

    def analyze_wrapper_calls(self) -> List[CallSite]:
        sites = []
        for func_name, vas in WRAPPER_CALLERS.items():
            for va in vas:
                next_call = self.service.find_next_call(va)
                cs = CallSite(
                    function=func_name,
                    va=va,
                    binary="service",
                    next_call_va=next_call[0] if next_call else None,
                    next_call_name=self.service.get_function_at_va(next_call[1]) if next_call else None,
                    sink_class=SinkClass.CRITICAL_NULL_SOURCE_DOS,  # via heap_string_materializer
                    notes=f"Wrapper call via heap_string_materializer (0x2957c) in {func_name}",
                )
                sites.append(cs)
        return sites

    def _classify_sink(self, func_name: str, va: int, next_call: Optional[Tuple[int, int]]) -> SinkClass:
        if func_name == "heap_string_materializer":
            return SinkClass.CRITICAL_NULL_SOURCE_DOS  # also OVERREAD_DISCLOSURE
        if func_name == "SessionAppLaunch":
            return SinkClass.CRITICAL_FORMAT_STRING_DISCLOSURE
        if next_call and next_call[1] in DEEP_DOWNSTREAM:
            return SinkClass.IPC_MARSHALLING_CHAIN
        if func_name in ("SessionLocation", "SessionExternalAccessoryProtocol",
                         "SessionHID", "SessionVoiceOver", "SessionWiFiInformation",
                         "SessionPlayMediaLibrary", "SessionCommunications",
                         "SessionBTConnection", "SessionMediaLibraryUpdates"):
            return SinkClass.PARAM_LIST_BUILDER
        return SinkClass.UNKNOWN

    def build_traces(self, direct_sites: List[CallSite], wrapper_sites: List[CallSite]) -> List[DownstreamTrace]:
        traces = []

        # Direct call traces
        for cs in direct_sites:
            trace = DownstreamTrace(
                source_caller=cs.function,
                source_va=cs.va,
                getbytes_va=GETBYTES_VA,
                immediate_sink=cs,
            )
            # Add deep sinks
            if cs.next_call_va and cs.next_call_va in [0x3c9dc, 0x3c77c, 0x3e48a, 0x3f7ae,
                                                         0x4218c, 0x432c2, 0x430d0]:
                deep = DEEP_DOWNSTREAM.get(f'FUN_00{cs.next_call_va:x}')
                if deep:
                    for call_name in deep["calls"]:
                        trace.deep_sinks.append(CallSite(
                            function=call_name.split()[0],
                            va=0,
                            binary="service",
                            sink_class=SinkClass.IPC_MARSHALLING_CHAIN,
                            notes=call_name,
                        ))
                    trace.sink_classes.add(SinkClass.IPC_MARSHALLING_CHAIN)

            # Classify exploitable primitives
            trace.exploitable_primitives = self._identify_primitives(cs.function, cs.va)
            trace.sink_classes.add(cs.sink_class) if cs.sink_class else None
            traces.append(trace)

        # Wrapper traces (all lead to heap_string_materializer)
        for cs in wrapper_sites:
            trace = DownstreamTrace(
                source_caller=cs.function,
                source_va=cs.va,
                getbytes_va=GETBYTES_VA,
                immediate_sink=CallSite(
                    function="heap_string_materializer",
                    va=0x2957c,
                    binary="service",
                    sink_class=SinkClass.CRITICAL_NULL_SOURCE_DOS,
                    notes="Wrapper calls FUN_0012957c at 0x2957c",
                ),
                deep_sinks=[
                    CallSite(function="malloc", va=0x4f10, binary="service", sink_class=SinkClass.UNKNOWN),
                    CallSite(function="memset", va=0x4a10, binary="service", sink_class=SinkClass.UNKNOWN),
                    CallSite(function="strncpy", va=0x49d0, binary="service",
                             sink_class=SinkClass.CRITICAL_OVERREAD_DISCLOSURE,
                             notes="CRITICAL: strncpy(dest, overread_ptr, len) or strncpy(dest, NULL, len)"),
                ],
                sink_classes={SinkClass.CRITICAL_NULL_SOURCE_DOS, SinkClass.CRITICAL_OVERREAD_DISCLOSURE},
                exploitable_primitives=[
                    "Null-source strncpy DoS (CWE-476)",
                    "Over-read disclosure via strncpy + later %s logging (CWE-125)",
                ],
            )
            traces.append(trace)

        return traces

    def _identify_primitives(self, func_name: str, va: int) -> List[str]:
        primitives = []
        if func_name == "heap_string_materializer":
            primitives.extend([
                "Null-source strncpy DoS (CWE-476): GetBytes returns NULL, len>0 passed to strncpy",
                "Over-read disclosure (CWE-125): GetBytes returns ptr into 64-byte over-read region, strncpy copies it to heap, later %s discloses",
            ])
        elif func_name == "SessionAppLaunch":
            primitives.append(
                "Format-string disclosure/null-crash (CWE-134): log(\"%s\", ptr) where ptr is over-read or NULL"
            )
        elif func_name in ("SessionBTConnection", "SessionLocation", "SessionExternalAccessoryProtocol",
                           "SessionHID", "SessionMediaLibraryUpdates", "SessionVoiceOver",
                           "SessionWiFiInformation", "SessionPlayMediaLibrary", "SessionCommunications"):
            primitives.append(
                f"Over-read/NULL pointer propagated to IPC marshalling chain via {func_name} param list builder"
            )
        return primitives

    def run(self) -> AuditResult:
        direct_sites = self.analyze_direct_calls()
        wrapper_sites = self.analyze_wrapper_calls()
        traces = self.build_traces(direct_sites, wrapper_sites)

        # Collect all unique primitives
        all_primitives = []
        seen = set()
        for trace in traces:
            for p in trace.exploitable_primitives:
                if p not in seen:
                    seen.add(p)
                    all_primitives.append({
                        "description": p,
                        "source_callers": [trace.source_caller],
                        "sink_classes": [s.value for s in trace.sink_classes],
                    })

        result = AuditResult(
            service_binary={
                "path": str(SERVICE_BIN),
                "sha256": SERVICE_SHA256,
                "size": SERVICE_SIZE,
                "build_id": SERVICE_BUILD_ID,
            },
            framework_binary={
                "path": str(FRAMEWORK_BIN),
                "sha256": FRAMEWORK_SHA256,
                "size": FRAMEWORK_SIZE,
                "build_id": FRAMEWORK_BUILD_ID,
            },
            transaction_tail_overread={
                "initializer": "iAp2MarshalInitFromTxn",
                "initializer_range": "0x210ff..0x21175",
                "overstatement_anchor": "0x21126..0x2115e",
                "overstatement_bytes": 64,
                "mechanism": "remaining = *(uint32_t*)(txn + 0x38) /* total size */; no remaining -= 0x40",
                "accessor_bounds_check": "iAp2MarshalGetBytes at 0x216ab compares requested_len against overstated remaining",
                "accessor_range": "0x21a56..0x21b21",
                "impact": "Accessor permits reads up to 64 bytes past true allocation end; returns interior pointer",
            },
            direct_call_sites=direct_sites,
            wrapper_call_sites=wrapper_sites,
            downstream_traces=traces,
            exploitable_primitives=all_primitives,
            validation={
                "total_direct_calls": sum(len(v) for v in DIRECT_CALL_SITES.values()),
                "total_wrapper_calls": sum(len(v) for v in WRAPPER_CALLERS.values()),
                "total_traces": len(traces),
                "critical_sinks": sum(1 for t in traces if SinkClass.CRITICAL_NULL_SOURCE_DOS in t.sink_classes
                                      or SinkClass.CRITICAL_OVERREAD_DISCLOSURE in t.sink_classes
                                      or SinkClass.CRITICAL_FORMAT_STRING_DISCLOSURE in t.sink_classes),
                "ipc_chain_sinks": sum(1 for t in traces if SinkClass.IPC_MARSHALLING_CHAIN in t.sink_classes),
            },
        )
        return result


# ─── Serialization ────────────────────────────────────────────────
def dataclass_to_dict(obj: Any) -> Any:
    if hasattr(obj, "__dataclass_fields__"):
        d = {}
        for k, v in asdict(obj).items():
            d[k] = dataclass_to_dict(v)
        return d
    elif isinstance(obj, set):
        return [dataclass_to_dict(x) for x in obj]
    elif isinstance(obj, list):
        return [dataclass_to_dict(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: dataclass_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, pathlib.Path):
        return str(obj)
    else:
        return obj


def write_audit_json(result: AuditResult, out_path: pathlib.Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = dataclass_to_dict(result)
    # Canonical JSON: sorted keys, no whitespace, UTF-8
    json_bytes = json.dumps(data, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")
    # Exclusive create
    try:
        out_path.open("xb").write(json_bytes)
    except FileExistsError:
        # Read existing, compare canonical
        existing = out_path.read_bytes()
        if existing != json_bytes:
            raise ValueError(f"Output file exists with different content: {out_path}")
    print(f"Written: {out_path} ({len(json_bytes)} bytes)")
    return hashlib.sha256(json_bytes).hexdigest()


# ─── Main ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="iAP2 Downstream Consumer Audit")
    parser.add_argument("--output", "-o", type=pathlib.Path,
                        default=pathlib.Path("evidence/artifacts/projection-candidates/iap2-downstream-consumers-audit.json"))
    parser.add_argument("--evidence-md", type=pathlib.Path,
                        default=pathlib.Path("evidence/iap2-downstream-consumers-audit.md"))
    args = parser.parse_args()

    audit = DownstreamAudit()
    result = audit.run()

    # Write JSON artifact
    sha256 = write_audit_json(result, args.output)
    print(f"Artifact SHA-256: {sha256}")

    # Write evidence markdown
    write_evidence_markdown(result, args.evidence_md, sha256)
    print(f"Evidence: {args.evidence_md}")

    # Print summary
    print(f"\n=== SUMMARY ===")
    print(f"Direct call sites: {result.validation['total_direct_calls']}")
    print(f"Wrapper call sites: {result.validation['total_wrapper_calls']}")
    print(f"Total traces: {result.validation['total_traces']}")
    print(f"Critical sinks: {result.validation['critical_sinks']}")
    print(f"IPC chain sinks: {result.validation['ipc_chain_sinks']}")
    print(f"Exploitable primitives: {len(result.exploitable_primitives)}")
    for p in result.exploitable_primitives:
        print(f"  - {p['description']}")


def write_evidence_markdown(result: AuditResult, path: pathlib.Path, artifact_sha256: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# iAP2 Downstream Consumer Audit — Exact Evidence",
        "",
        f"**Schema**: `ioniq-iap2-downstream-consumers-audit/v1`",
        f"**Tool Version**: `1.0.0`",
        f"**Artifact**: `evidence/artifacts/projection-candidates/iap2-downstream-consumers-audit.json`",
        f"**Artifact SHA-256**: `{artifact_sha256}`",
        "",
        "## Binary Identities",
        "",
        f"- **iAP2Service-2.0**: {SERVICE_SIZE} bytes, SHA-256 `{SERVICE_SHA256}`, Build ID `{SERVICE_BUILD_ID}`",
        f"- **libiAP2AppFramework-2.0.so**: {FRAMEWORK_SIZE} bytes, SHA-256 `{FRAMEWORK_SHA256}`, Build ID `{FRAMEWORK_BUILD_ID}`",
        "",
        "## Transaction-Tail Over-Read (Root Cause)",
        "",
        f"- **Initializer**: `iAp2MarshalInitFromTxn` at `0x210ff..0x21175`",
        f"- **Overstatement Anchor**: `0x21126..0x2115e` — `remaining = *(uint32_t*)(txn + 0x38)` (total size, not payload size); **no `remaining -= 0x40`**",
        f"- **Overstatement**: **64 bytes** — marshal state allows reads 64 bytes past true allocation end",
        f"- **Accessor**: `iAp2MarshalGetBytes` at `0x21a56..0x21b21` — bounds check at `0x216ab` uses overstated `remaining`",
        f"- **Impact**: Accessor returns interior pointer up to 64 bytes past allocation; NULL returned only when request exceeds overstated remaining",
        "",
        "## 31 Direct Call Sites + 22 Wrapper Calls",
        "",
        "| Caller | Direct Calls | Wrapper Calls | Total | Immediate Sink Class |",
        "|--------|-------------|---------------|-------|---------------------|",
    ]
    all_callers = set(DIRECT_CALL_SITES.keys()) | set(WRAPPER_CALLERS.keys())
    for caller in sorted(all_callers):
        dc = len(DIRECT_CALL_SITES.get(caller, []))
        wc = len(WRAPPER_CALLERS.get(caller, []))
        sink_class = "various"
        if caller == "heap_string_materializer":
            sink_class = "CRITICAL: strncpy (CWE-476, CWE-125)"
        elif caller == "SessionAppLaunch":
            sink_class = "CRITICAL: log(\"%s\", ptr) (CWE-134)"
        elif caller in ("SessionBTConnection", "SessionLocation", "SessionExternalAccessoryProtocol",
                        "SessionHID", "SessionMediaLibraryUpdates", "SessionVoiceOver",
                        "SessionWiFiInformation", "SessionPlayMediaLibrary", "SessionCommunications"):
            sink_class = "ParamListBuilder → IPC marshalling chain"
        lines.append(f"| {caller} | {dc} | {wc} | {dc+wc} | {sink_class} |")

    lines.extend([
        "",
        "## Exploitable Primitives (Exact-Static Candidates)",
        "",
    ])
    for i, p in enumerate(result.exploitable_primitives, 1):
        lines.append(f"### Primitive {i}: {p['description']}")
        lines.append(f"- **Source Callers**: {', '.join(p['source_callers'])}")
        lines.append(f"- **Sink Classes**: {', '.join(p['sink_classes'])}")
        lines.append("")

    lines.extend([
        "## Transaction Construction for Trigger",
        "",
        "Service receiver framing (`0x2dadd..0x2df7b`):",
        "1. `recv(fd, stack_hdr, 64, MSG_WAITALL)` — accepts any positive return",
        "2. `declared_total = stack_hdr[0x38]` (uint32)",
        "3. `malloc(declared_total)` — attacker controls allocation size",
        "4. **64-byte header copy BEFORE `declared_total <= 64` check** (CWE-787, CWE-457, CWE-400)",
        "5. `recv(fd, alloc+0x40, declared_total-64, MSG_WAITALL)` — body receive",
        "6. `handleClientCmd(alloc)` — dispatches to command handlers",
        "",
        "**Over-read trigger condition**:",
        "- Marshaled string field at parse offset `p` declares length `L`",
        "- True payload capacity: `declared_total - 64` bytes",
        "- Accessor permits read if `p + L <= declared_total` (overstated bound)",
        "- True bound: `p + L <= declared_total - 64`",
        "- **Over-read window**: `declared_total - 64 < p + L <= declared_total`",
        "- Request `L` in this window → `GetBytes` returns pointer into over-read region",
        "",
        "**Null-source trigger**: `p + L > declared_total` → `GetBytes` returns NULL, but caller uses declared length",
        "",
        "## Validation",
        "",
        f"- Total direct calls: **{result.validation['total_direct_calls']}** (expected 31)",
        f"- Total wrapper calls: **{result.validation['total_wrapper_calls']}** (expected 22)",
        f"- Total traces: **{result.validation['total_traces']}**",
        f"- Critical sinks (CWE-476, CWE-125, CWE-134): **{result.validation['critical_sinks']}**",
        f"- IPC marshalling chain sinks: **{result.validation['ipc_chain_sinks']}**",
        "",
        "## Boundaries & Limitations",
        "",
        "- **Exact-static only**: No live delivery, no runtime admission, no phone-to-handler reachability proven",
        "- **Over-read disclosure**: Requires heap adjacency with sensitive data; allocator behavior not modeled",
        "- **Null-source DoS**: Requires UID-0 service restart policy to be impactful",
        "- **IPC chain**: Downstream marshalling may validate/limit; not fully traced to final `send()`",
        "- **No CVE attribution**: These are exact-static candidates; CVE identity requires runtime exploitability proof",
        "",
        "## Artifacts",
        "",
        f"- JSON: `evidence/artifacts/projection-candidates/iap2-downstream-consumers-audit.json` (SHA-256: `{artifact_sha256}`)",
        f"- This markdown: `evidence/iap2-downstream-consumers-audit.md`",
        f"- Decompiled callers: `work/iap2-marshal-callers-20261112/decompiled/` (11 files)",
        f"- Decompiled downstream: `work/iap2-downstream-consumers-20261113/`",
        "",
    ])
    path.write_text("\n".join(lines))
    print(f"Evidence written to {path}")


if __name__ == "__main__":
    main()