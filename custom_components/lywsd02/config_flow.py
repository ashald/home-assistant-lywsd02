from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

DOMAIN = "lywsd02"
_SERVICE_UNIQUE_ID = "service"


class Lywsd02ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle configuration of LYWSD02 clocks."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure the LYWSD02 sync service."""

        if user_input is not None:
            await self.async_set_unique_id(_SERVICE_UNIQUE_ID)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="LYWSD02 Sync Clock",
                data={},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )
