# Home Assistant - LYWSD02 Sync

## Overview

This integration allows to configure LYWSD02 e-Ink clocks via HomeAssistant bluetooth integration.
This means that you can leverage all your ESPHome Bluetooth proxies for best coverage.

It exposes a single `lywsd02.set_time` service that syncs the clock (and,
optionally, the temperature unit and 12/24-hour format).

See [./info.md](./info.md) for usage details.

## Limitations

- **`clock_mode` (12/24-hour) is only supported on the LYWSD02MMC.** The command
  is validated against a Mi Home app capture, but on the plain LYWSD02 the time
  characteristic is fixed-length and rejects it. On such devices the time is
  still set and a warning is logged instead of failing the call — omit the
  `clock_mode` parameter to avoid the warning. See
  [#10](https://github.com/ashald/home-assistant-lywsd02/issues/10).

## Known issue: readings freeze in Home Assistant

Seen on a plain LYWSD02; not observed on the LYWSD02MMC. Temperature and
humidity reach Home Assistant through its
[Xiaomi BLE](https://www.home-assistant.io/integrations/xiaomi_ble/) integration,
not through this one.

**Symptom:** the clock's temperature and humidity stop changing in Home
Assistant while its battery level keeps updating. The clock's own display is
not affected.

**What we saw:** the clock kept broadcasting, but every temperature broadcast
was one byte short (its MiBeacon object declares 2 bytes of data and carries 1),
and no humidity broadcasts arrived at all. Xiaomi BLE drops such broadcasts, so
the last good readings stay in place. Every Bluetooth proxy received the same
short broadcasts, so the clock sends them that way. On that clock:

- it started on the day the clock was synced with `lywsd02.set_time`;
- the next `set_time`, a month later, did not fix it;
- the one after that did: complete broadcasts resumed within seconds.

**Workaround: re-sync automatically.** As a sync can put it right but does not
always, this automation re-syncs a clock once its temperature and humidity have
both stayed unchanged for 3 hours, and tries again every 6 hours while they
stay frozen. Replace the MAC address and the two Xiaomi BLE sensors with the
clock's own; add one automation per clock.

```yaml
automation:
  - alias: "LYWSD02: re-sync when its readings freeze"
    mode: single
    triggers:
      - trigger: time_pattern
        minutes: 0
    variables:
      mac: "A1:B2:C3:D4:E5:F6"
      temperature: sensor.lywsd02_temperature
      humidity: sensor.lywsd02_humidity
    conditions:
      # Skip a clock Home Assistant doesn't hear at all (dead battery, out of range).
      - "{{ states(temperature) | is_number }}"
      # Neither reading has changed for 3 hours.
      - >-
        {{ now() - [states[temperature].last_changed,
                    states[humidity].last_changed] | max > timedelta(hours=3) }}
      # Not more often than every 6 hours.
      - >-
        {{ this.attributes.last_triggered is none
           or now() - this.attributes.last_triggered > timedelta(hours=6) }}
    actions:
      - action: lywsd02.set_time
        data:
          mac: "{{ mac }}"
          timeout: 120
```

A Home Assistant restart also counts as a change, so the 3 hours start over.
A room whose temperature and humidity really stay unchanged for 3 hours only
costs an extra sync.

## Installation

### With HACS
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)

You can use HACS to manage the installation and provide update notifications.

1. Add this repo as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/):

```text
https://github.com/ashald/home-assistant-lywsd02
```

2. Install the integration using the appropriate button on the HACS Integrations page. Search for "home-assistant-lywsd02".
