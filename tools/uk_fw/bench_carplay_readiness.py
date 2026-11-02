#!/usr/bin/env python3
"""Assess passive bench evidence for the recovered CarPlay/iAP2 surface.

The tool consumes only canonical ``ioniq-bench-state/v1`` JSON produced by the
read-only disconnected-bench probe. It does not contact a target, open an iAP2
device, start a service, change an interface, or send protocol data. Positive
results bind installed identities and runtime prerequisites only; they do not
establish a public-CVE match, phone-to-parser delivery, code execution, root, or
persistence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any

INPUT_SCHEMA = "ioniq-bench-state/v1"
OUTPUT_SCHEMA = "ioniq-bench-carplay-readiness/v1"
TOOL_VERSION = "1.0.0"
MAX_INPUT_BYTES = 64 * 1024 * 1024
HEX64_RE = re.compile(r"[0-9a-f]{64}")
VALID_STATES = frozenset(("pass", "fail", "unknown"))
EXPECTED_SECTION_ORDER = (
    "meta",
    "identity",
    "processes",
    "smack",
    "units",
    "interfaces",
    "cellular",
    "bluetooth",
    "dropbear",
    "storage",
    "hashes",
    "complete",
)

REFERENCE_HASHES = {
    "/lib/systemd/system/carplay_iAP2.service": "f7cf915509005a4aaa18d09e3a6ccd0abdd72ef2b2816641ea9a592a1e3f4495",
    "/lib/systemd/system/carplay_mdnsd.service": "3d9f719d13b4c9dfc3f317a12d6aa40664886ce00bb04bcb6bda937650e88983",
    "/etc/iap2_mod.sh": "ecec04580a09b258796e96e20835deab60479b76edaceaaca01d58097b19656b",
    "/etc/smack/accesses.d/projection": "978ccab43e6724df0bb74c4f84e3319ab3f0022dec442f4389fba140f6b3c1c9",
    "/app/bin/iAP2Service-2.0": "38419131df82ec7e3c3b29a68ecc1a078c7f0b403051f137fe9f46f82b99f26e",
    "/app/bin/AppProjection": "8f0096bcc0734d4c9766c15bac54c42f302ed7057182c2573b5ac543913960e3",
    "/app/bin/mdnsd": "71122d8f59cdfd248f80414014e22114b0ee486415e5a7de23f5acd1676b9cdd",
    "/app/lib/libiAP2AppFramework-2.0.so": "d4d0558c9c53f02ee14024c081ccd83a02ca29404ef400131e2951f68a388120",
    "/app/lib/libAirPlay.so": "ef9e69e3b3388d4a7a1d185827c710af25b8ee99d406c60c664a9609b00aada0",
    "/app/lib/libCoreUtils.so": "9104e2c16ee27e647fac090ee7f3aa4cc686b8caaea1dc24763af2950c0ebfae",
    "/app/lib/libAirPlaySupport.so": "1e57d807c320999fda35ac08e7e213f6533014f8d68391b1c33b00505b175893",
    "/app/lib/libCarPlayAppFramework.so": "e3603e6b0744cf07724cc5cc79ea01ea3d9207d7eaf37c544c7ce26536ecd7a2",
    "/app/lib/libCarPlayMediaFramework.so": "69690210d1aa4dec33c77b0e80f1d3368f8a70bcb507c1b158b6245dc29eb2f3",
    "/lib/modules/4.1.27-abl/kernel/drivers/usb/gadget/function/usb_f_ncm.ko": "bb4c508c17d7c292d806f98d2d135a00949b2c144b57837194aa574c9a10cfaa",
    "/lib/modules/4.1.27-abl/kernel/drivers/usb/gadget/function/usb_f_iap2.ko": "13bb79d9d9e991fdb9a950fc4ef8d65491c804a061208acb669ba54683e1e7bd",
    "/lib/modules/4.1.27-abl/kernel/drivers/lge/mfd/mfd-iap2.ko": "1276cee2d1a2eca5e2c8d5c7f49eb813ffeae6b81ee490ba3abfc176ae2040c4",
}
EXPECTED_MODULES = frozenset(("usb_f_ncm", "usb_f_iap2", "mfd_iap2"))


class AssessmentError(ValueError):
    """Fail-closed input or output error."""


def _reject_constant(value: str) -> None:
    raise AssessmentError(f"non-finite JSON constant rejected: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AssessmentError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def stable_read(path: Path) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise AssessmentError("input must be a regular file")
        if before.st_size < 0 or before.st_size > MAX_INPUT_BYTES:
            raise AssessmentError(f"input exceeds {MAX_INPUT_BYTES} byte limit")
        remaining = before.st_size
        chunks: list[bytes] = []
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                raise AssessmentError("short input read")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise AssessmentError("input grew during read")
        after = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise AssessmentError("input identity changed during read")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def load_report_bytes(data: bytes) -> dict[str, Any]:
    if len(data) > MAX_INPUT_BYTES:
        raise AssessmentError(f"input exceeds {MAX_INPUT_BYTES} byte limit")
    try:
        text = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise AssessmentError(f"input is not strict UTF-8: {exc}") from exc
    try:
        report = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise AssessmentError(f"invalid JSON: {exc}") from exc
    if not isinstance(report, dict):
        raise AssessmentError("top-level JSON value must be an object")
    if report.get("schema") != INPUT_SCHEMA:
        raise AssessmentError(f"input schema must be {INPUT_SCHEMA}")
    for name in ("capture_sha256", "canonical_sha256"):
        value = report.get(name)
        if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
            raise AssessmentError(f"{name} must be 64 lowercase hex characters")
    subject = dict(report)
    supplied = subject.pop("canonical_sha256")
    computed = hashlib.sha256(_canonical_bytes(subject)).hexdigest()
    if supplied != computed:
        raise AssessmentError(
            f"canonical_sha256 mismatch: expected {computed}, observed {supplied}"
        )
    return report


def load_report(path: Path) -> dict[str, Any]:
    return load_report_bytes(stable_read(path))


def _facts(report: dict[str, Any]) -> dict[str, Any]:
    value = report.get("facts")
    if not isinstance(value, dict):
        raise AssessmentError("facts must be an object")
    return value


def _dict_fact(facts: dict[str, Any], name: str) -> dict[str, Any]:
    value = facts.get(name, {})
    if not isinstance(value, dict):
        raise AssessmentError(f"facts.{name} must be an object")
    return value


def _list_fact(facts: dict[str, Any], name: str) -> list[Any]:
    value = facts.get(name, [])
    if not isinstance(value, list):
        raise AssessmentError(f"facts.{name} must be an array")
    return value


def _gate(
    gate_id: str,
    status: str,
    summary: str,
    *,
    observed: Any = None,
    expected: Any = None,
) -> dict[str, Any]:
    if status not in VALID_STATES:
        raise AssertionError(f"invalid gate status: {status}")
    return {
        "id": gate_id,
        "status": status,
        "summary": summary,
        "observed": observed,
        "expected": expected,
    }


def _capture_gate(report: dict[str, Any]) -> dict[str, Any]:
    complete = report.get("complete")
    warnings = report.get("warnings")
    section_order = report.get("section_order")
    if not isinstance(complete, bool):
        raise AssessmentError("complete must be Boolean")
    if not isinstance(warnings, list) or not all(isinstance(x, str) for x in warnings):
        raise AssessmentError("warnings must be an array of strings")
    if not isinstance(section_order, list) or not all(
        isinstance(x, str) for x in section_order
    ):
        raise AssessmentError("section_order must be an array of strings")
    passed = complete and not warnings and section_order == list(EXPECTED_SECTION_ORDER)
    return _gate(
        "capture.complete",
        "pass" if passed else "fail",
        "capture is complete, warning-free, and canonically ordered"
        if passed
        else "capture is incomplete, warned, or noncanonically ordered",
        observed={
            "complete": complete,
            "warnings": warnings,
            "section_order": section_order,
        },
        expected={
            "complete": True,
            "warnings": [],
            "section_order": list(EXPECTED_SECTION_ORDER),
        },
    )


def _hash_gate(hashes: dict[str, Any], path: str) -> dict[str, Any]:
    observed = hashes.get(path)
    expected = REFERENCE_HASHES[path]
    gate_id = "identity." + hashlib.sha256(path.encode("utf-8")).hexdigest()[:16]
    if observed is None or observed in ("absent", "unavailable"):
        return _gate(
            gate_id,
            "unknown",
            f"runtime identity was not captured for {path}",
            observed=observed,
            expected={"path": path, "sha256": expected},
        )
    if not isinstance(observed, str) or not HEX64_RE.fullmatch(observed):
        return _gate(
            gate_id,
            "fail",
            f"runtime identity is malformed for {path}",
            observed=observed,
            expected={"path": path, "sha256": expected},
        )
    passed = observed == expected
    return _gate(
        gate_id,
        "pass" if passed else "fail",
        f"runtime identity {'matches' if passed else 'differs from'} recovered {path}",
        observed={"path": path, "sha256": observed},
        expected={"path": path, "sha256": expected},
    )


def _parse_unit(value: Any) -> dict[str, str] | None:
    if not isinstance(value, str):
        return None
    fields: dict[str, str] = {}
    for item in value.split(";"):
        if not item:
            continue
        if "=" not in item:
            return None
        key, setting = item.split("=", 1)
        if key in fields:
            return None
        fields[key] = setting
    return fields if fields else None


def _unit_gate(units: dict[str, Any], name: str, *, require_active: bool) -> dict[str, Any]:
    observed = units.get(name)
    gate_id = f"unit.{name}.{'active' if require_active else 'loaded'}"
    if observed is None or observed == "systemctl-unavailable":
        return _gate(
            gate_id,
            "unknown",
            f"{name} state was not captured",
            observed=observed,
            expected={"LoadState": "loaded", **({"ActiveState": "active"} if require_active else {})},
        )
    fields = _parse_unit(observed)
    if fields is None or "LoadState" not in fields:
        return _gate(
            gate_id,
            "fail",
            f"{name} state is malformed",
            observed=observed,
            expected={"LoadState": "loaded"},
        )
    passed = fields["LoadState"] == "loaded"
    if require_active:
        if "ActiveState" not in fields:
            return _gate(
                gate_id,
                "unknown",
                f"{name} active state was not captured",
                observed=fields,
                expected={"LoadState": "loaded", "ActiveState": "active"},
            )
        passed = passed and fields["ActiveState"] == "active"
    return _gate(
        gate_id,
        "pass" if passed else "fail",
        f"{name} {'is' if passed else 'is not'} {'active and loaded' if require_active else 'loaded'}",
        observed=fields,
        expected={"LoadState": "loaded", **({"ActiveState": "active"} if require_active else {})},
    )


def _parse_file_state(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    fields = value.split("|", 8)
    if len(fields) != 9 or fields[0] != "present":
        return None
    return {
        "state": fields[0],
        "mode": fields[1],
        "uid": int(fields[2]) if fields[2].isdigit() else fields[2],
        "gid": int(fields[3]) if fields[3].isdigit() else fields[3],
        "size": int(fields[4]) if fields[4].isdigit() else fields[4],
        "kind": fields[5],
        "device_major": fields[6].lower(),
        "device_minor": fields[7].lower(),
        "link_target": fields[8],
    }


def _device_gate(files: dict[str, Any], path: str) -> dict[str, Any]:
    observed = files.get(path)
    if observed is None or observed in ("absent", "unavailable"):
        return _gate(
            f"device.{path.rsplit('/', 1)[-1]}",
            "unknown",
            f"{path} was not observed",
            observed=observed,
            expected={"state": "present", "kind": "character special file"},
        )
    parsed = _parse_file_state(observed)
    passed = parsed is not None and parsed["kind"] == "character special file"
    return _gate(
        f"device.{path.rsplit('/', 1)[-1]}",
        "pass" if passed else "fail",
        f"{path} {'is' if passed else 'is not'} an observed character device",
        observed=parsed if parsed is not None else observed,
        expected={"state": "present", "kind": "character special file"},
    )


def _smack_gate(smack: dict[str, Any], path: str, expected: str) -> dict[str, Any]:
    observed_path = smack.get(path)
    gate_id = "smack." + path.rsplit("/", 1)[-1]
    if observed_path is None:
        return _gate(
            gate_id,
            "unknown",
            f"SMACK64 state was not captured for {path}",
            observed=None,
            expected=expected,
        )
    if not isinstance(observed_path, dict):
        raise AssessmentError(f"facts.smack_xattrs[{path!r}] must be an object")
    observed = observed_path.get("SMACK64")
    if not isinstance(observed, dict):
        return _gate(
            gate_id,
            "unknown",
            f"SMACK64 state was not captured for {path}",
            observed=observed,
            expected=expected,
        )
    state = observed.get("state")
    value = observed.get("value")
    if state in ("provider-unavailable", "path-absent", "attribute-absent"):
        return _gate(
            gate_id,
            "unknown",
            f"SMACK64 value is unavailable for {path}",
            observed=observed,
            expected=expected,
        )
    passed = state == "present" and value == expected
    return _gate(
        gate_id,
        "pass" if passed else "fail",
        f"{path} SMACK64 {'matches' if passed else 'does not match'} the recovered label",
        observed=observed,
        expected=expected,
    )


def _process_gate(
    processes: list[Any],
    credentials: dict[str, Any],
    security: dict[str, Any],
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for item in processes:
        if not isinstance(item, dict):
            raise AssessmentError("facts.processes entries must be objects")
        if item.get("exe") == "/app/bin/iAP2Service-2.0":
            candidates.append(item)
    if not candidates:
        return _gate(
            "process.iap2_service",
            "fail",
            "no running process with the exact iAP2 service executable was observed",
            observed=[],
            expected={"exe": "/app/bin/iAP2Service-2.0", "euid": 0, "smack_label": "App::projection"},
        )
    observations: list[dict[str, Any]] = []
    complete_credentials = True
    passed = False
    for process in candidates:
        pid = str(process.get("pid"))
        creds = credentials.get(pid)
        sec = security.get(pid)
        if not isinstance(creds, dict):
            complete_credentials = False
        euid = creds.get("euid") if isinstance(creds, dict) else None
        observations.append({"process": process, "credentials": creds, "security": sec})
        if euid == 0 and process.get("smack_label") == "App::projection":
            passed = True
    if passed:
        status = "pass"
        summary = "a running exact iAP2 service process has EUID 0 and App::projection"
    elif not complete_credentials:
        status = "unknown"
        summary = "the exact iAP2 service process exists but credentials were not fully captured"
    else:
        status = "fail"
        summary = "the observed iAP2 service process lacks the recovered EUID/SMACK combination"
    return _gate(
        "process.iap2_service",
        status,
        summary,
        observed=observations,
        expected={"exe": "/app/bin/iAP2Service-2.0", "euid": 0, "smack_label": "App::projection"},
    )


def _module_gate(modules: list[Any]) -> dict[str, Any]:
    if not modules:
        return _gate(
            "transport.modules",
            "unknown",
            "/proc/modules records were not present in this capture",
            observed=[],
            expected=sorted(EXPECTED_MODULES),
        )
    if not all(isinstance(item, str) for item in modules):
        raise AssessmentError("facts.modules entries must be strings")
    observed_names = sorted({item.split()[0].replace("-", "_") for item in modules if item.split()})
    missing = sorted(EXPECTED_MODULES.difference(observed_names))
    passed = not missing
    return _gate(
        "transport.modules",
        "pass" if passed else "fail",
        "all recovered iAP2/NCM transport modules are loaded"
        if passed
        else "one or more recovered iAP2/NCM transport modules are not loaded",
        observed={"loaded": observed_names, "missing": missing},
        expected=sorted(EXPECTED_MODULES),
    )


def _listener_gate(listeners: list[Any]) -> dict[str, Any]:
    if not listeners:
        return _gate(
            "listener.airplay_7000",
            "unknown",
            "listener records were not present in this capture",
            observed=[],
            expected="an optional local listener ending in :7000",
        )
    if not all(isinstance(item, str) for item in listeners):
        raise AssessmentError("facts.listeners entries must be strings")
    matches = [item for item in listeners if re.search(r":7000(?:\s|$)", item)]
    return _gate(
        "listener.airplay_7000",
        "pass" if matches else "unknown",
        "a port-7000 listener was observed"
        if matches
        else "no port-7000 listener was observed; wired CarPlay does not require this gate",
        observed={"matches": matches, "all": listeners},
        expected="informational only",
    )


def assess(report: dict[str, Any]) -> dict[str, Any]:
    facts = _facts(report)
    hashes = _dict_fact(facts, "hashes")
    units = _dict_fact(facts, "units")
    files = _dict_fact(facts, "files")
    smack = _dict_fact(facts, "smack_xattrs")
    credentials = _dict_fact(facts, "process_credentials")
    security = _dict_fact(facts, "process_security")
    processes = _list_fact(facts, "processes")
    modules = _list_fact(facts, "modules")
    listeners = _list_fact(facts, "listeners")

    capture_gate = _capture_gate(report)
    hash_gates = [_hash_gate(hashes, path) for path in sorted(REFERENCE_HASHES)]
    loaded_gate = _unit_gate(units, "carplay_iAP2.service", require_active=False)
    active_gate = _unit_gate(units, "carplay_iAP2.service", require_active=True)
    mdns_gate = _unit_gate(units, "carplay_mdnsd.service", require_active=True)
    process_gate = _process_gate(processes, credentials, security)
    mfd_gate = _device_gate(files, "/dev/mfd-iap2")
    tty_gate = _device_gate(files, "/dev/ttyIAP20")
    exe_label_gate = _smack_gate(smack, "/app/bin/iAP2Service-2.0", "App::projection")
    mfd_label_gate = _smack_gate(smack, "/dev/mfd-iap2", "System::iap20")
    tty_label_gate = _smack_gate(smack, "/dev/ttyIAP20", "System::iap20")
    module_gate = _module_gate(modules)
    listener_gate = _listener_gate(listeners)
    gates = [
        capture_gate,
        *hash_gates,
        loaded_gate,
        active_gate,
        mdns_gate,
        process_gate,
        mfd_gate,
        tty_gate,
        exe_label_gate,
        mfd_label_gate,
        tty_label_gate,
        module_gate,
        listener_gate,
    ]

    installed_match = capture_gate["status"] == "pass" and all(
        gate["status"] == "pass" for gate in hash_gates
    )
    active_prerequisites = installed_match and all(
        gate["status"] == "pass"
        for gate in (
            active_gate,
            process_gate,
            mfd_gate,
            exe_label_gate,
            mfd_label_gate,
            module_gate,
        )
    )
    result: dict[str, Any] = {
        "schema": OUTPUT_SCHEMA,
        "tool_version": TOOL_VERSION,
        "input": {
            "schema": report["schema"],
            "capture_sha256": report["capture_sha256"],
            "canonical_sha256": report["canonical_sha256"],
        },
        "reference_hashes": REFERENCE_HASHES,
        "gates": gates,
        "gate_counts": {
            state: sum(gate["status"] == state for gate in gates)
            for state in ("fail", "pass", "unknown")
        },
        "verdict": {
            "installed_reference_stack_matches": installed_match,
            "active_wired_carplay_prerequisites_observed": active_prerequisites,
            "configured_uid_zero_and_projection_process_observed": process_gate["status"] == "pass",
            "iap2_device_boundary_observed": all(
                gate["status"] == "pass" for gate in (mfd_gate, mfd_label_gate)
            ),
            "alternate_tty_iap2_endpoint_observed": all(
                gate["status"] == "pass" for gate in (tty_gate, tty_label_gate)
            ),
            "transport_modules_observed": module_gate["status"] == "pass",
            "airplay_port_7000_observed": listener_gate["status"] == "pass",
            "exact_public_cve_code_match_established": False,
            "phone_to_parser_delivery_observed": False,
            "malformed_protocol_input_sent": False,
            "crash_observed": False,
            "code_execution_observed": False,
            "unrestricted_root_access_demonstrated": False,
            "persistence_demonstrated": False,
        },
        "boundaries": [
            "A positive installed-stack verdict binds only exact passive file identities from the owner-controlled disconnected bench.",
            "An active-prerequisite verdict records the exact service, process, module, /dev/mfd-iap2, and SMACK state; the alternate /dev/ttyIAP20 endpoint is reported but not required.",
            "Active prerequisites do not prove phone authentication or attacker-selected bytes reaching a parser.",
            "Port 7000 is informational and is not required for the recovered wired CarPlay path.",
            "Configured EUID zero remains constrained by the observed App::projection SMACK domain and is not an unrestricted-root finding.",
            "No USB/iAP2/AirPlay message, malformed input, service transition, code execution, root transition, flash write, or persistence action is performed or inferred.",
            "This passive assessor does not decide CVE-2025-24132 or CVE-2025-30422 applicability; apply the separate exact-static mechanism review and retain its vendor-confirmation and runtime-delivery limits.",
        ],
    }
    result["canonical_sha256"] = hashlib.sha256(_canonical_bytes(result)).hexdigest()
    return result


def _write_json_exclusive(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(data)
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="canonical bench-state JSON")
    parser.add_argument("-o", "--output", type=Path, help="create this JSON report")
    args = parser.parse_args(argv)
    try:
        result = assess(load_report(args.report))
        data = json.dumps(
            result, ensure_ascii=False, indent=2, sort_keys=True
        ).encode("utf-8") + b"\n"
        if args.output is None:
            sys.stdout.buffer.write(data)
        else:
            _write_json_exclusive(args.output, data)
    except (AssessmentError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
