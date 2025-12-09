
3. Restart Home Assistant  

---

## Configuration

### 🔑 Getting Your API Key

1. Log in to your [Simbase Dashboard](https://dashboard.simbase.com/)  
2. Navigate to **Settings → API Key**  
3. Copy your API key (**Admin privileges required**)  

---

### 🛠 Setup

1. Go to **Settings → Devices & Services**  
2. Click **+ Add Integration**  
3. Search for **Simbase**  
4. Enter your **Simbase API key**  
5. Select which sensors you want to enable  
6. Click **Submit**  

---

### ⚙️ Options

After setup, you can modify options at any time:

1. Go to **Settings → Devices & Services**  
2. Find **Simbase** and click **Configure**  
3. Adjust:
   - **Update interval** (60–3600 seconds, default: 300)
   - **Enabled sensors**
   - **Enabled binary sensors**
   - **Enable activation switch**

---

## Entities

### 📱 Per-SIM Device

Each SIM card appears as a device with the following entities:

---

### 🔍 Sensors

| Sensor | Description |
|--------|-------------|
| Data Usage | Current month data usage in MB |
| Status | SIM state (enabled / disabled / active / inactive) |
| Coverage | Coverage plan name |
| Monthly Cost | Current month cost in USD |
| SMS Total | Total SMS this month |
| SMS Sent | SMS sent (MO) |
| SMS Received | SMS received (MT) |
| Hardware | Device hardware model |
| IMEI | Device IMEI number |
| Phone Number | MSISDN phone number |
| IP Address | Static IP ONLY |

---

### 🔘 Binary Sensors

| Sensor | Description |
|--------|-------------|
| Online | Whether the SIM is enabled/active |

---

### 🎛 Controls

| Entity | Description |
|--------|-------------|
| Active Switch | Toggle to activate/deactivate the SIM card |

---

## 🏢 Simbase Account Device

A special device that shows account-wide information:

---

### 📊 Sensors

| Sensor | Description |
|--------|-------------|
| Account Balance | Account balance |
| Total SIMs | Total number of SIM cards |
| Active SIMs | Number of enabled/active SIMs |
| Inactive SIMs | Number of disabled/inactive SIMs |
| Total Data Usage | Combined data usage |
| Total Monthly Cost | Combined monthly cost |
| Total SMS Sent | SMS sent across all SIMs |
| Total SMS Received | SMS received across all SIMs |
| Total SMS | Combined SMS total |

---

### 🧨 Controls

| Entity | Description |
|--------|-------------|
| Activate All SIMs | Activate all inactive SIMs |
| Deactivate All SIMs | Deactivate all active SIMs |

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
