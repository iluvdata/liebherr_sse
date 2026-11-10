"""Config flow for Liebherr Integration."""

from collections.abc import Mapping
import logging
import re
from typing import Any

import probatio
from pyliebherr import LiebherrAPI
from pyliebherr.exception import LiebherrAuthException

from homeassistant.config_entries import (
    SOURCE_REAUTH,
    SOURCE_USER,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import BooleanSelector, TextSelector
import homeassistant.helpers.issue_registry as ir
from homeassistant.loader import async_get_custom_components

from . import LiebherrConfigEntry
from .const import (
    CONF_PRESENTATION_LIGHT_AS_NUMBER,
    DOMAIN,
    URL_CONNECT_INSTRUCTIONS,
    URL_DOWNLOAD_APP,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

LIGHT_SECTION: str = "presentation_light_options"


class OptionsFlowHandler(OptionsFlowWithReload):
    """Handle options flow for Liebherr Integration."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        if user_input is not None:
            return self.async_create_entry(
                data={
                    CONF_PRESENTATION_LIGHT_AS_NUMBER: user_input[LIGHT_SECTION][
                        CONF_PRESENTATION_LIGHT_AS_NUMBER
                    ],
                }
            )
        suggested_values = {
            LIGHT_SECTION: {
                CONF_PRESENTATION_LIGHT_AS_NUMBER: self.config_entry.options.get(
                    CONF_PRESENTATION_LIGHT_AS_NUMBER, False
                ),
            },
        }
        options_schema = probatio.Schema(
            {
                probatio.Required(LIGHT_SECTION): section(
                    probatio.Schema(
                        {
                            probatio.Required(
                                CONF_PRESENTATION_LIGHT_AS_NUMBER
                            ): BooleanSelector(),
                        }
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                options_schema, suggested_values
            ),
            errors=errors,
        )


class LiebherrConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Liebherr Integration."""

    async def async_on_create_entry(self, result: ConfigFlowResult) -> ConfigFlowResult:
        """Remove the deprecation issue if present."""
        ir.async_delete_issue("liebherr", "deprecated_integration")

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            custom_components = await async_get_custom_components(self.hass)
            if custom_components.get("liebherr") is not None:
                # the legacy custom lieberr compoent is install
                for config_entry in self.hass.config_entries.async_entries("liebherr"):
                    # it's the custom integration
                    from custom_components.liebherr import LiebherrRuntimeData  # noqa: PLC0415

                    if isinstance(config_entry.runtime_data, LiebherrRuntimeData):
                        user_input = {CONF_API_KEY: config_entry.data[CONF_API_KEY]}
                        await self.hass.config_entries.async_remove(
                            config_entry.entry_id
                        )
        errors = {}
        if user_input is not None:
            # check the API key
            if not re.fullmatch("^\\S.*\\S$", user_input[CONF_API_KEY]):
                errors[CONF_API_KEY] = "whitespace_api_key"
            else:
                try:
                    api: LiebherrAPI = LiebherrAPI(
                        user_input[CONF_API_KEY], async_get_clientsession(self.hass)
                    )
                    await api.async_test_key()
                except LiebherrAuthException:
                    errors["base"] = "auth_error"
                finally:
                    if hasattr(self, "api"):
                        await api.async_close()
            if not errors:
                await self.async_set_unique_id(f"{DOMAIN}_{user_input[CONF_API_KEY]}")
                self._abort_if_unique_id_configured()
                if self.source == SOURCE_USER:
                    return self.async_create_entry(
                        title="Liebherr SmartDevice",
                        data={
                            CONF_API_KEY: user_input[CONF_API_KEY],
                        },
                    )
                if self.source == SOURCE_REAUTH:
                    return self.async_update_reload_and_abort(
                        self._get_reauth_entry(),
                        unique_id=f"{DOMAIN}_{user_input[CONF_API_KEY]}",
                        data={
                            CONF_API_KEY: user_input[CONF_API_KEY],
                        },
                    )
                _LOGGER.error(
                    "An invalid config flow source was specified: %s", self.source
                )
                return self.async_abort(reason="invalid_source")

        data_schema: probatio.Schema = probatio.Schema(
            {probatio.Required(CONF_API_KEY): probatio.All(TextSelector())}
        )
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "url_download_app": URL_DOWNLOAD_APP,
                "url_connect_instructions": URL_CONNECT_INSTRUCTIONS,
            },
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Perform reauth upon an API authentication error."""
        return await self.async_step_user()

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: LiebherrConfigEntry,
    ) -> OptionsFlowHandler:
        """Create the options flow."""
        return OptionsFlowHandler()
