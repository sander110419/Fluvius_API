#from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumwire import webdriver
import json
import requests

fluviuslogin = "yourlogin@youremail.com"
fluviuspassword = "yourfluviuspassword"
fluviusEAN = "the EAN you want to request the usage for" # example: 5414488200441000000

# Initialize Chrome WebDriver with performance logging enabled
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--enable-logging')
chrome_options.add_argument('--log-level=0')
chrome_options.add_argument('--headless')
chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
seleniumwire_options={ 'enable_har': True }
driver = webdriver.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)

# Open the login page
driver.get('https://mijn.fluvius.be')

log_entries = driver.get_log("performance")
# Initialize dictionaries to store request and response headers
request_headers_data = []
response_headers_data = []
last_known_url = None  # To keep track of the URL associated with the latest entry

# Wait for the button to be clickable
wait = WebDriverWait(driver, 10)
button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="b2c-account-type-selection-button-personal"]')))

# Find the button and click it
button = driver.find_element("xpath", '//button[@data-testid="b2c-account-type-selection-button-personal"]')
button.click()

# Wait for the email input field to be visible
wait = WebDriverWait(driver, 10)
email_input = wait.until(EC.visibility_of_element_located((By.ID, 'signInName')))

# Enter the email and password
email_input.send_keys(fluviuslogin)
password_input = driver.find_element(By.ID, "password")
password_input.send_keys(fluviuspassword)

# Click the login button
login_button = driver.find_element(By.ID, 'next')
login_button.click()

# Wait for the page to load and get the cookies
wait = WebDriverWait(driver, 200)
button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@id="fluv-cookies-button-accept-all"]')))
button.click()

with open('output.json', 'w') as file:
    file.write(driver.har)

# Load the JSON file
with open('output.json') as f:
    data = json.load(f)

# Initialize a variable to store the authorization header
auth_header = None

# Loop through each entry in the log
for entry in data['log']['entries']:
    # Loop through each header in the request
    for header in entry['request']['headers']:
        # Check if the header name is 'authorization' and starts with 'Bearer e'
        if header['name'] == 'authorization' and header['value'].startswith('Bearer e'):
            # If so, store it in our variable and break the loop
            auth_header = header['value']
            break
    # Break the outer loop if we found an authorization header
    if auth_header is not None:
        break

# Print the authorization header
if auth_header is not None:
    print(auth_header)
else:
    print("No authorization header found.")


driver.quit()

# Use the token to make a request

# Define the URL
url = f'https://mijn.fluvius.be/verbruik/api/consumption-histories/{fluviusEAN}?historyFrom=2023-06-30T22:00:00Z&historyUntil=2024-07-07T22:00:00Z&granularity=3&asServiceProvider=false'

# Define the headers for the request
headers = {
    'Authorization': auth_header,
}

# Make the GET request
response = requests.get(url, headers=headers)

# Print the response
print(response.json())
