#!/usr/bin/env python3
"""
Example usage of the Fluvius API solution
Demonstrates various ways to use the API
"""

from fluvius_api_solution import get_bearer_token, get_consumption_data, analyze_consumption_data
import json
import csv
from datetime import datetime, timedelta

def example_basic_usage():
    """Basic usage example"""
    print("=== Basic Usage Example ===")
    
    # Step 1: Get authentication token (only needed once)
    print("Getting Bearer token...")
    token = get_bearer_token()
    
    if not token:
        print("❌ Failed to get token")
        return
    
    # Step 2: Get consumption data
    print("Getting consumption data...")
    data = get_consumption_data(
        bearer_token=token,
        ean="5414488XXXXXX",  # Replace with your EAN
        meter_serial="1SAG110XXXXXX",  # Replace with your meter serial
        days_back=7
    )
    
    if data:
        print("✅ Success! Got data for analysis")
        analyze_consumption_data(data)
    else:
        print("❌ Failed to get data")

def example_export_to_csv():
    """Export consumption data to CSV"""
    print("\n=== Export to CSV Example ===")
    
    token = get_bearer_token()
    data = get_consumption_data(token, "5414488XXXXXXXX", "1SAG1100XXXXXXXXXXXXXXXX", days_back=30)
    
    if data:
        with open('consumption_export.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Date', 'End_Date', 'Type', 'Tariff', 'Value_kWh', 'Status'])
            
            for day in data:
                date = day.get('d', '')
                end_date = day.get('de', '')
                
                for reading in day.get('v', []):
                    direction = 'Consumption' if reading.get('dc') == 1 else 'Injection'
                    tariff = 'High' if reading.get('t') == 1 else 'Low'
                    value = reading.get('v', 0)
                    status = reading.get('vs', 0)
                    
                    writer.writerow([date, end_date, direction, tariff, value, status])
        
        print("✅ Data exported to consumption_export.csv")

def example_monthly_summary():
    """Calculate monthly summary statistics"""
    print("\n=== Monthly Summary Example ===")
    
    token = get_bearer_token()
    data = get_consumption_data(token, "XXXXXXXXXXXXXXXXXXXXx", "XXXXXXXXXXXXXXXXXXXXXXX", days_back=30)
    
    if data:
        total_consumption_high = 0
        total_consumption_low = 0
        total_injection_high = 0
        total_injection_low = 0
        
        for day in data:
            for reading in day.get('v', []):
                value = reading.get('v', 0)
                direction = reading.get('dc', 0)
                tariff = reading.get('t', 0)
                
                if direction == 1:  # Consumption
                    if tariff == 1:  # High tariff
                        total_consumption_high += value
                    else:  # Low tariff
                        total_consumption_low += value
                elif direction == 2:  # Injection
                    if tariff == 1:  # High tariff
                        total_injection_high += value
                    else:  # Low tariff
                        total_injection_low += value
        
        total_consumption = total_consumption_high + total_consumption_low
        total_injection = total_injection_high + total_injection_low
        net_consumption = total_consumption - total_injection
        
        print(f"📊 30-Day Summary:")
        print(f"   ⚡ Total Consumption: {total_consumption:.2f} kWh")
        print(f"      • High tariff: {total_consumption_high:.2f} kWh")
        print(f"      • Low tariff: {total_consumption_low:.2f} kWh")
        print(f"   ☀️ Total Injection: {total_injection:.2f} kWh")
        print(f"      • High tariff: {total_injection_high:.2f} kWh")
        print(f"      • Low tariff: {total_injection_low:.2f} kWh")
        print(f"   📈 Net Consumption: {net_consumption:.2f} kWh")
        
        if net_consumption < 0:
            print(f"   🎉 You generated {abs(net_consumption):.2f} kWh more than you consumed!")
        else:
            print(f"   📊 You consumed {net_consumption:.2f} kWh net from the grid")

def example_custom_date_range():
    """Get data for a custom date range"""
    print("\n=== Custom Date Range Example ===")
    
    import requests
    
    token = get_bearer_token()
    
    # Define custom date range (e.g., June 2025)
    start_date = datetime(2025, 6, 1)
    end_date = datetime(2025, 6, 30)
    
    # Format dates for API
    history_from = start_date.strftime('%Y-%m-%dT00:00:00.000+02:00')
    history_until = end_date.strftime('%Y-%m-%dT23:59:59.999+02:00')
    
    print(f"Getting data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    url = "https://mijn.fluvius.be/verbruik/api/meter-measurement-history/5414XXXXXXXXXXXXXXXXXxx"
    
    params = {
        'historyFrom': history_from,
        'historyUntil': history_until,
        'granularity': '3',
        'asServiceProvider': 'false',
        'meterSerialNumber': '1SAG1XXXXXXXXXXXXXXXXXXX'
    }
    
    headers = {
        'Authorization': token,
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got {len(data)} days of data for custom range")
        
        # Save custom data
        with open('custom_range_data.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("💾 Saved to custom_range_data.json")
        
    else:
        print(f"❌ Failed: {response.status_code}")

def example_token_reuse():
    """Demonstrate token reuse for multiple API calls"""
    print("\n=== Token Reuse Example ===")
    
    # Get token once
    print("Getting token once...")
    token = get_bearer_token()
    
    if not token:
        return
    
    # Use token for multiple calls
    print("Making multiple API calls with same token...")
    
    # Call 1: Last 7 days
    data_week = get_consumption_data(token, "541448XXXXXX", "1SAG11XXXXXXXXXX", days_back=7)
    if data_week:
        print(f"✅ Week data: {len(data_week)} days")
    
    # Call 2: Last 14 days
    data_2weeks = get_consumption_data(token, "541448XXXXXX", "1SAG11XXXXXXXXXX", days_back=14)
    if data_2weeks:
        print(f"✅ 2-week data: {len(data_2weeks)} days")
    
    # Call 3: Last 30 days
    data_month = get_consumption_data(token, "541448XXXXXX", "1SAG11XXXXXXXXXX", days_back=30)
    if data_month:
        print(f"✅ Month data: {len(data_month)} days")
    
    print("✅ All calls successful with single token!")

def main():
    """Run all examples"""
    print("🏠 FLUVIUS API - USAGE EXAMPLES")
    print("=" * 50)
    
    # Run examples
    example_basic_usage()
    example_export_to_csv()
    example_monthly_summary()
    example_custom_date_range()
    example_token_reuse()
    
    print("\n" + "=" * 50)
    print("🎉 All examples completed!")
    print("Check the generated files:")
    print("  • consumption_export.csv")
    print("  • custom_range_data.json")
    print("  • fluvius_consumption_data.json")

if __name__ == "__main__":
    main()
