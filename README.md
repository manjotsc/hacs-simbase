# Simbase IoT SIM Management for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/your-username/hacs-simbase)](https://github.com/your-username/hacs-simbase/releases)
[![License](https://img.shields.io/github/license/your-username/hacs-simbase)](LICENSE)

A Home Assistant custom integration for [Simbase](https://www.simbase.com/) IoT SIM card management. Monitor and control your IoT SIM cards directly from Home Assistant.

## Features

- **SIM Card Monitoring** - Track data usage, status, costs, SMS counts, and more
- **Account Overview** - See totals across all SIM cards in one place
- **Activation Control** - Enable/disable individual SIMs or all SIMs at once
- **SMS Support** - Send SMS messages to your SIM cards
- **Configurable Sensors** - Choose which sensors to enable during setup
- **Real-time Updates** - Configurable polling interval

## Screenshots

*Coming soon*

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on **Integrations**
3. Click the three dots menu in the top right corner
4. Select **Custom repositories**
5. Add the repository URL: `https://github.com/your-username/hacs-simbase`
6. Select category: **Integration**
7. Click **Add**
8. Search for "Simbase" and install it
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/your-username/hacs-simbase/releases)
2. Extract the `simbase` folder to your `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

### Getting Your API Key

1. Log in to your [Simbase Dashboard](https://dashboard.simbase.com/)
2. Navigate to **Settings** > **API Key**
3. Copy your API key (Admin privileges required)

### Setup

1. Go to **Settings** > **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Simbase"
4. Enter your Simbase API key
5. Select which sensors you want to enable for your SIM cards
6. Click **Submit**

### Options

After setup, you can modify options at any time:

1. Go to **Settings** > **Devices & Services**
2. Find the Simbase integration and click **Configure**
3. Adjust settings:
   - **Update interval** - How often to fetch data (60-3600 seconds, default: 300)
   - **Sensors** - Select which sensors to enable per SIM
   - **Binary Sensors** - Select which binary sensors to enable
   - **Enable Activation Switch** - Toggle SIM activation control

## Entities

### Per-SIM Device

Each SIM card appears as a device with the following entities:

#### Sensors

| Sensor | Description |
|--------|-------------|
| Data Usage | Current month data usage in MB |
| Status | SIM state (enabled/disabled/active/inactive) |
| Coverage | Coverage plan name |
| Monthly Cost | Current month cost in USD |
| SMS Total | Total SMS (sent + received) this month |
| SMS Sent | SMS sent (MO) this month |
| SMS Received | SMS received (MT) this month |
| Hardware | Device hardware model |
| IMEI | Device IMEI number |
| Phone Number | MSISDN phone number |
| IP Address | * Only IF Static IP |

#### Binary Sensors

| Sensor | Description |
|--------|-------------|
| Online | Whether the SIM is enabled/active |

#### Controls

| Entity | Description |
|--------|-------------|
| Active Switch | Toggle to activate/deactivate the SIM card |

### Simbase Account Device

A special device that shows account-wide information:

#### Sensors

| Sensor | Description |
|--------|-------------|
| Account Balance | Account balance (if API supports it) |
| Total SIMs | Total number of SIM cards |
| Active SIMs | Number of enabled/active SIMs |
| Inactive SIMs | Number of disabled/inactive SIMs |
| Total Data Usage | Combined data usage from all SIMs |
| Total Monthly Cost | Combined monthly cost from all SIMs |
| Total SMS Sent | SMS sent across all SIMs |
| Total SMS Received | SMS received across all SIMs |
| Total SMS | Combined SMS total |

#### Controls

| Entity | Description |
|--------|-------------|
| Activate All SIMs | Button to activate all inactive SIM cards |
| Deactivate All SIMs | Button to deactivate all active SIM cards |

## Services

### simbase.activate_sim

Activate a SIM card by ICCID.

```yaml
service: simbase.activate_sim
data:
  iccid: "89012345678901234567"
```

### simbase.deactivate_sim

Deactivate a SIM card by ICCID.

```yaml
service: simbase.deactivate_sim
data:
  iccid: "89012345678901234567"
```

### simbase.send_sms

Send an SMS message to a SIM card.

```yaml
service: simbase.send_sms
data:
  iccid: "89012345678901234567"
  message: "Hello from Home Assistant!"
```

## Example Automations

### Alert on High Data Usage

```yaml
automation:
  - alias: "Alert High SIM Data Usage"
    trigger:
      - platform: numeric_state
        entity_id: sensor.my_sim_data_usage
        above: 1000
    action:
      - service: notify.mobile_app
        data:
          title: "High Data Usage Alert"
          message: "SIM has used over 1GB of data this month"
```

### Disable SIM When Cost Exceeds Budget

```yaml
automation:
  - alias: "Disable SIM on Budget Exceeded"
    trigger:
      - platform: numeric_state
        entity_id: sensor.my_sim_monthly_cost
        above: 50
    action:
      - service: simbase.deactivate_sim
        data:
          iccid: "89012345678901234567"
      - service: notify.mobile_app
        data:
          title: "SIM Disabled"
          message: "SIM was disabled due to exceeding $50 budget"
```

### Daily Cost Summary

```yaml
automation:
  - alias: "Daily Simbase Cost Summary"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Simbase Daily Summary"
          message: >
            Total SIMs: {{ states('sensor.simbase_account_total_sims') }}
            Active: {{ states('sensor.simbase_account_active_sims') }}
            Monthly Cost: ${{ states('sensor.simbase_account_total_monthly_cost') }}
            Data Used: {{ states('sensor.simbase_account_total_data_usage') }} MB
```

### Dashboard Card Example

```yaml
type: entities
title: Simbase Account Overview
entities:
  - entity: sensor.simbase_account_total_sims
    name: Total SIMs
  - entity: sensor.simbase_account_active_sims
    name: Active
  - entity: sensor.simbase_account_inactive_sims
    name: Inactive
  - type: divider
  - entity: sensor.simbase_account_total_data_usage
    name: Data Usage
  - entity: sensor.simbase_account_total_monthly_cost
    name: Monthly Cost
  - type: divider
  - entity: button.simbase_account_activate_all_sims
  - entity: button.simbase_account_deactivate_all_sims
```

## Troubleshooting

### Integration Not Loading

1. Check Home Assistant logs for errors (**Settings** > **System** > **Logs**)
2. Verify your API key is correct
3. Ensure you have network connectivity to api.simbase.com
4. Try removing and re-adding the integration

### Sensors Showing "Unknown"

Some sensors may show "unknown" if:
- The SIM card doesn't have data for that field
- The Simbase API doesn't provide that information for your account
- The SIM is not currently active/connected

### Account Balance Shows "Unknown"

The Account Balance sensor requires an API endpoint that may not be available for all Simbase accounts. Other account-level sensors (Total SIMs, costs, etc.) will still work as they are calculated from SIM data.

### Rate Limiting

The Simbase API has rate limits:
- 10 requests per second
- 5,000 requests per day

The integration includes automatic rate limit protection. If you have many SIMs, consider increasing the update interval.

## Known Limitations

The following features are **not available** due to Simbase API limitations:

| Feature | Reason |
|---------|--------|
| Network Operator | Not provided by Simbase API |
| Signal Strength | Not provided by Simbase API |
| Connection Type (2G/3G/4G/5G) | Not provided by Simbase API |
| Data Limit | Not provided by Simbase API |
| Roaming Status | Not provided by Simbase API |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

- **Bug Reports**: [GitHub Issues](https://github.com/your-username/hacs-simbase/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/your-username/hacs-simbase/issues)
- **Simbase Support**: [Simbase Help Center](https://support.simbase.com/)
- **API Documentation**: [Simbase Developer Portal](https://developer.simbase.com/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not officially affiliated with or endorsed by Simbase. Use at your own risk.

---

**Note**: Remember to replace `your-username` in the badge URLs and repository links with your actual GitHub username.
