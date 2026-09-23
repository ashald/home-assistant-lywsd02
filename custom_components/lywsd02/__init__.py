from __future__ import annotations

import time
import struct
import logging

from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.typing import ConfigType
from homeassistant.components import bluetooth
from homeassistant.util import dt as dt_util

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.BUTTON]

_LOGGER = logging.getLogger(__name__)


_UUID_TIME = 'EBE0CCB7-7A0A-4B0C-8A1A-6FF2997DA3A6'
_UUID_TEMO = 'EBE0CCBE-7A0A-4B0C-8A1A-6FF2997DA3A6'

def get_localized_timestamp(tz_offset_hours: int) -> int:
    """Return a 'fake UTC' epoch carrying only the sub-hour remainder of the offset.

    The device itself applies `tz_offset` (whole hours, written alongside this
    timestamp in the same characteristic) on top of whatever epoch it is
    given to compute the displayed wall-clock time. Baking the full local
    offset into the timestamp *and* sending the same offset again via
    `tz_offset` double-counts it - e.g. at UTC+3 the device ends up 3 hours
    ahead of the correct time, since both applications add the offset.

    Only the fractional-hour remainder (relevant for offsets like UTC+5:30)
    needs to ride in the timestamp; whole hours belong solely in `tz_offset`.

    Home Assistant's own configured time zone is used (Settings -> General ->
    Time Zone, via dt_util), not the host machine's OS time zone - those
    commonly diverge, since containerized installs typically stay on UTC at
    the OS level regardless of what's configured in HA itself.
    """
    now = int(time.time())
    offset_seconds = dt_util.now().utcoffset().total_seconds()
    remainder_seconds = offset_seconds - tz_offset_hours * 3600
    return now + int(remainder_seconds)


async def async_sync_lywsd02(
    hass: HomeAssistant,
    mac: str,
    *,
    tz_offset: int | None = None,
    timestamp: int | None = None,
    temp_mode: str | None = None,
    clock_mode: int | None = None,
    timeout: int = 60,
) -> None:
    """Connect to a LYWSD02/LYWSD02MMC and sync its clock.

    Optionally also sets the display's temperature unit and, on the
    LYWSD02MMC only, its 12/24-hour clock face. Shared by the legacy
    `set_time` service and the config-entry "Sync time" button.

    Raises HomeAssistantError if the device can't be found or connected to.
    """
    mac = mac.upper()
    tz_offset_given = tz_offset is not None
    if tz_offset is None:
        tz_offset = round(dt_util.now().utcoffset().total_seconds() / 3600)

    ble_device = bluetooth.async_ble_device_from_address(
        hass,
        mac,
        connectable=True
    )

    if not ble_device:
        raise HomeAssistantError(f"Could not find '{mac}'.")

    _LOGGER.info(f"Found '{ble_device}' - Attempting to update time.")

    temo_set = False
    temo = (temp_mode or "").upper()
    if temo in ('C', 'F'):
        data_temp_mode = struct.pack('B', (0x01 if temo == 'F' else 0xFF))
        _LOGGER.debug("Will set temp_mode")
        temo_set = True

    ckmo_set = clock_mode in (12, 24)
    if ckmo_set:
        data_clock_mode = struct.pack('IHB', 0, 0, 0xaa if clock_mode == 12 else 0x00)
        _LOGGER.debug("Will set clock_mode")

    # A plain BleakClient regularly fails on the first attempt when the
    # device is reached through an ESPHome/Shelly Bluetooth proxy rather
    # than a local adapter. establish_connection retries and handles the
    # proxy's connection slots; `timeout` is forwarded to the client.
    client = await establish_connection(
        BleakClientWithServiceCache,
        ble_device,
        mac,
        timeout=timeout,
    )
    try:
        if timestamp is not None:
            resolved_timestamp = int(timestamp)
        elif tz_offset_given:
            # A caller-supplied tz_offset with no timestamp means they want
            # the device to apply that offset itself - send the raw UTC
            # epoch rather than baking in HA's own offset on top of it.
            resolved_timestamp = int(time.time())
        else:
            resolved_timestamp = get_localized_timestamp(tz_offset)

        data = struct.pack('Ib', resolved_timestamp, tz_offset)
        await client.write_gatt_char(_UUID_TIME, data)
        if temo_set:
            await client.write_gatt_char(_UUID_TEMO, data_temp_mode)
        if ckmo_set:
            # 12/24-hour switching writes a 7-byte clock-format value to the
            # time characteristic. This is validated against a Mi Home app
            # capture on the LYWSD02MMC (0xAA => 12h, 0x00 => 24h, see #10),
            # but on the plain LYWSD02 the same characteristic is a fixed
            # 5-byte time attribute and rejects it with "Invalid attribute
            # length". Treat a rejection as "unsupported on this model" and
            # warn rather than failing the call - the time is already set.
            try:
                await client.write_gatt_char(_UUID_TIME, data_clock_mode)
            except BleakError as err:
                _LOGGER.warning(
                    "clock_mode (12/24-hour) could not be set on '%s': it is "
                    "only supported on the LYWSD02MMC and this device "
                    "rejected the write (%s). The time was set successfully "
                    "- remove the 'clock_mode' parameter to silence this "
                    "warning.",
                    mac, err,
                )
    finally:
        await client.disconnect()

    _LOGGER.info(f"Done - refreshed time on '{mac}' to '{resolved_timestamp}' with offset of '{tz_offset}' hours.")


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """
    Based off https://github.com/h4/lywsd02
    """

    async def set_time(call: ServiceCall) -> None:
        mac = call.data.get('mac')
        if not mac:
            _LOGGER.error(f"The 'mac' parameter is missing from service call: {call.data}.")
            return

        try:
            await async_sync_lywsd02(
                hass,
                mac,
                tz_offset=call.data.get('tz_offset'),
                timestamp=call.data.get('timestamp'),
                temp_mode=call.data.get('temp_mode'),
                clock_mode=call.data.get('clock_mode', 0),
                timeout=int(call.data.get('timeout', 60)),
            )
        except HomeAssistantError as err:
            _LOGGER.error(str(err))

    hass.services.async_register(DOMAIN, 'set_time', set_time)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a LYWSD02/LYWSD02MMC from a config entry.

    This only adds the "Sync time" button; the `lywsd02.set_time` service
    registered in async_setup above keeps working exactly as before and does
    not require a config entry.
    """
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
