# Migration from `liebherr` to `liebherr_sse` domain

## Background and rationale

Overriding a core's integration using the same `DOMAIN` in Home Assistant is discouraged. Additionally the current repository was forked long ago from the original custom integration and the current integration is very different from that integration.  The need to distinguish the current integration from the core integration and the past iterations had become increasing apparent.

## Migration Steps

> [!WARNING]
>
> This migration removes the prior entry, device and all entities.  They will be recreated in the configuration flow. Given that home assistant now allows you to configure [entity id schemes](http://home-assistant.io/docs/configuration/customizing-entities) the new entities might have different names that the prior entities.

1. Upgrade or uninstall the custom `liebherr` integration.  If migrating directly from the `liebherr` respository you must be using version  `2026.11.0`.
   
   [![Open your Home Assistant instance and open a repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=iluvdata&repository=liebherr)
2. Install  `liebherr_sse`:
   
    [![Open your Home Assistant instance and open a repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=iluvdata&repository=liebherr_sse)
3. Configure the `liebherr_sse` integration:

   [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=liebherr_sse)
   1. This will import the API Key and some of the configuration options from the current integration.
   2. It will remove the legacy `liebherr` config entry if the new `liebherr_sse` configuration is successful.
4. (Optional) Uninstall the `liebherr` custom integration in Marketplace/HACS:
   
   [![Open your Home Assistant instance and open a repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=iluvdata&repository=liebherr)
5. Review the new entities for name changes that may include **breaking changes** to Automations and Dashboards.
   
   [![Open your Home Assistant instance and show your entities.](https://my.home-assistant.io/badges/entities.svg)](https://my.home-assistant.io/redirect/entities/?domain=liebherr_sse&group=device)

