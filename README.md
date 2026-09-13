# Home Assistant - LYWSD02 Sync Clock

Configure Xiaomi LYWSD02 e-ink clocks through Home Assistant Bluetooth. The integration also works with Bluetooth proxies, including ESPHome Bluetooth proxies.

## Installation

### HACS

[![HACS badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)

1. In HACS, open **Integrations**.
2. Open the menu and choose **Custom repositories**.
3. Add:

  ```text
  https://github.com/shirou93/home-assistant-lywsd02
  ```

4. Select **Integration** as the category and install **LYWSD02 Sync Clock**.
5. Restart Home Assistant.

## Configuration

No YAML configuration is required.

1. Open **Settings > Devices & services**.
2. Select **Add integration**.
3. Search for **LYWSD02 Sync Clock**.
4. Complete the setup. No clock is added in the UI.

Clock addresses are provided only when calling the service.

## Synchronize Time

The integration provides the `lywsd02.set_time` service. Provide the target clock MAC address in every call:

```yaml
service: lywsd02.set_time
data:
  mac: A1:B2:C3:D4:E5:F6
```

The service sets the clock to the current Home Assistant time. Create an automation to run it periodically.

## Optional Parameters

The service supports the following optional parameters:

```yaml
service: lywsd02.set_time
data:
  mac: A1:B2:C3:D4:E5:F6
  timeout: 60
  clock_mode: 24
  temp_mode: C
  tz_offset: 0
```

- `mac`: target clock address. Required for every call.
- `timeout`: connection timeout in seconds. The default is `60`.
- `clock_mode`: `12` or `24` hour mode.
- `temp_mode`: `C` or `F`.
- `tz_offset`: timezone offset in hours.
- `timestamp`: optional UNIX timestamp instead of the current time.

The service definition is available in [services.yaml](custom_components/lywsd02/services.yaml).
