# Fluvius API - Complete Solution

A Python solution to authenticate with Fluvius (Belgian energy provider) and retrieve your energy consumption data programmatically, without needing a headless browser for API calls.

## 🎯 What This Does

- ✅ **Authenticates** with Fluvius using Azure B2C (one-time browser automation)
- ✅ **Extracts Bearer token** for API access
- ✅ **Retrieves consumption data** via REST API calls
- ✅ **Analyzes energy usage** including solar injection
- ✅ **No browser needed** for API calls after authentication

## 📋 Requirements

```bash
pip install selenium selenium-wire beautifulsoup4 requests
```

You'll also need Chrome browser installed for the initial authentication.

## 🚀 Quick Start

### 1. Configuration

Edit the credentials in `fluvius_api_solution.py`:

```python
# Your credentials and meter info
FLUVIUS_LOGIN = "your.email@example.com"
FLUVIUS_PASSWORD = "your_password"
FLUVIUS_EAN = "your_ean_number"
METER_SERIAL = "your_meter_serial"
```

### 2. Run the Solution

```bash
python fluvius_api_solution.py
```

This will:
1. Authenticate and get your Bearer token
2. Retrieve 7 days of consumption data
3. Analyze and display your energy usage
4. Save raw data to `fluvius_consumption_data.json`

## 📊 API Usage

### Get Bearer Token (One-time)

```python
from fluvius_api_solution import get_bearer_token

# Authenticate once to get token
token = get_bearer_token()
print(f"Token: {token}")
```

### Get Consumption Data

```python
from fluvius_api_solution import get_consumption_data

# Get consumption data for any period
data = get_consumption_data(
    bearer_token=token,
    ean="541448820044159229",
    meter_serial="1SAG1100042062",
    days_back=30  # Last 30 days
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

- `dc`: Direction code
  - `1` = Consumption (taking from grid)
  - `2` = Injection (feeding into grid, e.g., solar panels)
- `t`: Tariff type
  - `1` = High tariff (peak hours)
  - `2` = Low tariff (off-peak hours)
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
    {"ean": "541448820044159229", "serial": "1SAG1100042062"},
    {"ean": "541448820044159236", "serial": "1SAG1100042063"}
]

for meter in meters:
    print(f"Getting data for EAN: {meter['ean']}")
    data = get_consumption_data(token, meter['ean'], meter['serial'])
    # Process data...
```

## 📁 File Structure

```
fluvius-api/
├── fluvius_api_solution.py     # Main solution
├── test_exact_api.py           # Test script
├── fluvius_consumption_data.json  # Your data (generated)
├── requirements.txt            # Dependencies
└── README.md                   # This guide
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

**Problem:** "No Bearer token found"
```python
# Solution: Check credentials and try again
token = get_bearer_token()
```

**Problem:** "Authentication failed"
- Verify your email and password are correct
- Make sure you can login manually to mijn.fluvius.be
- Check if you have 2FA enabled (not currently supported)

### API Issues

**Problem:** "400 Bad Request" with date validation errors
```python
# Solution: Ensure correct date format
date_str = "2025-06-30T00:00:00.000+02:00"  # Correct format
```

**Problem:** "401 Unauthorized"
```python
# Solution: Token expired, get a new one
token = get_bearer_token()
```

**Problem:** Empty data returned
- Check if your EAN and meter serial are correct
- Verify the date range (data might not be available for future dates)
- Ensure your meter is active and reporting data

### Browser Issues

**Problem:** Selenium crashes
```bash
# Install Chrome and ChromeDriver
# Ubuntu/Debian:
sudo apt-get update
sudo apt-get install google-chrome-stable

# Or update Chrome to latest version
```

## 📈 Data Analysis Examples

### Calculate Monthly Usage

```python
def calculate_monthly_stats(data):
    total_consumption = 0
    total_injection = 0
    
    for day in data:
        for reading in day.get('v', []):
            value = reading.get('v', 0)
            if reading.get('dc') == 1:  # Consumption
                total_consumption += value
            elif reading.get('dc') == 2:  # Injection
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
                direction = 'Consumption' if reading.get('dc') == 1 else 'Injection'
                tariff = 'High' if reading.get('t') == 1 else 'Low'
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
- Official API: Check Fluvius developer portal (if available)

## 📄 License

This project is for educational and personal use only. Respect Fluvius's terms of service and rate limits.

---

**🎉 Enjoy your energy data!** 

With this solution, you can now programmatically access your Fluvius consumption data, analyze your energy usage patterns, track your solar panel performance, and integrate with home automation systems.
