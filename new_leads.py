from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from apify_client import ApifyClient

# Apify API Token
TOKEN = 'apify_api_d0637a4bRXhqGvBGFedZTl4vK6Qiv71xtUbw'

# Apollo Login Credentials
APOLLO_EMAIL = "utescanodalli@gmail.com"
APOLLO_PASSWORD = "utescaNodalli11235apollo!"

# Set up Selenium WebDriver
print("🚀 Setting up Selenium...")
chrome_options = Options()
chrome_options.add_argument("--headless")  # Remove this if you want to see the browser
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Open Apollo.io and log in
    print("🔑 Opening Apollo.io...")
    driver.get("https://app.apollo.io")
    time.sleep(3)  # Allow time for the page to load

    print("📝 Entering login details...")
    email_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")

    email_input.send_keys(APOLLO_EMAIL)
    password_input.send_keys(APOLLO_PASSWORD)
    password_input.send_keys(Keys.RETURN)  # Press Enter

    print("🔄 Logging in...")
    time.sleep(8)  # Wait for login to process

    # Extract cookies using Chrome DevTools Protocol
    print("📡 Fetching all cookies using DevTools...")
    all_cookies = driver.execute_cdp_cmd("Network.getAllCookies", {})

    formatted_cookies = [
        {
            "domain": cookie["domain"],
            "expirationDate": cookie.get("expires", 0),
            "hostOnly": cookie.get("hostOnly", False),
            "httpOnly": cookie.get("httpOnly", False),
            "name": cookie["name"],
            "path": cookie["path"],
            "sameSite": cookie.get("sameSite", "Lax"),
            "secure": cookie["secure"],
            "session": cookie.get("session", False),
            "storeId": "0",
            "value": cookie["value"],
            "id": idx + 1
        }
        for idx, cookie in enumerate(all_cookies["cookies"])
    ]

    print(f"✅ Retrieved {len(formatted_cookies)} cookies.")
    
    # Connect to Apify API
    print("🔗 Connecting to Apify API...")
    apify_client = ApifyClient(TOKEN)
    actor_client = apify_client.actor('curious_coder/apollo-io-scraper')

    input_data = {
        "cookie": formatted_cookies,
        "getEmails": True,
        "guessedEmails": False,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"]
        },
        "searchUrl": "https://app.apollo.io/#/people?finderViewId=5b8050d050a3893c382e9360&page=1&prospectedByCurrentTeam[]=no&contactEmailStatusV2[]=likely_to_engage&contactEmailStatusV2[]=verified&qKeywords=corporate%20banking&organizationIds[]=5f49727d63d39c0001f6693b&organizationIds[]=54a122df69702d7fe6374003",
        "startPage": 1,
        "waitForVerification": False
    }

    print("🚀 Starting Apollo scraper actor...")
    call_result = actor_client.call(run_input=input_data)

    if call_result is None:
        print('❌ Actor run failed.')
        driver.quit()
        exit()

    # Fetch results from the Apify actor's dataset
    dataset_client = apify_client.dataset(call_result['defaultDatasetId'])
    list_items_result = dataset_client.list_items().items  # Extract actual list of items
    print(f'✅ Retrieved {len(list_items_result)} results from Apollo.')

    # Close Selenium WebDriver after API call
    driver.quit()

    # Print results
    print(json.dumps(list_items_result, indent=4))

except Exception as e:
    print(f"❌ Error: {e}")
    driver.quit()
