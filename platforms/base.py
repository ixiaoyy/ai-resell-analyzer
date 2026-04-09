from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class PlatformCapability:
    code: str
    description: str


@dataclass(frozen=True, slots=True)
class PlatformDescriptor:
    code: str
    display_name: str
    roles: tuple[str, ...]
    capabilities: tuple[PlatformCapability, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)

    def supports_role(self, role: str) -> bool:
        return role in self.roles

    def supports_capability(self, capability_code: str) -> bool:
        return any(capability.code == capability_code for capability in self.capabilities)


class PlatformAdapter(Protocol):
    descriptor: PlatformDescriptor

    def list_platform_codes(self) -> tuple[str, ...]:
        ...
