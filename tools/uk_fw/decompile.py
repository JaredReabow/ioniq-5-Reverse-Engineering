#!/usr/bin/env python3
"""Decompile selected functions of a recovered vendor binary with Ghidra.

The retained listings are hand-annotated disassembly excerpts; this tool produces
the matching C for a named function or an address, without a GUI and without a
system-wide install. Ghidra and a JDK are looked up in the environment first.

    python3 tools/uk_fw/decompile.py --binary work/.../ApplicationManager \
        --select 0x190c70,0x19108d

Nothing is written outside the project: the Ghidra project, the decompiled output
and the log all live under ignored `work/`.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
SCRIPT_DIR = HERE / "ghidra"
DEFAULT_GHIDRA = Path.home() / ".local/tools/ghidra"
DEFAULT_JAVA_HOME = Path.home() / ".local/tools/jdk21"


class DecompileError(RuntimeError):
    pass


def find_ghidra(explicit: Path | None) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    override = os.environ.get("IONIQ_GHIDRA")
    if override:
        candidates.append(Path(override))
    candidates.append(DEFAULT_GHIDRA)
    for candidate in candidates:
        headless = candidate / "support/analyzeHeadless"
        if headless.is_file():
            return candidate
    raise DecompileError(
        "Ghidra was not found; set IONIQ_GHIDRA or --ghidra to an unpacked release"
    )


def java_environment() -> dict[str, str]:
    """analyzeHeadless needs a JDK; prefer the project-local one when installed."""
    env = os.environ.copy()
    if env.get("JAVA_HOME") and (Path(env["JAVA_HOME"]) / "bin/java").is_file():
        return env
    for candidate in (DEFAULT_JAVA_HOME,):
        if (candidate / "bin/java").is_file():
            env["JAVA_HOME"] = str(candidate)
            env["PATH"] = str(candidate / "bin") + os.pathsep + env.get("PATH", "")
            return env
    if shutil.which("java"):
        return env
    raise DecompileError("a JDK is required; set JAVA_HOME or install one locally")


def project_output(path: Path) -> Path:
    path = path.resolve()
    if path == PROJECT or not path.is_relative_to(PROJECT):
        raise DecompileError(f"output must be a subdirectory of the project: {path}")
    return path


def decompile(binary: Path, select: str, out: Path, ghidra: Path,
              project_dir: Path, timeout: int, limit: int,
              reuse: bool = False, analysis_timeout: int = 0,
              discard: bool = False, max_cpu: int = 0,
              slice_spec: str = "", function_timeout: int = 0) -> dict[str, object]:
    binary = binary.resolve()
    if not binary.is_file():
        raise DecompileError(f"binary not found: {binary}")
    out = project_output(out)
    project_dir = project_output(project_dir)
    out.mkdir(parents=True, exist_ok=True)
    project_dir.mkdir(parents=True, exist_ok=True)
    env = java_environment()
    headless = str(ghidra / "support/analyzeHeadless")
    if select.upper() == "STUBBORN":
        # Final pass: retry after re-disassembly, then publish a listing so a refused
        # function still has an artifact and its reason.
        inventory = out / "functions.tsv"
        if not inventory.is_file():
            raise DecompileError(f"STUBBORN needs an inventory: {inventory}")
        script_args = ["-scriptPath", str(SCRIPT_DIR), "-postScript",
                       "DecompileStubborn.java", str(out), str(inventory),
                       slice_spec or "0/1", str(function_timeout or 1800)]
    elif select.upper() == "MISSING":
        # The tail pass has its own script: it trusts the inventory instead of the
        # resume predicate, which is what made the general pass disagree with it.
        inventory = out / "functions.tsv"
        if not inventory.is_file():
            raise DecompileError(f"MISSING needs an inventory: {inventory}")
        script_args = ["-scriptPath", str(SCRIPT_DIR), "-postScript",
                       "DecompileMissing.java", str(out), str(inventory),
                       slice_spec or "0/1", str(function_timeout or 90)]
    else:
        script_args = ["-scriptPath", str(SCRIPT_DIR), "-postScript",
                       "DecompileSymbols.java", str(out), select, str(limit or 0),
                       slice_spec or "0/1", str(function_timeout or 0)]
    if reuse and (project_dir / "ioniq.rep").exists():
        # Re-importing a 50 MB binary costs minutes; reuse the analysed project.
        command = [headless, str(project_dir), "ioniq", "-process", binary.name,
                   "-noanalysis"] + script_args
    else:
        command = [headless, str(project_dir), "ioniq", "-import", str(binary)] + script_args
        if analysis_timeout > 0:
            # A 143 MB binary can analyse for hours; bound it and keep whatever
            # functions were discovered so a later --reuse run can continue.
            command += ["-analysisTimeoutPerFile", str(analysis_timeout)]
        if max_cpu > 0:
            # Ghidra's parallel analyzers are the only intra-program parallelism;
            # a single program still averages about one core.
            command += ["-max-cpu", str(max_cpu)]
        if discard:
            command += ["-deleteProject"]
    timed_out = False
    try:
        finished = subprocess.run(command, cwd=PROJECT, env=env, capture_output=True,
                                  text=True, timeout=timeout, check=False)
        returncode = finished.returncode
        log = (finished.stdout or "") + (finished.stderr or "")
    except subprocess.TimeoutExpired as expired:
        # A killed headless run leaves a half-imported project and partial output; the
        # caller has to be able to tell that apart from a finished one.
        timed_out = True
        returncode = -1
        log = f"headless run exceeded {timeout}s\n" + (
            (expired.stdout or b"").decode("utf-8", "replace")[-2000:]
            if isinstance(expired.stdout, bytes) else (expired.stdout or "")[-2000:])
    (out / "ghidra.log").write_text(log, encoding="utf-8")
    produced = sorted(out.glob("*.c"))
    produced_total = len(produced)
    if limit and len(produced) > limit:
        produced = produced[:limit]
    # A 140k-file listing is noise, not a report; the count carries the information.
    sample = [path.name for path in produced[:40]]
    failures_path = out / "failures.tsv"
    failure_rows = 0
    if failures_path.is_file():
        with failures_path.open(encoding="utf-8", errors="replace") as handle:
            failure_rows = sum(1 for _ in handle)
    # The script reports its own accounting; a resumed run that decompiled nothing
    # but skipped everything already done is a success, not a failure.
    # Only the script's summary line counts: the per-entry lines read "failed <entry> :",
    # so a loose "failed (\d+)" search would report the first digits of an address.
    counters = {"decompiled": None, "skipped": None, "failed": None}
    summary = re.search(r"decompiled (\d+) function\(s\), skipped (\d+), failed (\d+)", log)
    if summary:
        counters["decompiled"] = int(summary.group(1))
        counters["skipped"] = int(summary.group(2))
        counters["failed"] = int(summary.group(3))
    return {
        "decompiled": counters["decompiled"],
        "skipped": counters["skipped"],
        "failed": counters["failed"],
        "binary": str(binary),
        "select": select,
        "out": str(out),
        "functions": produced_total,
        "failure_rows": failure_rows,
        "log_path": str(out / "ghidra.log"),
        "files": sample,
        "returncode": returncode,
        "timed_out": timed_out,
        "log_tail": log.strip().splitlines()[-6:],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--select", default="ALL",
                        help="ALL, a function-name substring, or 0xADDR,0xADDR")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--ghidra", type=Path, default=None)
    parser.add_argument("--project", type=Path, default=PROJECT / "work/ghidra-project")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--limit", type=int, default=0,
                        help="maximum functions to decompile (0 = no cap)")
    parser.add_argument("--reuse", action="store_true",
                        help="reuse an existing analysed Ghidra project")
    parser.add_argument("--analysis-timeout", type=int, default=0,
                        help="bound headless auto-analysis (seconds per file)")
    parser.add_argument("--discard", action="store_true",
                        help="delete the Ghidra project after the run")
    parser.add_argument("--slice", default="",
                        help="i/n: decompile only every n-th function, for parallel workers")
    parser.add_argument("--function-timeout", type=int, default=0,
                        help="per-function decompiler timeout in seconds (0 = Ghidra default of 90)")
    parser.add_argument("--max-cpu", type=int, default=0,
                        help="cores for Ghidra's parallel analyzers (0 = Ghidra default)")
    args = parser.parse_args(argv)
    out = args.out or PROJECT / "work/decompiled" / args.binary.name
    try:
        report = decompile(args.binary, args.select, out, find_ghidra(args.ghidra),
                           args.project, args.timeout, args.limit, args.reuse,
                           args.analysis_timeout, args.discard, args.max_cpu,
                           args.slice, args.function_timeout)
    except (DecompileError, OSError, subprocess.SubprocessError) as exc:
        print(f"decompile: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    if report.get("timed_out"):
        # Distinct code: the caller must not read a truncated run as a finished one.
        return 3
    if report["returncode"] != 0:
        return 1
    if report["failed"] and not report["decompiled"] and not report["skipped"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
