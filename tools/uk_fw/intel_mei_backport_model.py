#!/usr/bin/env python3
"""Classify four historical Intel MEI memory-safety fix premises.

The default inputs are pre-recorded facts from the exact EU 260128 ``mei.ko``
static excerpt.  This model never loads the module, opens a MEI device, sends a
firmware message, or emits a proof-of-concept.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

SCHEMA = "ioniq-intel-mei-backport-model/v1"
FACT_NAMES = (
    "write_size_cached_before_callback_transfer",
    "callback_pointer_cleared_after_queueing",
    "write_caller_does_not_free_after_mei_cl_write",
    "irq_fragment_addition_has_carry_guard",
    "irq_fragment_total_checked_before_copy",
    "disconnect_response_deferred_to_completion",
    "completion_frees_callback_before_set_disconnected",
)
PRE_RECORDED_TARGET_STATE = {name: True for name in FACT_NAMES}
OBSERVED_FIELDS = (
    "runtime_mei_node_present",
    "runtime_mei_node_unprivileged_writable",
    "installed_module_identity_observed",
    "firmware_controlled_fragment_sequence_observed",
    "host_triggerable_link_reset_observed",
    "kernel_use_after_free_observed",
    "kernel_double_free_observed",
    "kernel_buffer_overflow_observed",
    "kernel_memory_corruption_observed",
    "privilege_escalation_observed",
    "persistence_observed",
)


class ModelError(ValueError):
    pass


def classify(**state: bool) -> dict[str, Any]:
    if set(state) != set(FACT_NAMES):
        raise ModelError("state keys mismatch")
    for name in FACT_NAMES:
        if type(state[name]) is not bool:
            raise ModelError(f"{name} must be a boolean")

    write_fix = all(
        state[name]
        for name in (
            "write_size_cached_before_callback_transfer",
            "callback_pointer_cleared_after_queueing",
        )
    )
    ownership_fix = all(
        state[name]
        for name in (
            "callback_pointer_cleared_after_queueing",
            "write_caller_does_not_free_after_mei_cl_write",
        )
    )
    fragment_fix = all(
        state[name]
        for name in (
            "irq_fragment_addition_has_carry_guard",
            "irq_fragment_total_checked_before_copy",
        )
    )
    disconnect_fix = all(
        state[name]
        for name in (
            "disconnect_response_deferred_to_completion",
            "completion_frees_callback_before_set_disconnected",
        )
    )
    rejected = {
        "23253c31_blocking_write_freed_callback_access": write_fix,
        "6cbb097f_link_reset_callback_double_free": ownership_fix,
        "f862b6b2_fragment_length_integer_overflow": fragment_fix,
        "6a8d648c_fw_disconnect_list_invalidation": disconnect_fix,
    }
    result: dict[str, Any] = {
        "input": {name: state[name] for name in FACT_NAMES},
        "complete_fix_effects": {
            "blocking_write_callback_lifetime": write_fix,
            "write_callback_ownership": ownership_fix,
            "fragment_length_arithmetic": fragment_fix,
            "firmware_disconnect_completion": disconnect_fix,
        },
        "historical_premises_rejected_by_supplied_fix_effects": rejected,
        "all_four_historical_premises_rejected": all(rejected.values()),
    }
    result.update({name: None for name in OBSERVED_FIELDS})
    return result


def build_report(state: dict[str, bool] | None = None) -> dict[str, Any]:
    selected = dict(PRE_RECORDED_TARGET_STATE if state is None else state)
    return {
        "schema": SCHEMA,
        "artifact": {
            "module_sha256": "8518715e6e1910aacddf9da116aa97b98e7fca8f14c64da83959c60204d83609",
            "module_build_id": "ca127bac6266f1afd1ff48cdd0c0bdcb4a67d643",
            "exact_static_excerpt_sha256": "f52f4723550174e90eadae6faa87eb8e991c4eda44dbc2c2e460a34753f1f8a8",
        },
        "classification": classify(**selected),
        "claim_boundary": {
            "historical_fix_effects_are_not_runtime_module_identity": True,
            "device_permissions_and_client_reachability_remain_runtime_questions": True,
            "firmware_influence_does_not_establish_host_control": True,
            "no_cve_or_root_claim_from_version_banner": True,
            "emits_no_operational_payload_or_mei_protocol_traffic": True,
        },
    }


def parse_bool(value: str) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in FACT_NAMES:
        parser.add_argument(f"--{name.replace('_', '-')}", type=parse_bool)
    args = parser.parse_args(argv)
    supplied = [getattr(args, name) is not None for name in FACT_NAMES]
    if any(supplied) and not all(supplied):
        parser.error("supply all Intel MEI fix-effect arguments or none")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    state = None
    if getattr(args, FACT_NAMES[0]) is not None:
        state = {name: getattr(args, name) for name in FACT_NAMES}
    payload = json.dumps(build_report(state), indent=2, sort_keys=True).encode("ascii") + b"\n"
    sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
