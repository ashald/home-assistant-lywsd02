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

## Installation

### With HACS
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)

You can use HACS to manage the installation and provide update notifications.

1. Add this repo as a [custom repository](https://hacs.xyz/docs/faq/custom_repositories/):

```text
https://github.com/ashald/home-assistant-lywsd02
```

2. Install the integration using the appropriate button on the HACS Integrations page. Search for "home-assistant-lywsd02".
