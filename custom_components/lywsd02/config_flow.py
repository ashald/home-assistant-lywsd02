"""Config flow for the LYWSD02 / LYWSD02MMC integration.

This is purely opt-in: it exists to give a device a page in Settings ->
Devices & Services with a "Sync time" button. The lywsd02.set_time YAML
service registered in __init__.py works independently of this and needs no
config entry.
"""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import BluetoothServiceInfo
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_MAC, CONF_NAME

from .const import DOMAIN

_MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")


class LywsdConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LYWSD02 / LYWSD02MMC."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_mac: str | None = None
        self._discovered_name: str | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfo
    ) -> ConfigFlowResult:
        """Handle a LYWSD02/LYWSD02MMC discovered over Bluetooth."""
        mac = discovery_info.address.upper()
        await self.async_set_unique_id(mac)
        self._abort_if_unique_id_configured()
        self._discovered_mac = mac
        self._discovered_name = discovery_info.name or mac
        self.context["title_placeholders"] = {"name": self._discovered_name}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm setup of a discovered device."""
        assert self._discovered_mac is not None
        if user_input is not None:
            return self.async_create_entry(
                title=self._discovered_name or self._discovered_mac,
                data={CONF_MAC: self._discovered_mac},
            )
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={"name": self._discovered_name or ""},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual entry of a MAC address."""
        errors: dict[str, str] = {}
        if user_input is not None:
            mac = user_input[CONF_MAC].upper()
            if not _MAC_RE.match(mac):
                errors[CONF_MAC] = "invalid_mac"
            else:
                await self.async_set_unique_id(mac)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME) or mac,
                    data={CONF_MAC: mac},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MAC): str,
                    vol.Optional(CONF_NAME): str,
                }
            ),
            errors=errors,
        )
