"""Button platform for the LYWSD02 / LYWSD02MMC integration."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import async_sync_lywsd02
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sync-time button for a config entry."""
    async_add_entities([LywsdSyncTimeButton(entry)])


class LywsdSyncTimeButton(ButtonEntity):
    """Button that syncs a LYWSD02/LYWSD02MMC's clock on press."""

    _attr_has_entity_name = True
    _attr_name = "Sync time"
    _attr_icon = "mdi:clock-check-outline"

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the button for one configured device."""
        self._mac = entry.data[CONF_MAC]
        self._attr_unique_id = f"{self._mac}_sync_time"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._mac)},
            name=entry.title,
            manufacturer="Xiaomi",
            model="LYWSD02 / LYWSD02MMC",
        )

    async def async_press(self) -> None:
        """Sync the device's clock to Home Assistant's current time.

        Raises HomeAssistantError (via async_sync_lywsd02) on failure, which
        Home Assistant surfaces as a failed-action notice in the UI.
        """
        await async_sync_lywsd02(self.hass, self._mac)
