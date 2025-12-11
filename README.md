# Simbase IoT SIM Management for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/manjotsc/ha-simbase)](https://github.com/manjotsc/ha-simbase/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Monitor and control your [Simbase](https://www.simbase.com/) IoT SIM cards directly from Home Assistant. Track data usage, costs, SMS metrics, and manage SIM activation from your dashboard.

> **Note:** This is an unofficial, community-developed integration and is not affiliated with or endorsed by Simbase.

## Features

| Feature | Description |
|---------|-------------|
| SIM Monitoring | Track data usage, status, costs, and SMS counts |
| Account Overview | View totals across all SIM cards |
| Activation Control | Enable/disable SIMs individually or in bulk |
| SMS Support | Send SMS messages to your SIM cards |
| Configurable | Choose which sensors to enable |
| Automations | Trigger automations based on SIM status |

## Installation

### HACS (Recommended)

1. Open **HACS** in Home Assistant
2. Go to **Integrations** → **Menu** (three dots) → **Custom repositories**
3. Add `https://github.com/manjotsc/ha-simbase` with category **Integration**
4. Search for and install **Simbase**
5. Restart Home Assistant

### Manual

1. Download the [latest release](https://github.com/manjotsc/ha-simbase/releases)
2. Copy `custom_components/simbase` to your `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Get your API key from [Simbase Dashboard](https://dashboard.simbase.com/) → **Settings** → **API Key**
2. In Home Assistant, go to **Settings** → **Devices & Services**
3. Click **Add Integration** and search for **Simbase**
4. Enter your API key and select your preferred sensors

## Available Entities

### Per-SIM Sensors

| Sensor | Description |
|--------|-------------|
| Data Usage | Current month data consumption |
| Status | SIM state (active/disabled/suspended) |
| Monthly Cost | Current month costs |
| SMS Sent/Received | Message counts |
| Coverage Plan | Current plan |
| Hardware | Device info |
| IMEI | Device identifier |
| MSISDN | Phone number |
| IP Address | Assigned IP |

### Account Sensors

| Sensor | Description |
|--------|-------------|
| Account Balance | Credit balance |
| Total/Active/Inactive SIMs | SIM counts |
| Total Data Usage | Aggregate data consumption |
| Total Monthly Cost | Sum of all SIM costs |
| Total SMS | Aggregate message counts |

### Controls

| Entity | Description |
|--------|-------------|
| SIM Activation Switch | Enable/disable individual SIMs |
| Activate All Button | Enable all SIMs at once |
| Deactivate All Button | Disable all SIMs at once |

### Services

| Service | Description |
|---------|-------------|
| `simbase.activate_sim` | Activate a SIM card |
| `simbase.deactivate_sim` | Deactivate a SIM card |
| `simbase.send_sms` | Send SMS to a SIM card |
| `simbase.read_sms` | Read SMS messages from a SIM card |

## Known Limitations

The following sensors are **not available** due to Simbase API limitations:

| Sensor | Reason |
|--------|--------|
| Network Operator | No network info in API |
| Data Limit | Not provided by API |
| Signal Strength | Not provided by API |
| Connection Type | Not provided by API |
| Data Limit Exceeded | Not provided by API |
| Throttled Status | Not provided by API |
| Roaming Status | Not provided by API |

## License

This project is licensed under the [MIT License](LICENSE).

---

**Trademark Notice:** Simbase is a trademark of its respective owner. This project is not affiliated with Simbase.
