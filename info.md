# LYWSD02 Sync

Once installed, you need to add following to HomeAssistant's `configuration.yaml` and restart it:
```yaml
lywsd02:
```

## Sync time button

If you'd rather press a button than call a service, go to **Settings ->
Devices & Services -> Add Integration -> LYWSD02 Sync** and enter the
device's MAC address (or accept the prompt if Home Assistant discovers it
over Bluetooth on its own). This adds a device with a single "Sync time"
button that calls `lywsd02.set_time` with no extra options. It's independent
of the service below — use whichever fits your setup, or both.

## Setting Time

Now you have have `lywsd.set_time` service that can be used to set time on a LYWSD02 given its BLE MAC address.

Only MAC address parameter is requried, and it will set the time to what is on your HomeAssistant.
Here's how the minimal invocation looks like:
```yaml
service: lywsd02.set_time
data:
  mac: A1:B2:C3:D4:E5:F6
```

Now you can setup an automation to invoke this service as often as you'd like to sync LYWSD02's time.

If you want a lower-lever control - you can tweak the exact time set via additional parameters.
See [./services.yaml](./custom_components/lywsd02/services.yaml) for details.

## Setting Unit

You can also set the temperature unit (F/C), TZ offset, and clock mode (12/24) via optional parameters:
```yaml
service: lywsd02.set_time
data:
  mac: A1:B2:C3:D4:E5:F6
  clock_mode: 24
  tz_offset: 0
  temp_mode: 'C'
```

> **Note:** `clock_mode` (12/24-hour) is only supported on the **LYWSD02MMC**.
> The payload is validated against a Mi Home app capture, but on the plain
> LYWSD02 the time characteristic is fixed-length and rejects it — in that case
> a warning is logged and the time is still set (see #10).

## Timeout

If you get an error establishing connection - could be because it takes longer than expected to get the Bluetooth proxy working. Consider increasing `timeout` from default 10s to a larger value:
```yaml
service: lywsd02.set_time
data:
  mac: A1:B2:C3:D4:E5:F6
  timeout: 60
```
