from __future__ import annotations

from platforms.base import PlatformAdapter, PlatformCapability, PlatformDescriptor
from platforms.registry import register_many

DEMAND_LISTING = PlatformCapability(code="demand_listing", description="Supports demand-side listing collection")
SUPPLY_LISTING = PlatformCapability(code="supply_listing", description="Supports supply-side listing collection")
ENGAGEMENT_SIGNAL = PlatformCapability(code="engagement_signal", description="Provides engagement or sales signals")
DROPSHIP_SIGNAL = PlatformCapability(code="dropship_signal", description="Provides dropship-related supplier signals")


class StaticPlatformAdapter:
    def __init__(self, descriptor: PlatformDescriptor, aliases: tuple[str, ...] = ()) -> None:
        self.descriptor = descriptor
        self._aliases = aliases

    def list_platform_codes(self) -> tuple[str, ...]:
        return (self.descriptor.code, *self._aliases)


DEFAULT_ADAPTERS: tuple[PlatformAdapter, ...] = (
    StaticPlatformAdapter(
        PlatformDescriptor(
            code="xianyu",
            display_name="闲鱼",
            roles=("demand", "sell_target"),
            capabilities=(DEMAND_LISTING, ENGAGEMENT_SIGNAL),
            metadata={"family": "c2c", "price_sensitivity": "medium"},
        )
    ),
    StaticPlatformAdapter(
        PlatformDescriptor(
            code="pinduoduo",
            display_name="拼多多",
            roles=("demand", "sell_target"),
            capabilities=(DEMAND_LISTING, ENGAGEMENT_SIGNAL),
            metadata={"family": "marketplace", "price_sensitivity": "high"},
        )
    ),
    StaticPlatformAdapter(
        PlatformDescriptor(
            code="1688",
            display_name="1688",
            roles=("supply",),
            capabilities=(SUPPLY_LISTING, DROPSHIP_SIGNAL),
            metadata={"family": "wholesale", "price_sensitivity": "low"},
        ),
        aliases=("alibaba_1688",),
    ),
)


def register_default_platforms() -> None:
    register_many(DEFAULT_ADAPTERS)
