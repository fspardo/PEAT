"""
Code for handling methods
"""

from dataclasses import dataclass
from types import FunctionType
from typing import Any
from peat import DeviceData
from .http import HTTP3622
from loguru import logger


def check_firmware_compat(ver: int, ranges: list[range | int]) -> bool:
    for r in ranges:
        if isinstance(r, range):
            if ver in r:
                return True
        else:
            if ver == r:
                return True

    return False


class Method:
    handler: FunctionType
    attempts: int
    for_device: list[str]
    for_firmware: list[range | int]

    def __init__(
        self,
        handler: FunctionType,
        attempts: int = 3,
        for_device: list[str] = [],
        for_firmware: list[range | int] = [],
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
