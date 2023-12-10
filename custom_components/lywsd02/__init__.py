from __future__ import annotations

import time
import struct
import logging

from datetime import datetime

from bleak import BleakClient

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers.typing import ConfigType
from homeassistant.components import bluetooth

DOMAIN = "lywsd02"

_LOGGER = logging.getLogger(__name__)

_UUID_TIME = 'EBE0CCB7-7A0A-4B0C-8A1A-6FF2997DA3A6'

def get_localized_timestamp():
    now = int(time.time())
    utc = datetime.utcfromtimestamp(now)
    local = datetime.fromtimestamp(now)
    diff = (utc-local).seconds
    return now - diff

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """
    Based off https://github.com/h4/lywsd02
    """
    
    @callback
    async def set_time(call: ServiceCall) -> None:
        mac = call.data['mac'].upper()
        if not mac:
            _LOGGER.error(f"The 'mac' parameter is missinf from service call: {call.data}.")
            return

        tz_offset = call.data.get('tz_offset', 0)
        timestamp = int(
            call.data.get('timestamp') or get_localized_timestamp()
        )

        data = struct.pack('Ib', timestamp, tz_offset)

        ble_device = bluetooth.async_ble_device_from_address(
            hass,
            mac,
            connectable=True
        )

        if not ble_device:
            _LOGGER.error(f"Could not find '{mac}'.")
            return

        _LOGGER.info(f"Found '{ble_device}' - Attempting to update time.")

        async with BleakClient(ble_device) as client:
            await client.write_gatt_char(_UUID_TIME, data)

        _LOGGER.info(f"Done - refreshed time on '{mac}' to '{timestamp}' with offset of '{tz_offset}' hours.")

    hass.services.async_register(DOMAIN, 'set_time', set_time)

    return True
