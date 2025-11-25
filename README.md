# Fluvius API - Complete Solution

A Python solution to authenticate with Fluvius (Belgian energy provider) and retrieve your energy consumption data programmatically, without needing a headless browser for API calls.

## 🎯 What This Does

- **Authenticates** with Fluvius using the same Azure B2C PKCE flow the website uses (pure HTTP, no browser)
- **Extracts Bearer token** for API access
- **Retrieves consumption data** via REST API calls
- **Analyzes energy usage** including solar injection

## 📋 Requirements

- Python 3.9+
- `requests` (install with `pip install -r requirements.txt`)

Both `fluvius_fetch_token.py` and `fluvius_api_solution.py` rely on the same dependency list.
## 🚀 Quick Start

### 1. Configuration

Provide your Fluvius credentials and meter information via environment variables or CLI arguments:

```bash
set FLUVIUS_LOGIN=your.email@example.com
set FLUVIUS_PASSWORD=your_password
set FLUVIUS_EAN=5414488200XXXXXXX
set FLUVIUS_METER_SERIAL=1SAG1100XXXXXXX
```

Alternatively, pass them explicitly when running the script:

```bash
python fluvius_api_solution.py ^
  --email your.email@example.com ^
  --password LOUVRE ^
  --ean 5414488200XXXXXXX ^
  --meter-serial 1SAG1100XXXXXXX ^
  --days-back 7
```

Optional flags:
- `--bearer-token <token>`: skip authentication and reuse an existing token
- `--remember-me`: forwards the rememberMe flag to Fluvius
- `--output <path>`: override the output JSON path (default `fluvius_consumption_data.json`)
- `--timezone <IANA name>`: choose which timezone to use for `historyFrom`/`historyUntil` (default `Europe/Brussels` or `FLUVIUS_TIMEZONE`)
- `--granularity <value>`: override the Fluvius granularity parameter (`3`=quarter-hour, `4`=daily; default `4` or `FLUVIUS_GRANULARITY`)

### 2. Run the Solution

```bash
python fluvius_api_solution.py
```

This will:
1. Call `fluvius_fetch_token.py` to obtain a Bearer token via HTTP
2. Retrieve the requested number of days of consumption data
3. Analyze and display your energy usage
4. Save raw data to `fluvius_consumption_data.json` (or your chosen path)

## 📊 API Usage

### Get Bearer Token Programmatically

```python
from fluvius_fetch_token import get_bearer_token_http

token, token_payload = get_bearer_token_http(
  email="your.email@example.com",
  password="your_password",
  remember_me=False,
  verbose=True,
)
print(f"Token: {token[:40]}...")
```

### Get Consumption Data

```python
from fluvius_api_solution import get_consumption_data

data = get_consumption_data(
  access_token=token,
  ean="5414488200441XXXXX",S
  meter_serial="1SAG11000XXXXX",
  days_back=30,
)
```

### Analyze Data

```python
from fluvius_api_solution import analyze_consumption_data

# Get human-readable analysis
analyze_consumption_data(data)
```

## 🔌 API Endpoints

### Meter Measurement History

**Endpoint:** `GET /verbruik/api/meter-measurement-history/{ean}`

**Parameters:**
- `historyFrom`: Start date (format: `2025-06-30T00:00:00.000+02:00`)
- `historyUntil`: End date (format: `2025-07-06T23:59:59.999+02:00`)
- `granularity`: `3` (daily data)
- `asServiceProvider`: `false`
- `meterSerialNumber`: Your meter serial number

**Headers:**
- `Authorization`: `Bearer {your_token}`
- `Accept`: `application/json`

**Example Response:**
```json
[
  {
    "d": "2025-06-30T22:00:00Z",
    "de": "2025-07-01T22:00:00Z",
    "v": [
      {
        "dc": 1,
        "t": 1,
        "st": 0,
        "v": 9.133,
        "vs": 2,
        "u": 3,
        "gcuv": null
      }
    ]
  }
]
```

## 📖 Data Format Explanation

### Daily Data Structure

- `d`: Start date of the period
- `de`: End date of the period  
- `v`: Array of values (measurements)

### Measurement Values

- `dc`: Tariff type
  - `1` = High tariff (peak hours)
  - `2` = Low tariff (off-peak hours)
- `t`: Direction code
  - `1` = Consumption (taking from grid)
  - `2` = Injection (feeding into grid, e.g., solar panels)
- `v`: Value in kWh
- `vs`: Value status (2 = valid)
- `st`: Status
- `u`: Unit (3 = kWh)

### Example Analysis Output

```
📅 Day 1: 2025-06-30T22:00:00Z
   ⚡ Consumption (High): 9.133 kWh
   ⚡ Consumption (Low): 2.200 kWh
   ☀️ Injection (High): 12.421 kWh
   ☀️ Injection (Low): 0.000 kWh
   📊 Total consumption: 11.333 kWh
   📊 Total injection: 12.421 kWh
   📊 Net consumption: -1.088 kWh
```

## 🔧 Advanced Usage

### Custom Date Range

```python
from datetime import datetime, timedelta

# Get specific date range
end_date = datetime(2025, 7, 1)
start_date = end_date - timedelta(days=30)

# Format dates for API
history_from = start_date.strftime('%Y-%m-%dT00:00:00.000+02:00')
history_until = end_date.strftime('%Y-%m-%dT23:59:59.999+02:00')

# Make custom API call
import requests
url = f"https://mijn.fluvius.be/verbruik/api/meter-measurement-history/{ean}"
response = requests.get(url, params={
    'historyFrom': history_from,
    'historyUntil': history_until,
    'granularity': '3',
    'asServiceProvider': 'false',
    'meterSerialNumber': meter_serial
}, headers={'Authorization': token})
```

### Process Multiple Meters

```python
meters = [
    {"ean": "5414488XXXXXXXXXXX", "serial": "1SAG1100042062"},
    {"ean": "5414488XXXXXXXXXXX", "serial": "1SAG1100042063"}
]

for meter in meters:
    print(f"Getting data for EAN: {meter['ean']}")
    data = get_consumption_data(token, meter['ean'], meter['serial'])
    # Process data...
```

## 📁 File Structure

```
Fluvius_API/
├── fluvius_api_solution.py      # CLI + analysis helpers
├── fluvius_fetch_token.py       # HTTP-only authenticator
├── example_usage.py             # Sample helper script
├── requirements.txt             # Python dependency
├── README.md                    # This guide
└── (generated) fluvius_consumption_data.json
```

## 🔍 Finding Your Meter Information

### Your EAN Number
- Login to https://mijn.fluvius.be
- Go to "Verbruik" (Consumption)
- Your EAN is displayed on the main page

### Your Meter Serial Number
- In the same section, look for meter details
- Or check your physical meter
- Format: Usually starts with letters like "1SAG"

## 🛠️ Troubleshooting

### Authentication Issues

**Problem:** `Authentication failed: ...`
- Verify the email/password or the `FLUVIUS_*` environment variables
- Re-run with `--quiet` removed to see the detailed HTTP steps
- If you have 2FA active on your account, disable it (Azure B2C policy currently expects password-only)

**Problem:** `Token endpoint error (4xx)`
- Fluvius sometimes rotates MSAL metadata; run again so the script refreshes config
- Ensure your IP is not blocked by too many rapid attempts

### API Issues

**Problem:** "400 Bad Request" with date validation errors
- Ensure you requested a positive `--days-back`
- Double-check custom date ranges follow `YYYY-MM-DDTHH:MM:SS.mmm+TZ`
- If you're outside Belgium, pass `--timezone Europe/Brussels` (or your desired zone) so the offset matches Fluvius expectations

**Problem:** "401 Unauthorized"
- Token likely expired; either rerun the CLI or pass a fresh value via `--bearer-token`

**Problem:** Empty data returned
- Check if your EAN and meter serial are correct
- Verify the date range (data might not be available for future dates)
- Ensure your meter is active and reporting data

### Networking Issues

- If you see timeouts, rerun with `--quiet` disabled to view which HTTP hop failed
- Corporate proxies may block the Azure B2C endpoints; configure the `HTTP(S)_PROXY` env vars if needed

## 📈 Data Analysis Examples

### Calculate Monthly Usage

```python
def calculate_monthly_stats(data):
    total_consumption = 0
    total_injection = 0
    
    for day in data:
        for reading in day.get('v', []):
            value = reading.get('v', 0)
            if reading.get('t') == 1:  # Consumption
                total_consumption += value
            elif reading.get('t') == 2:  # Injection
                total_injection += value
    
    net_usage = total_consumption - total_injection
    return {
        'consumption': total_consumption,
        'injection': total_injection,
        'net': net_usage
    }
```

### Export to CSV

```python
import csv
from datetime import datetime

def export_to_csv(data, filename='consumption.csv'):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Type', 'Tariff', 'Value (kWh)'])
        
        for day in data:
            date = day.get('d', '')
            for reading in day.get('v', []):
                direction = 'Consumption' if reading.get('t') == 1 else 'Injection'
                tariff = 'High' if reading.get('dc') == 1 else 'Low'
                value = reading.get('v', 0)
                writer.writerow([date, direction, tariff, value])
```

## ⚠️ Important Notes

1. **Rate Limiting**: Don't make too many API calls in quick succession
2. **Token Expiry**: Bearer tokens expire after some time (usually hours)
3. **Data Availability**: Recent data might take time to appear
4. **Time Zone**: All timestamps are in UTC, data periods are in local time (CET/CEST)
5. **Privacy**: Keep your Bearer token secure and don't share it

## 🔒 Security Best Practices

- Store credentials in environment variables:
```python
import os
FLUVIUS_LOGIN = os.getenv('FLUVIUS_LOGIN')
FLUVIUS_PASSWORD = os.getenv('FLUVIUS_PASSWORD')
```

- Don't commit credentials to version control
- Regenerate tokens regularly
- Use HTTPS for all API calls (already implemented)

## 📞 Support

This is an unofficial solution. For official support:
- Fluvius Customer Service: https://www.fluvius.be/contact

## 📄 License

This project is for educational and personal use only. 

---

**🎉 Enjoy your energy data!** 

With this solution, you can now programmatically access your Fluvius consumption data, analyze your energy usage patterns, track your solar panel performance, and integrate with home automation systems.
