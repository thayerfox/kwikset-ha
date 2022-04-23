"""Kwikset device object"""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from distutils.util import strtobool

from aiokwikset.api import API
from aiokwikset.errors import RequestError
from async_timeout import timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .const import DOMAIN as KWIKSET_DOMAIN, LOGGER

class KwiksetDeviceDataUpdateCoordinator(DataUpdateCoordinator):
    """Kwikset device object"""

    def __init__(
        self, hass: HomeAssistant, api_client: API, device_id: str
    ):
        """Initialize the device"""
        self.hass: HomeAssistantType = hass
        self.api_client: API = api_client
        self._kwikset_device_id: str = device_id
        self._manufacturer: str = "Kwikset"
        self._device_information: Optional[Dict[str, Any]] | None = None
        super().__init__(
            hass,
            LOGGER,
            name=f"{KWIKSET_DOMAIN}-{device_id}",
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self):
        """Update data via library"""
        try:
            async with timeout(10):
                await asyncio.gather(
                    *[self._update_device()]
                )
        except (RequestError) as error:
            raise UpdateFailed(error) from error

    @property
    def id(self) -> str:
        """Return device id"""
        return self._kwikset_device_id

    @property
    def device_name(self) -> str:
        """Return device name."""
        return self._device_information["devicename"]

    @property
    def manufacturer(self) -> str:
        """Return manufacturer for device"""
        return self._manufacturer

    @property
    def model(self) -> str:
        """Return model for device"""
        return self._device_information["modelnumber"]

    @property
    def battery_percentage(self) -> int:
        """Return device battery percentage"""
        return self._device_information["batterypercentage"]

    @property
    def firmware_version(self) -> str:
        """Return the firmware version for the device."""
        return self._device_information["firmwarebundleversion"]

    @property
    def serial_number(self) -> str:
        """Return the serial number for the device."""
        return self._device_information["serialnumber"]

    async def _update_device(self, *_) -> None:
        """Update the device information from the API"""
        self._device_information = await self.api_client.device.get_device_info(
            self._kwikset_device_id
        )
        LOGGER.debug("Kwikset device data: %s", self._device_information)