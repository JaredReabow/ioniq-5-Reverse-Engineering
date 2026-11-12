#!/usr/bin/env python3
"""Serve a disk image while changing selected byte ranges between read sweeps.

This module implements the nbdkit Python API v2.  The baseline image is always
the source of bytes outside configured regions.  Within a region, reads use the
baseline until the configured sweep and use the replacement from that sweep
onward.  A request that crosses either edge of a region is split so bytes
outside the region can never be sourced from the replacement file.

Configuration keys accepted by nbdkit are ``baseline``, ``regions``, ``log``
and ``reads``.  The regions file is a JSON list.  Each item contains ``off``,
``len``, ``evil``, optional ``switch_after_pass`` (default 2), and optional
``mode`` (``benign_then_evil`` or ``evil_then_benign``).
"""

from __future__ import annotations

import builtins
import json
import os
from pathlib import Path
import sys
import threading
import time
from typing import BinaryIO


API_VERSION = 2  # Required by nbdkit's Python plugin API.
TOOL_VERSION = "1.0.0"


class DynamicMediaError(RuntimeError):
    """Raised when the dynamic-media configuration is unsafe or incomplete."""


class _Region:
    """Own the policy and live read-sweep state for one replacement range."""

    VALID_MODES = frozenset({"benign_then_evil", "evil_then_benign"})

    def __init__(self, value: dict[str, object]) -> None:
        try:
            self.offset = int(value["off"])
            self.length = int(value["len"])
            self.replacement_path = Path(os.fspath(value["evil"])).expanduser().resolve()
            self.switch_after_pass = int(value.get("switch_after_pass", 2))
            self.mode = str(value.get("mode", "benign_then_evil"))
        except (KeyError, TypeError, ValueError, OSError) as exc:
            raise DynamicMediaError(f"invalid region: {exc}") from exc

        if self.offset < 0:
            raise DynamicMediaError("region offset must be non-negative")
        if self.length <= 0:
            raise DynamicMediaError("region length must be positive")
        if self.switch_after_pass <= 0:
            raise DynamicMediaError("switch_after_pass must be positive")
        if self.mode not in self.VALID_MODES:
            raise DynamicMediaError(
                f"unsupported region mode {self.mode!r}; expected one of "
                f"{sorted(self.VALID_MODES)}"
            )

        self.pass_number = 0
        self.max_seen = -1
        self.switched = False
        self.seen_start = False
        self.previous_read_near_start = False
        self.pass_reads = 0
        self.pass_baseline_bytes = 0
        self.pass_replacement_bytes = 0
        self.pass_min = 0
        self.pass_started_at = 0.0
        self.replacement: BinaryIO | None = None

    @property
    def end(self) -> int:
        """Return the exclusive end offset."""

        return self.offset + self.length

    def intersects(self, offset: int, count: int) -> bool:
        """Return whether a read overlaps this region."""

        return offset < self.end and offset + count > self.offset

    def intersection(self, offset: int, count: int) -> tuple[int, int]:
        """Return the absolute intersection start and exclusive end."""

        return max(offset, self.offset), min(offset + count, self.end)

    def use_replacement(self) -> bool:
        """Apply this region's mode to its current switched state."""

        if self.mode == "benign_then_evil":
            return self.switched
        return not self.switched


class _DynamicMediaBackend:
    """Own nbdkit configuration, file handles, policy, and cleanup."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Return the backend to a closed, unconfigured state."""

        self.config_values: dict[str, str] = {}
        self.regions: list[_Region] = []
        self.baseline: BinaryIO | None = None
        self.size = 0
        self.reads: BinaryIO | None = None
        self.last_reads_sync = 0.0
        self.lock = threading.Lock()

    def configure(self, key: str, value: str) -> None:
        """Store one nbdkit configuration value."""

        if key not in {"baseline", "regions", "log", "reads"}:
            raise DynamicMediaError(f"unknown config key {key}")
        self.config_values[key] = value

    def finish_configuration(self) -> None:
        """Load and validate every configured replacement region."""

        for required in ("baseline", "regions"):
            if required not in self.config_values:
                raise DynamicMediaError(f"missing config: {required}")

        baseline_path = Path(self.config_values["baseline"]).expanduser().resolve()
        regions_path = Path(self.config_values["regions"]).expanduser().resolve()
        if not baseline_path.is_file():
            raise DynamicMediaError(f"baseline is not a file: {baseline_path}")
        if not regions_path.is_file():
            raise DynamicMediaError(f"regions is not a file: {regions_path}")

        try:
            raw = json.loads(regions_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise DynamicMediaError(f"cannot read regions file: {exc}") from exc
        if not isinstance(raw, list) or not raw:
            raise DynamicMediaError("regions must be a non-empty JSON list")
        if not all(isinstance(item, dict) for item in raw):
            raise DynamicMediaError("each region must be a JSON object")

        candidate = [_Region(item) for item in raw]
        candidate.sort(key=lambda region: region.offset)
        baseline_size = baseline_path.stat().st_size
        previous_end = 0
        for index, region in enumerate(candidate):
            if region.end > baseline_size:
                raise DynamicMediaError(
                    f"region [{region.offset},{region.end}) exceeds baseline size {baseline_size}"
                )
            if index and region.offset < previous_end:
                raise DynamicMediaError("replacement regions must not overlap")
            try:
                replacement_size = region.replacement_path.stat().st_size
            except OSError as exc:
                raise DynamicMediaError(
                    f"cannot stat replacement {region.replacement_path}: {exc}"
                ) from exc
            if replacement_size != region.length:
                raise DynamicMediaError(
                    f"replacement size {replacement_size} does not equal region length "
                    f"{region.length}: {region.replacement_path}"
                )
            previous_end = region.end

        self.config_values["baseline"] = str(baseline_path)
        self.config_values["regions"] = str(regions_path)
        self.config_values.setdefault("log", "/var/log/ioniq-dynamic-media.log")
        self.config_values.setdefault("reads", "/var/log/ioniq-dynamic-media-reads.log")
        self.regions = candidate

    @staticmethod
    def _monotonic() -> float:
        return time.monotonic()

    def _timestamp(self) -> str:
        return f"{time.strftime('%Y-%m-%dT%H:%M:%S')} mono={self._monotonic():.3f}"

    def log(self, message: str, sync: bool = False) -> None:
        """Write bounded lifecycle information to stderr and the configured log."""

        line = f"[dynamic-media] {self._timestamp()} {message}\n"
        try:
            sys.stderr.write(line)
        except Exception:
            pass
        path = self.config_values.get("log")
        if not path:
            return
        try:
            with builtins.open(path, "ab", buffering=0) as handle:
                handle.write(line.encode("utf-8", "replace"))
                if sync:
                    os.fsync(handle.fileno())
        except OSError:
            pass

    def open(self) -> dict[str, str]:
        """Open the baseline and replacement inputs for one nbdkit session."""

        if not self.regions:
            raise DynamicMediaError("configuration is incomplete")
        try:
            self.baseline = builtins.open(self.config_values["baseline"], "rb", buffering=0)
            self.size = os.fstat(self.baseline.fileno()).st_size
            for region in self.regions:
                region.replacement = builtins.open(region.replacement_path, "rb", buffering=0)
            reads_path = self.config_values.get("reads")
            if reads_path:
                self.reads = builtins.open(reads_path, "ab", buffering=0)
                self.last_reads_sync = self._monotonic()
        except BaseException:
            self.close(None)
            raise

        session = os.urandom(4).hex()
        self.log(
            f"session start id={session} baseline={self.config_values['baseline']} "
            f"size={self.size} regions={len(self.regions)}",
            sync=True,
        )
        for region in self.regions:
            self.log(
                f"region [{region.offset},{region.end}) mode={region.mode} "
                f"switch_after_pass={region.switch_after_pass} "
                f"replacement={region.replacement_path}"
            )
        return {"session": session}

    @staticmethod
    def _read_exact(handle: BinaryIO, count: int, offset: int) -> bytes:
        """Read exactly ``count`` bytes at ``offset`` without shared seek state."""

        data = os.pread(handle.fileno(), count, offset)
        if len(data) != count:
            raise DynamicMediaError(
                f"short backing read at {offset}: expected {count}, got {len(data)}"
            )
        return data

    def _finish_pass(self, region: _Region) -> None:
        if region.pass_number < 1 or region.pass_reads <= 0:
            region.pass_reads = 0
            return
        replacement = region.pass_replacement_bytes
        baseline = region.pass_baseline_bytes
        source = "replacement" if baseline == 0 else (
            "baseline" if replacement == 0 else "mixed"
        )
        duration = self._monotonic() - region.pass_started_at
        self.log(
            f"region@{region.offset} pass={region.pass_number} end "
            f"reads={region.pass_reads} baseline_bytes={baseline} "
            f"replacement_bytes={replacement} source={source} "
            f"span=[{region.pass_min},{region.max_seen}) duration={duration:.2f}s",
            sync=True,
        )
        region.pass_reads = 0

    def _record_region_read(
        self, region: _Region, intersection_start: int, intersection_end: int
    ) -> bool:
        """Update sweep state and return whether this read uses replacement bytes."""

        # Keep the start zone proportional for small test images while capping
        # the real firmware region at 64 KiB.  A fixed 4 KiB minimum would make
        # every read of a small region "near" and hide the return-to-start edge.
        zone = max(1, min(0x10000, region.length >> 3))
        near = intersection_start <= region.offset + zone
        deep = region.max_seen >= region.offset + (region.length >> 1)
        new_sweep = near and not region.previous_read_near_start and (
            not region.seen_start or deep
        )
        region.previous_read_near_start = near

        if new_sweep:
            self._finish_pass(region)
            region.seen_start = True
            region.pass_number += 1
            region.max_seen = -1
            region.pass_reads = 0
            region.pass_baseline_bytes = 0
            region.pass_replacement_bytes = 0
            region.pass_min = intersection_start
            region.pass_started_at = self._monotonic()
            self.log(
                f"region@{region.offset} pass={region.pass_number} start "
                f"off={intersection_start} len={intersection_end - intersection_start}",
                sync=True,
            )
            if (
                region.pass_number >= region.switch_after_pass
                and not region.switched
            ):
                region.switched = True
                self.log(
                    f"region@{region.offset} switch pass={region.pass_number} "
                    f"mode={region.mode}",
                    sync=True,
                )

        region.max_seen = max(region.max_seen, intersection_end)
        use_replacement = region.use_replacement()
        count = intersection_end - intersection_start
        region.pass_reads += 1
        if use_replacement:
            region.pass_replacement_bytes += count
        else:
            region.pass_baseline_bytes += count
        region.pass_min = min(region.pass_min, intersection_start)
        self._log_read(region, intersection_start, count, use_replacement)
        return use_replacement

    def _log_read(
        self, region: _Region, offset: int, count: int, replacement: bool
    ) -> None:
        if self.reads is None:
            return
        try:
            line = (
                f"{self._monotonic():.3f} "
                f"{'R' if replacement else 'B'} off={offset} len={count} "
                f"pass={region.pass_number} region={region.offset}\n"
            )
            self.reads.write(line.encode("ascii"))
            now = self._monotonic()
            if now - self.last_reads_sync >= 1.0:
                os.fsync(self.reads.fileno())
                self.last_reads_sync = now
        except OSError:
            pass

    def read(self, count: int, offset: int) -> bytes:
        """Return one request with replacements clipped to configured regions."""

        if self.baseline is None:
            raise DynamicMediaError("backend is not open")
        if count < 0 or offset < 0 or offset + count > self.size:
            raise DynamicMediaError(
                f"read [{offset},{offset + count}) is outside image size {self.size}"
            )
        if count == 0:
            return b""

        output = bytearray(self._read_exact(self.baseline, count, offset))
        with self.lock:
            decisions: list[tuple[_Region, int, int, bool]] = []
            for region in self.regions:
                if not region.intersects(offset, count):
                    continue
                start, end = region.intersection(offset, count)
                decisions.append(
                    (region, start, end, self._record_region_read(region, start, end))
                )

        for region, start, end, use_replacement in decisions:
            if not use_replacement:
                continue
            if region.replacement is None:
                raise DynamicMediaError("replacement backing is not open")
            replacement_offset = start - region.offset
            replacement = self._read_exact(
                region.replacement, end - start, replacement_offset
            )
            output[start - offset:end - offset] = replacement
        return bytes(output)

    def close(self, handle: object) -> None:
        """Close only file handles owned by this backend instance."""

        for region in self.regions:
            self._finish_pass(region)
        if self.reads is not None:
            try:
                os.fsync(self.reads.fileno())
            except OSError:
                pass
            try:
                self.reads.close()
            except OSError:
                pass
            self.reads = None
        if self.baseline is not None:
            try:
                self.baseline.close()
            except OSError:
                pass
            self.baseline = None
        for region in self.regions:
            if region.replacement is not None:
                try:
                    region.replacement.close()
                except OSError:
                    pass
                region.replacement = None
        if isinstance(handle, dict):
            self.log(f"session end id={handle.get('session', '?')}", sync=True)


_BACKEND = _DynamicMediaBackend()


def nbdkit_dynamic_media_reset() -> None:
    """Reset module state for a new nbdkit process or an isolated test."""

    global _BACKEND
    _BACKEND.close(None)
    _BACKEND = _DynamicMediaBackend()


def nbdkit_dynamic_media_config(key: str, value: str) -> None:
    """Configure one backend value."""

    _BACKEND.configure(key, value)


def nbdkit_dynamic_media_config_complete() -> None:
    """Validate the complete backend configuration."""

    _BACKEND.finish_configuration()


def nbdkit_dynamic_media_open(readonly: bool) -> dict[str, str]:
    """Open a read-only dynamic-media session."""

    del readonly
    return _BACKEND.open()


def nbdkit_dynamic_media_get_size(handle: object) -> int:
    """Return the exported block-device size."""

    del handle
    return _BACKEND.size


def nbdkit_dynamic_media_pread(
    handle: object, buffer: object, offset: int, flags: int = 0
) -> bytes | None:
    """Implement both nbdkit's writable-buffer API and the integer test API."""

    del handle, flags
    if isinstance(buffer, int):
        return _BACKEND.read(buffer, offset)
    view = memoryview(buffer)  # type: ignore[arg-type]
    view[:] = _BACKEND.read(len(view), offset)
    return None


def nbdkit_dynamic_media_close(handle: object) -> None:
    """Close the current dynamic-media session."""

    _BACKEND.close(handle)


# nbdkit requires these exact callback names; policy remains in prefixed APIs.
def config(key: str, value: str) -> None:
    nbdkit_dynamic_media_config(key, value)


def config_complete() -> None:
    nbdkit_dynamic_media_config_complete()


def open(readonly: bool) -> dict[str, str]:
    return nbdkit_dynamic_media_open(readonly)


def get_size(handle: object) -> int:
    return nbdkit_dynamic_media_get_size(handle)


def pread(handle: object, buffer: object, offset: int, flags: int = 0) -> bytes | None:
    return nbdkit_dynamic_media_pread(handle, buffer, offset, flags)


def close(handle: object) -> None:
    nbdkit_dynamic_media_close(handle)


if __name__ == "__main__":
    print(f"nbdkit_dynamic_media.py {TOOL_VERSION}")
