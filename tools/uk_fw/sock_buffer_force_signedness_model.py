#!/usr/bin/env python3
"""Classify bounded CVE-2016-9793 socket-buffer signedness facts.

This Boolean-only host model does not create a socket, issue setsockopt, use a
capability, execute recovered code, interact with a target, or emit an
invocation, option value, payload, race schedule, command, or firmware bytes.
Instruction facts are established separately by exact-static review.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

SCHEMA_VERSION = 1
VMLINUX_SHA256 = "f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b"
BUILD_ID = "273378887b4cf563c10862fdf18b2292765df781"
FIX_COMMIT = "b98b0bc8c431e3ceb4b26b0dfc8db509518fb290"

PRE_RECORDED_TARGET_STATE = {
    "send_force_cap_net_admin_gate_present": True,
    "receive_force_cap_net_admin_gate_present": True,
    "send_doubled_value_compared_as_signed": True,
    "receive_doubled_value_compared_as_signed": True,
    "send_minimum_selected_for_nonpositive_wrapped_result": True,
    "receive_minimum_selected_for_nonpositive_wrapped_result": True,
    "send_store_occurs_after_signed_minimum_selection": True,
    "receive_store_occurs_after_signed_minimum_selection": True,
    "unsigned_maximum_on_doubled_force_value_present": False,
}


class ModelError(ValueError):
    """Supplied facts do not satisfy the bounded Boolean contract."""


def classify_signedness(**values: bool) -> dict[str, Any]:
    expected = set(PRE_RECORDED_TARGET_STATE)
    actual = set(values)
    if actual != expected:
        raise ModelError(
            f"state keys mismatch: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )
    state: dict[str, bool] = {}
    for name in PRE_RECORDED_TARGET_STATE:
        value = values[name]
        if type(value) is not bool:
            raise ModelError(f"{name} must be a boolean")
        state[name] = value

    capability_gates = (
        state["send_force_cap_net_admin_gate_present"]
        and state["receive_force_cap_net_admin_gate_present"]
    )
    signed_clamp_effects = all(
        state[name]
        for name in (
            "send_doubled_value_compared_as_signed",
            "receive_doubled_value_compared_as_signed",
            "send_minimum_selected_for_nonpositive_wrapped_result",
            "receive_minimum_selected_for_nonpositive_wrapped_result",
            "send_store_occurs_after_signed_minimum_selection",
            "receive_store_occurs_after_signed_minimum_selection",
        )
    )
    vulnerable_unsigned_effect = state[
        "unsigned_maximum_on_doubled_force_value_present"
    ]
    rejected = signed_clamp_effects and not vulnerable_unsigned_effect
    if rejected:
        premise: bool | None = False
    elif vulnerable_unsigned_effect:
        premise = True
    else:
        premise = None

    return {
        "input": state,
        "both_force_routes_require_cap_net_admin": capability_gates,
        "complete_signed_clamp_effects_present": signed_clamp_effects,
        "vulnerable_unsigned_maximum_effect_present": vulnerable_unsigned_effect,
        "cve_2016_9793_negative_buffer_premise_present": premise,
        "cve_2016_9793_rejected_by_supplied_machine_effects": rejected,
        "cve_2016_9793_not_rejected_by_complete_machine_effects": not rejected,
        "installed_kernel_identity_observed": None,
        "runtime_socket_policy_observed": None,
        "runtime_cap_net_admin_observed": None,
        "socket_option_invocation_observed": None,
        "negative_socket_buffer_state_observed": None,
        "memory_corruption_observed": None,
        "kernel_crash_observed": None,
        "privilege_escalation_observed": None,
        "persistence_observed": None,
    }


def build_report(state: dict[str, bool] | None = None) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "model": "sock-buffer-force-signedness",
        "evidence_binding": {
            "vmlinux_sha256": VMLINUX_SHA256,
            "vmlinux_build_id": BUILD_ID,
            "upstream_fix_commit": FIX_COMMIT,
            "pre_recorded_target_state": {
                "source": "separate Homebrew-LLVM instruction review; not verified by this model execution",
                **PRE_RECORDED_TARGET_STATE,
            },
            "assessment": "evidence/vendor-kernel-sock-buffer-force-cve-2016-9793.md",
        },
        "claim_boundary": {
            "establishes": [
                "classification of supplied Boolean capability-gate and signed-clamp facts",
                "whether complete signed minimum-selection effects reject the named negative-buffer premise",
                "unknown rather than affected when fix facts are incomplete and no vulnerable unsigned effect is supplied",
            ],
            "does_not_establish": [
                "automatic instruction verification",
                "owner-unit installed kernel identity or runtime socket policy",
                "live capability possession, invocation, negative state, corruption, crash, root, or persistence",
            ],
            "inputs_are_boolean_only": True,
            "emits_no_socket_option_value_invocation_payload_race_command_instructions_or_firmware_bytes": True,
        },
        "pre_recorded_target_classification": classify_signedness(
            **PRE_RECORDED_TARGET_STATE
        ),
    }
    if state is not None:
        report["classification"] = classify_signedness(**state)
    return report


def _bool(value: str) -> bool:
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    raise argparse.ArgumentTypeError("expected true or false")


class _Once(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest) is not None:
            parser.error(f"{option_string} may be specified only once")
        setattr(namespace, self.dest, values)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    for name in PRE_RECORDED_TARGET_STATE:
        parser.add_argument(
            f"--{name.replace('_', '-')}", dest=name, type=_bool, action=_Once
        )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    state = {name: getattr(args, name) for name in PRE_RECORDED_TARGET_STATE}
    supplied = [value is not None for value in state.values()]
    if any(supplied) and not all(supplied):
        raise SystemExit(
            "error: all socket-buffer signedness arguments must be supplied together"
        )
    try:
        report = build_report(state if all(supplied) else None)  # type: ignore[arg-type]
    except ModelError as exc:
        raise SystemExit(f"error: {exc}") from exc
    sys.stdout.buffer.write(
        json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
