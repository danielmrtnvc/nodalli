from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from apify_client import ApifyClient
import time  # existing import
from dotenv import load_dotenv

start_time = time.time()
load_dotenv()

# Apify API Token
TOKEN = os.getenv('APIFY_API_KEY')

# Apollo Login Credentials
APOLLO_EMAIL = os.getenv('APOLLO_EMAIL')
APOLLO_PASSWORD = os.getenv('APOLLO_PASSWORD')

print("🚀 Setting up Selenium...")
chrome_options = Options()

# ✅ Fix 1: Make headless mode more human-like
chrome_options.add_argument("--headless=new")  # Use "new" headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")  # Fake fullscreen
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")  # Fake real browser

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.set_page_load_timeout(60)

try:
    print("🔑 Opening Apollo.io...")
    driver.get("https://app.apollo.io")
    time.sleep(5)  # ✅ Fix 2: Shorten wait times

    print("📝 Entering login details...")
    email_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")

    email_input.send_keys(APOLLO_EMAIL)
    password_input.send_keys(APOLLO_PASSWORD)
    password_input.send_keys(Keys.RETURN)  # Press Enter

    print("🔄 Logging in...")
    time.sleep(7)  # ✅ Fix 3: Reduce excessive sleep time

    # ✅ Fix 4: Scroll down to trigger JavaScript events
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    # ✅ Fix 5: Capture cookies using `get_cookies()` instead of DevTools
    print("📡 Fetching all cookies...")
    all_cookies = driver.get_cookies()

    formatted_cookies = [
        {
            "domain": cookie["domain"],
            "expirationDate": cookie.get("expiry", 0),
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
        for idx, cookie in enumerate(all_cookies)
    ]

    print(f"✅ Retrieved {len(formatted_cookies)} cookies.")

    # ✅ Fix 6: Recheck if cookies contain session data
    if not any("session" in c["name"].lower() for c in formatted_cookies):
        raise Exception("❌ Missing session cookies, login likely failed!")

    # Connect to Apify API
    print("🔗 Connecting to Apify API...")
    apify_client = ApifyClient(TOKEN)
    actor_client = apify_client.actor('curious_coder/apollo-io-scraper')
    print(formatted_cookies)
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
    # time.sleep(100)
    list_items_result = dataset_client.list_items().items  # Extract actual list of items
    print(f'✅ Retrieved {len(list_items_result)} results from Apollo.')
    # Close Selenium WebDriver after API call
    driver.quit()

    # Print results
    # print(json.dumps(list_items_result, indent=4))

except Exception as e:
    print(f"❌ Error: {e}")
    driver.quit()

end_time = time.time()
total_time = end_time - start_time
print(f"⏰ Total execution time: {total_time:.2f} seconds.")