"""Base provider interface (structural typing only — no runtime coupling)."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class Provider(Protocol):
    """Every provider declares its name; selection is config-driven (ADR-005)."""

    name: str
