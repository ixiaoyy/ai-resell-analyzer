from __future__ import annotations

from collections.abc import Iterable

from platforms.base import PlatformAdapter, PlatformDescriptor


class PlatformRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, PlatformAdapter] = {}

    def register(self, adapter: PlatformAdapter) -> None:
        for code in adapter.list_platform_codes():
            self._adapters[code] = adapter

    def get(self, code: str) -> PlatformAdapter | None:
        return self._adapters.get(code)

    def descriptors(self, role: str | None = None) -> list[PlatformDescriptor]:
        descriptors: dict[str, PlatformDescriptor] = {}
        for adapter in self._adapters.values():
            descriptor = adapter.descriptor
            if role is not None and not descriptor.supports_role(role):
                continue
            descriptors[descriptor.code] = descriptor
        return sorted(descriptors.values(), key=lambda item: item.code)

    def codes(self, role: str | None = None) -> tuple[str, ...]:
        return tuple(descriptor.code for descriptor in self.descriptors(role=role))


registry = PlatformRegistry()


def register_many(adapters: Iterable[PlatformAdapter]) -> None:
    for adapter in adapters:
        registry.register(adapter)
