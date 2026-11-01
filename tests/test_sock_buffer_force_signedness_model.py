from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/uk_fw/sock_buffer_force_signedness_model.py"
SPEC = importlib.util.spec_from_file_location("sock_buffer_force_signedness_model", TOOL)
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)
OPTIONS = tuple(M.PRE_RECORDED_TARGET_STATE)
SIGNED_FACTS = OPTIONS[2:8]


def args_for(state: dict[str, bool]) -> list[str]:
    result: list[str] = []
    for name in OPTIONS:
        result += [f"--{name.replace('_', '-')}", str(state[name]).lower()]
    return result


class SockBufferForceSignednessModelTests(unittest.TestCase):
    def test_pre_recorded_state_rejects_named_premise(self) -> None:
        result = M.classify_signedness(**M.PRE_RECORDED_TARGET_STATE)
        self.assertTrue(result["both_force_routes_require_cap_net_admin"])
        self.assertTrue(result["complete_signed_clamp_effects_present"])
        self.assertFalse(result["vulnerable_unsigned_maximum_effect_present"])
        self.assertFalse(result["cve_2016_9793_negative_buffer_premise_present"])
        self.assertTrue(result["cve_2016_9793_rejected_by_supplied_machine_effects"])
        self.assertFalse(result["cve_2016_9793_not_rejected_by_complete_machine_effects"])
        for name, value in result.items():
            if name.endswith("_observed"):
                self.assertIsNone(value)

    def test_exhaustive_boolean_domain(self) -> None:
        for bits in itertools.product((False, True), repeat=len(OPTIONS)):
            state = dict(zip(OPTIONS, bits))
            with self.subTest(bits=bits):
                result = M.classify_signedness(**state)
                gates = state[OPTIONS[0]] and state[OPTIONS[1]]
                signed = all(state[name] for name in SIGNED_FACTS)
                vulnerable = state[OPTIONS[-1]]
                rejected = signed and not vulnerable
                premise = False if rejected else (True if vulnerable else None)
                self.assertEqual(
                    result["both_force_routes_require_cap_net_admin"], gates
                )
                self.assertEqual(
                    result["complete_signed_clamp_effects_present"], signed
                )
                self.assertEqual(
                    result["vulnerable_unsigned_maximum_effect_present"], vulnerable
                )
                self.assertEqual(
                    result["cve_2016_9793_negative_buffer_premise_present"], premise
                )
                self.assertEqual(
                    result["cve_2016_9793_rejected_by_supplied_machine_effects"],
                    rejected,
                )
                self.assertEqual(
                    result["cve_2016_9793_not_rejected_by_complete_machine_effects"],
                    not rejected,
                )

    def test_each_signed_effect_is_required_for_rejection(self) -> None:
        for name in SIGNED_FACTS:
            state = dict(M.PRE_RECORDED_TARGET_STATE)
            state[name] = False
            with self.subTest(name=name):
                result = M.classify_signedness(**state)
                self.assertIsNone(
                    result["cve_2016_9793_negative_buffer_premise_present"]
                )
                self.assertFalse(
                    result["cve_2016_9793_rejected_by_supplied_machine_effects"]
                )

    def test_capability_gates_do_not_replace_signedness_facts(self) -> None:
        state = dict(M.PRE_RECORDED_TARGET_STATE)
        state[OPTIONS[0]] = False
        state[OPTIONS[1]] = False
        result = M.classify_signedness(**state)
        self.assertFalse(result["both_force_routes_require_cap_net_admin"])
        self.assertTrue(result["cve_2016_9793_rejected_by_supplied_machine_effects"])

    def test_explicit_unsigned_effect_marks_premise_present(self) -> None:
        state = dict(M.PRE_RECORDED_TARGET_STATE)
        state[OPTIONS[-1]] = True
        result = M.classify_signedness(**state)
        self.assertTrue(result["cve_2016_9793_negative_buffer_premise_present"])
        self.assertFalse(result["cve_2016_9793_rejected_by_supplied_machine_effects"])

    def test_rejects_wrong_keys_and_non_booleans(self) -> None:
        state = dict(M.PRE_RECORDED_TARGET_STATE)
        del state[OPTIONS[0]]
        with self.assertRaisesRegex(M.ModelError, "state keys mismatch"):
            M.classify_signedness(**state)
        state = dict(M.PRE_RECORDED_TARGET_STATE)
        state[OPTIONS[0]] = 1
        with self.assertRaisesRegex(M.ModelError, "must be a boolean"):
            M.classify_signedness(**state)

    def test_cli_complete_and_fail_closed_cases(self) -> None:
        state = dict(M.PRE_RECORDED_TARGET_STATE)
        run = subprocess.run(
            [sys.executable, str(TOOL), *args_for(state)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["classification"]["input"], state)
        option = f"--{OPTIONS[0].replace('_', '-')}"
        for argv, text in (
            ([option, "true"], "all socket-buffer signedness arguments"),
            ([option, "true", option, "false"], "only once"),
            (["--send-force-gate", "true"], "unrecognized arguments"),
            ([option, "yes"], "expected true or false"),
        ):
            with self.subTest(argv=argv):
                run = subprocess.run(
                    [sys.executable, str(TOOL), *argv],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.assertNotEqual(run.returncode, 0)
                self.assertIn(text, run.stderr)

    def test_default_output_deterministic_utf8_lf(self) -> None:
        expected = json.dumps(M.build_report(), indent=2, sort_keys=True).encode() + b"\n"
        outputs = []
        for encoding in ("ascii:strict", "latin-1:strict", "utf-16:strict"):
            env = dict(os.environ, PYTHONIOENCODING=encoding)
            run = subprocess.run(
                [sys.executable, str(TOOL)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
            self.assertEqual(run.stdout, expected)
            self.assertNotIn(b"\r", run.stdout)
            outputs.append(run.stdout)
        self.assertEqual(len(set(outputs)), 1)
        self.assertEqual(
            hashlib.sha256(outputs[0]).hexdigest(),
            "f870c510768654e861a027b42d85cdc83933fdfc9f4c3008e7cae5a556c75417",
        )

    def test_report_has_no_operational_material(self) -> None:
        encoded = json.dumps(M.build_report(), sort_keys=True).lower()
        for forbidden in (
            "0xffffffff",
            "setsockopt(",
            "socket(",
            "so_sndbufforce",
            "so_rcvbufforce",
        ):
            self.assertNotIn(forbidden, encoded)
        self.assertTrue(
            M.build_report()["claim_boundary"][
                "emits_no_socket_option_value_invocation_payload_race_command_instructions_or_firmware_bytes"
            ]
        )


if __name__ == "__main__":
    unittest.main()
