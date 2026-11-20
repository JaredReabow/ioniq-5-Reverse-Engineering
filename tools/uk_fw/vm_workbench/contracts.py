"""Frozen public contracts shared by the VM workbench modules.

This module contains types and validation only.  Runtime ownership, simulator
policy, subprocess defaults, and HTTP policy remain inside their owning modules.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping, Optional, Protocol


GUEST_WIDTH = 1920
GUEST_HEIGHT = 720
API_PREFIX = "/api/v1"


@dataclass(frozen=True)
class CommandReceipt:
    """Result of one sequenced operator command."""

    command_id: str
    accepted: bool
    state: str
    message: str
    created_ns: int
    acknowledged_ns: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-safe representation."""

        return asdict(self)


@dataclass(frozen=True)
class FrameSnapshot:
    """Metadata and bytes for one guest or explicitly labelled fixture frame."""

    sequence: int
    captured_ns: int
    width: int
    height: int
    mime_type: str
    payload: bytes
    source: str
    stale: bool


@dataclass(frozen=True)
class ModuleField:
    """One validated simulator field exposed to the operator surface."""

    name: str
    value: Any
    value_type: str
    writable: bool
    evidence: str
    choices: Optional[List[Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-safe representation."""

        return asdict(self)


@dataclass(frozen=True)
class ModuleSnapshot:
    """Current state for one module-owned simulator API."""

    module_id: str
    label: str
    transport: str
    integration: str
    fields: List[ModuleField]
    observe_label: Optional[str] = None
    diagnose_label: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-safe representation."""

        data = asdict(self)
        data["fields"] = [field.to_dict() for field in self.fields]
        return data


@dataclass(frozen=True)
class EventRecord:
    """Correlated workbench event retained in bounded memory."""

    event_id: int
    timestamp_ns: int
    correlation_id: str
    component: str
    event: str
    detail: Mapping[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-safe representation."""

        return asdict(self)


class WorkbenchBackend(Protocol):
    """Only interface the browser server may use to operate the workbench."""

    def get_status(self) -> Mapping[str, Any]:
        """Return current session state without mutating it."""

    def get_frame(self) -> FrameSnapshot:
        """Return the latest bounded guest or labelled fixture frame."""

    def send_pointer(
        self,
        *,
        action: str,
        x1: int,
        y1: int,
        x2: Optional[int] = None,
        y2: Optional[int] = None,
        correlation_id: Optional[str] = None,
    ) -> CommandReceipt:
        """Queue one click or drag in guest coordinates."""

    def observe_and_confirm_once(self, *, frame_sequence: int,
                                 correlation_id: Optional[str] = None) -> CommandReceipt:
        """Observe and confirm one operator-approved live compositor frame."""

    def send_key(
        self,
        *,
        action: str,
        key: str,
        correlation_id: Optional[str] = None,
    ) -> CommandReceipt:
        """Queue one validated key press/release operation."""

    def get_modules(self) -> List[ModuleSnapshot]:
        """Return module-owned simulator state and evidence labels."""

    def set_module_field(
        self,
        *,
        module_id: str,
        field: str,
        value: Any,
        correlation_id: Optional[str] = None,
    ) -> CommandReceipt:
        """Set one writable field through its owning module API."""

    def observe_module(
        self,
        *,
        module_id: str,
        correlation_id: Optional[str] = None,
    ) -> CommandReceipt:
        """Observe the supported module's fixed guest-side reply."""

    def diagnose_module(self, *, module_id: str, correlation_id: Optional[str] = None) -> CommandReceipt:
        """Run a module's fixed, bounded diagnostic if declared."""

    def get_events(self, *, after_id: int, limit: int) -> List[EventRecord]:
        """Return ordered correlated events after ``after_id``."""

    def shutdown(self) -> CommandReceipt:
        """Boundedly stop only the VM process owned by this backend."""
