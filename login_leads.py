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
try:
    apify_client = ApifyClient(TOKEN)
    actor_client = apify_client.actor('curious_coder/apollo-io-scraper')
    input_data = {
        "email": APOLLO_EMAIL,
        "password": APOLLO_PASSWORD,
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

    call_result = actor_client.call(run_input=input_data)

    if call_result is None:
        print('❌ Actor run failed.')
        exit()

    # Fetch results from the Apify actor's dataset
    dataset_client = apify_client.dataset(call_result['defaultDatasetId'])
    # time.sleep(100)
    list_items_result = dataset_client.list_items().items  # Extract actual list of items
    print(f'✅ Retrieved {len(list_items_result)} results from Apollo.')
    # Close Selenium WebDriver after API call

    # Print results
    # print(json.dumps(list_items_result, indent=4))

except Exception as e:
    print(f"❌ Error: {e}")

end_time = time.time()
total_time = end_time - start_time
print(f"⏰ Total execution time: {total_time:.2f} seconds.")