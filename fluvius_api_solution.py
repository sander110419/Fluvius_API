#!/usr/bin/env python3
"""
Complete working Fluvius API solution
✅ Authenticates with Azure B2C
✅ Gets Bearer token
✅ Makes successful API calls
✅ Returns valid JSON consumption data
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver
import json
import requests
import time
from datetime import datetime, timedelta

# Your credentials and meter info
FLUVIUS_LOGIN = 
FLUVIUS_PASSWORD = 
FLUVIUS_EAN = 
METER_SERIAL = 

def get_bearer_token():
    """
    Authenticate with Fluvius and extract Bearer token
    This only needs to be run once to get the token
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    seleniumwire_options = {'enable_har': True}
    
    driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)
    
    try:
        print("🔐 Authenticating with Fluvius...")
        
        # Step 1: Go to main page
        driver.get('https://mijn.fluvius.be')
        
        # Step 2: Click personal account button
        wait = WebDriverWait(driver, 20)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="b2c-account-type-selection-button-personal"]')))
        button.click()
        
        # Step 3: Enter credentials
        email_input = wait.until(EC.visibility_of_element_located((By.ID, 'signInName')))
        email_input.send_keys(FLUVIUS_LOGIN)
        
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(FLUVIUS_PASSWORD)
        
        # Step 4: Submit login
        login_button = driver.find_element(By.ID, 'next')
        login_button.click()
        
        # Step 5: Wait for redirect
        wait.until(lambda d: 'mijn.fluvius.be' in d.current_url and 'b2clogin' not in d.current_url)
        
        # Step 6: Accept cookies
        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@id="fluv-cookies-button-accept-all"]')))
            cookie_button.click()
        except:
            pass
        
        # Step 7: Navigate to verbruik to trigger API calls
        driver.get('https://mijn.fluvius.be/verbruik')
        time.sleep(5)
        
        # Step 8: Extract Bearer token from captured requests
        for request in driver.requests:
            if '/api/' in request.url and request.headers.get('Authorization'):
                auth_header = request.headers['Authorization']
                if auth_header.startswith('Bearer'):
                    print(f"✅ Successfully got Bearer token")
                    return auth_header
        
        print("❌ No Bearer token found")
        return None
        
    finally:
        driver.quit()

def get_consumption_data(bearer_token, ean, meter_serial, days_back=7):
    """
    Get meter measurement history data
    
    Args:
        bearer_token: Authentication token from get_bearer_token()
        ean: Your EAN number (e.g., "541448820XXXXXXX")
        meter_serial: Your meter serial number (e.g., "1SAG110XXXXXXXXXX")
        days_back: Number of days of history to retrieve
    
    Returns:
        dict: JSON response with consumption data, or None if failed
    """
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Format dates exactly as required by the API
    history_from = start_date.strftime('%Y-%m-%dT00:00:00.000+02:00')
    history_until = end_date.strftime('%Y-%m-%dT23:59:59.999+02:00')
    
    url = f"https://mijn.fluvius.be/verbruik/api/meter-measurement-history/{ean}"
    
    params = {
        'historyFrom': history_from,
        'historyUntil': history_until,
        'granularity': '3',
        'asServiceProvider': 'false',
        'meterSerialNumber': meter_serial
    }
    
    headers = {
        'Authorization': bearer_token,
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"📊 Getting {days_back} days of consumption data...")
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"✅ Successfully retrieved {len(data)} days of data")
            return data
        except:
            print("❌ Failed to parse JSON response")
            return None
    else:
        print(f"❌ API call failed: {response.status_code}")
        print(f"Error: {response.text[:200]}...")
        return None

def analyze_consumption_data(data):
    """
    Analyze and display consumption data in a readable format
    """
    if not data:
        print("❌ No data to analyze")
        return
    
    print(f"\n📊 CONSUMPTION ANALYSIS:")
    print(f"=" * 50)
    
    total_days = len(data)
    print(f"📅 Period: {total_days} days")
    
    for day_idx, day_data in enumerate(data):
        date = day_data.get('d', 'Unknown date')
        date_end = day_data.get('de', 'Unknown end date')
        values = day_data.get('v', [])
        
        print(f"\n📅 Day {day_idx + 1}: {date}")
        
        # Sum up consumption for the day
        day_consumption = 0
        day_injection = 0
        
        for reading in values:
            direction = reading.get('dc', 0)  # 1 = consumption, 2 = injection
            tariff = reading.get('t', 0)      # 1 = high tariff, 2 = low tariff
            value = reading.get('v', 0)       # actual value in kWh
            
            if direction == 1:  # Consumption
                day_consumption += value
                tariff_name = "High" if tariff == 1 else "Low"
                print(f"   ⚡ Consumption ({tariff_name}): {value:.3f} kWh")
            elif direction == 2:  # Injection (solar panels)
                day_injection += value
                tariff_name = "High" if tariff == 1 else "Low"
                print(f"   ☀️ Injection ({tariff_name}): {value:.3f} kWh")
        
        net_consumption = day_consumption - day_injection
        print(f"   📊 Total consumption: {day_consumption:.3f} kWh")
        print(f"   📊 Total injection: {day_injection:.3f} kWh")
        print(f"   📊 Net consumption: {net_consumption:.3f} kWh")

def main():
    """
    Main function demonstrating the complete solution
    """
    print("=" * 60)
    print("🏠 FLUVIUS API - COMPLETE WORKING SOLUTION")
    print("=" * 60)
    
    # Step 1: Get Bearer token (authentication)
    print("\nStep 1: Authentication...")
    bearer_token = get_bearer_token()
    
    if not bearer_token:
        print("❌ Authentication failed")
        return
    
    print(f"✅ Authentication successful")
    print(f"🔑 Token: {bearer_token[:50]}...")
    
    # Step 2: Get consumption data
    print("\nStep 2: Retrieving consumption data...")
    consumption_data = get_consumption_data(
        bearer_token=bearer_token,
        ean=FLUVIUS_EAN,
        meter_serial=METER_SERIAL,
        days_back=7  # Get last 7 days
    )
    
    if consumption_data:
        # Step 3: Save raw data
        with open('fluvius_consumption_data.json', 'w') as f:
            json.dump(consumption_data, f, indent=2)
        print("💾 Raw data saved to fluvius_consumption_data.json")
        
        # Step 4: Analyze data
        analyze_consumption_data(consumption_data)
        
        # Step 5: Show how to use programmatically
        print(f"\n" + "=" * 60)
        print("🔧 HOW TO USE THIS PROGRAMMATICALLY:")
        print("=" * 60)
        print("1. Call get_bearer_token() once to authenticate")
        print("2. Use the token with get_consumption_data() to fetch data")
        print("3. The token works for multiple API calls until it expires")
        print(f"4. Your EAN: {FLUVIUS_EAN}")
        print(f"5. Your meter serial: {METER_SERIAL}")
        
        print(f"\n📋 EXAMPLE CODE:")
        print(f"```python")
        print(f"token = get_bearer_token()")
        print(f"data = get_consumption_data(token, '{FLUVIUS_EAN}', '{METER_SERIAL}', days_back=30)")
        print(f"```")
        
        print(f"\n🎉 SUCCESS! You now have a complete working solution!")
        
    else:
        print("❌ Failed to retrieve consumption data")

if __name__ == "__main__":
    main()
