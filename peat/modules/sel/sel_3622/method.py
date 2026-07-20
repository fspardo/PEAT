"""
Code for handling methods
"""

from dataclasses import dataclass
from types import FunctionType
from typing import Any

from loguru import logger

from peat import DeviceData

from .http import HTTP3622


class AdvancedRange:
    """An inclusive range type for versioning."""

    low: int | None
    high: int | None

    def __init__(self, low: int | None = None, high: int | None = None):
        self.low = low
        self.high = high

    def __contains__(self, value: int) -> bool:
        result = True

        if self.low:
            result = value >= self.low

        if self.high and result:
            result = self.high >= value

        return result


def irange(low: int | None = None, high: int | None = None) -> AdvancedRange:
    return AdvancedRange(low, high)


def check_firmware_compat(ver: int, ranges: list[AdvancedRange | int]) -> bool:
    for r in ranges:
        if isinstance(r, AdvancedRange):
            if ver in r:
                return True
        else:
            if ver == r:
                return True

    return False


class Method:
    """Handles methods and compatibility"""

    handler: FunctionType
    attempts: int
    for_device: list[str]
    for_firmware: list[AdvancedRange | int]

    def __init__(
        self,
        handler: FunctionType,
        attempts: int = 3,
        for_device: list[str] = [],
        for_firmware: list[AdvancedRange | int] = [],
    ):
        self.handler = handler
        self.attempts = attempts
        self.for_device = for_device
        self.for_firmware = for_firmware

    def handle(self, dev: DeviceData, session: HTTP3622) -> dict[str, Any]:
        device = dev._cache["DEVICE"]
        firmware = dev._cache["VERSION"]

        logger.debug(f"Device: {device} ({self.for_device})")
        logger.debug(f"Firmware: {firmware} ({self.for_firmware})")

        if len(self.for_device) > 0 and device not in self.for_device:
            raise Exception("Incompatible device")
        elif len(self.for_firmware) > 0 and check_firmware_compat(
            firmware, self.for_firmware
        ):
            raise Exception("Incompatible firmware")

        ex: Exception | None = None
        for a in range(self.attempts):
            try:
                return self.handler(dev, session)
            except Exception as e:
                ex = e

        raise (
            ex
            if isinstance(ex, Exception)
            else Exception(f"Failed to run method {self.handler.__name__}")
        )
