#!/usr/bin/env python3.13
"""make_run_manifest.py - generate a run manifest from the real bytes on disk.

Astra C10 rejected a hand-written manifest because it proves nothing: the check must describe the
files that actually exist, computed from those files. More importantly, C11 established that the
manifest proves the *named driver file matched* - it never proves the driver ran. This tool exists so
the "matched" half is at least real.

The manifest is a small text format the in-guest helper parses:

    RUN id=<identifier>
    DRIVER path=<path> sha256=<64 hex>
    HELPER path=<path> sha256=<64 hex>

`path` may contain spaces; the helper's parser spans `path=` to ` sha256=`, so a path with spaces is
safe. (A first draft of the helper truncated at the first space, and on this project the repository
path itself contains spaces, so the truncation resolved to an existing directory and hashed to
nothing.)

Usage:
    make_run_manifest.py --run-id <id> --driver PATH --helper PATH --output PATH
    make_run_manifest.py --run-id <id> --driver PATH --helper PATH          # print to stdout
    make_run_manifest.py --run-id <id> --driver PATH --helper PATH \
        --driver-guest-path /interval-run.sh --helper-guest-path /interval-capture.sh

Exit status: 0 written, 2 usage, 3 a named file is missing or unreadable.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(
    run_id: str,
    driver: Path,
    helper: Path,
    driver_guest_path: str | None = None,
    helper_guest_path: str | None = None,
) -> str:
    """Return the manifest text. Raises FileNotFoundError if a named file is absent.

    The digest is always computed from the host file. The `path=` field may name a DIFFERENT path,
    which is required in practice: inside the guest the staged files live at paths like
    `/interval-run.sh`, and the helper checks that the manifest's driver path is readable and matches
    there. Recording the host path would make every in-guest check fail for the wrong reason.
    """
    for label, path in (("driver", driver), ("helper", helper)):
        if not path.is_file():
            raise FileNotFoundError(f"{label} is not a regular file: {path}")
    driver_field = driver_guest_path or str(driver)
    helper_field = helper_guest_path or str(helper)
    return (
        f"RUN id={run_id}\n"
        f"DRIVER path={driver_field} sha256={sha256_of(driver)}\n"
        f"HELPER path={helper_field} sha256={sha256_of(helper)}\n"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", required=True, help="identifier for this run")
    ap.add_argument("--driver", required=True, type=Path, help="the retained driver script")
    ap.add_argument("--helper", required=True, type=Path, help="the frozen capture helper")
    ap.add_argument("--driver-guest-path", default=None,
                    help="path recorded in the manifest for the driver, if different from the host path")
    ap.add_argument("--helper-guest-path", default=None,
                    help="path recorded in the manifest for the helper, if different from the host path")
    ap.add_argument("--output", type=Path, default=None, help="write here instead of stdout")
    args = ap.parse_args(argv)

    if not args.run_id.strip():
        print("error: --run-id must not be empty", file=sys.stderr)
        return 2

    try:
        text = build_manifest(
            args.run_id, args.driver, args.helper,
            args.driver_guest_path, args.helper_guest_path,
        )
    except (FileNotFoundError, PermissionError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    if args.output is None:
        sys.stdout.write(text)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
