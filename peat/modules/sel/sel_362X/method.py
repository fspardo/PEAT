"""
Code for handling methods
"""

from dataclasses import dataclass
from types import FunctionType
from typing import Any

from loguru import logger

from peat import DeviceData

from .http import HTTP362X


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

    def __str__(self) -> str:
        if self.low and self.high:
            return f"{self.low} - {self.high}"
        elif self.low:
            return f">= {self.low}"
        elif self.high:
            return f"<= {self.high}"
        else:
            return "any"


def irange(low: int | None = None, high: int | None = None) -> AdvancedRange:
    return AdvancedRange(low, high)


class Method:
    """Handles methods and compatibility"""

    handler: FunctionType
    attempts: int
    for_device: list[str]
    for_firmware: AdvancedRange

    def __init__(
        self,
        handler: FunctionType,
        attempts: int = 3,
        for_device: list[str] = [],
        for_firmware: AdvancedRange = AdvancedRange(),
    ):
        self.handler = handler
        self.attempts = attempts
        self.for_device = for_device
        self.for_firmware = for_firmware

    def iscompat(self, dev: DeviceData) -> bool:
        device = dev._cache["DEVICE"]
        firmware = dev._cache["VERSION"]

        if len(self.for_device) > 0 and device not in self.for_device:
            return False
        elif firmware not in self.for_firmware:
            return False

        return True

    def handle(self, dev: DeviceData, session: HTTP362X) -> dict[str, Any] | None:
        if not self.iscompat(dev):
            return None

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
