# Simbase IoT SIM Management for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/manjotsc/hacs-simbase)](https://github.com/manjotsc/hacs-simbase/releases)
[![License](https://img.shields.io/github/license/manjotsc/hacs-simbase)](LICENSE)

A Home Assistant custom integration for [Simbase](https://www.simbase.com/) IoT SIM card management. Monitor and control your IoT SIM cards directly from Home Assistant.

---

> ⚠️ **Disclaimer**  
> This is an **unofficial, community-developed project** and is **not affiliated with, endorsed by, or supported by Simbase**.  
>  
> All product names, logos, and trademarks belong to their respective owners. API usage is subject to Simbase’s terms and conditions.

---

## Features

- **SIM Card Monitoring** – Track data usage, status, costs, SMS counts, and more  
- **Account Overview** – See totals across all SIM cards in one place  
- **Activation Control** – Enable/disable individual SIMs or all SIMs at once  
- **SMS Support** – Send SMS messages to your SIM cards  
- **Configurable Sensors** – Choose which sensors to enable  
- **Real-time Updates** – Configurable polling interval  

---

## Screenshots

*Coming soon*

---

## Installation

### 🔧 HACS (Recommended)

1. Open **HACS** in Home Assistant  
2. Go to **Integrations**  
3. Open **Menu → Custom repositories**  
4. Add: https://github.com/manjotsc/hacs-simbase
5. Choose category: **Integration**  
6. Install **Simbase**  
7. Restart Home Assistant  

---

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/manjotsc/hacs-simbase/releases)
2. Extract and copy `custom_components/simbase` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant  

---

## Configuration

### API Key

1. Log into your [Simbase Dashboard](https://dashboard.simbase.com/)  
2. Go to **Settings → API Key**  
3. Copy your API token  

---

### Adding the Integration

1. Go to **Settings → Devices & Services**  
2. Click **Add Integration**  
3. Search for **Simbase**  
4. Enter your API key  
5. Select optional sensors and features  

---

## Entities

### Per-SIM Device

Includes:  
- Data usage  
- Status  
- Monthly cost  
- SMS totals  
- Coverage  
- Hardware  
- IMEI  
- MSISDN  
- Static IP (if available)  

Binary sensors:  
- Online status  

Controls:  
- SIM activation switch  

---

## Account Overview

Global entities:  
- Total SIM count  
- Active SIMs  
- Inactive SIMs  
- Total data usage  
- Total cost  
- SMS metrics  

Controls:  
- Activate all SIMs  
- Deactivate all SIMs  

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE).

## Trademark Notice

Simbase® and all related names are trademarks of their respective owners.  
This project makes no claim to those marks.


