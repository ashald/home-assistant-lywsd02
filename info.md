# LYWSD02 Sync

Once installed, you need to add following to HomeAssistant's `configuration.yaml` and restart it:
```yaml
lywsd02:
```

## Setting Time

Now you have have `lywsd.set_time` service that can be used to set time on a LYWSD02 given its BLE MAC address.

Only MAC address parameter is requried, and it will set the time to what is on your HomeAssistant.
You can tweak the exact time set via additional parameters.

See [./services.yaml](./custom_components/lywsd02/services.yaml) for details.

Now you can setup an automation to invoke this service as often as you'd like to sync LYWSD02's time.

## Setting Unit

Will be added in future versions.
