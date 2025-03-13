import time
import os
from apify_client import ApifyClient
import time
from dotenv import load_dotenv
import csv
from urllib.parse import quote_plus
import requests

start_time = time.time()
load_dotenv()

# Apify API Token
TOKEN = os.getenv('APIFY_API_KEY')

# Apollo Login Credentials
APOLLO_EMAIL = os.getenv('APOLLO_EMAIL')
APOLLO_PASSWORD = os.getenv('APOLLO_PASSWORD')

def clean_field(value):
    """Remove unwanted characters like brackets and strip spaces."""
    if isinstance(value, list):
        return [str(v).strip().replace("[", "").replace("]", "") for v in value]
    return str(value).strip().replace("[", "").replace("]", "")

def build_apollo_search_url(job_titles, location, company_size, industry):
    base_url = "https://app.apollo.io/#/people?sortByField=recommendations_score&sortAscending=false&page=1"
    job_titles_str = "&".join([f"personTitles[]={quote_plus(title)}" for title in job_titles])
    location_str = f"personLocations[]={quote_plus(location)}"
    # Convert company size to Apollo's format (assuming size is a range like "1,10")
    company_size_str = f"organizationNumEmployeesRanges[]={company_size.replace('Micro (', '').replace(' employees)', '')}" 
    industry_str = f"qOrganizationKeywordTags[]={quote_plus(industry)}"
    # Combine all parameters
    search_url = f"{base_url}&{job_titles_str}&{location_str}&{company_size_str}&{industry_str}"
    return search_url

def fetch_and_send(data):
    try:
        industry = data.get("preferred_industries", "")
        company_size = data.get("preferred_company_size", "")
        company_location = data.get("preferred_location", "")
        job_titles = data.get("job_titles", [])
        print(f"📊 Searching for leads in Industry: {industry}, Company Size: {company_size}, Location: {company_location}, Job Titles: {job_titles}")
        # Join filters into the Apollo search URL
        search_url = build_apollo_search_url(job_titles, company_location, company_size, industry)
        print(f"🔍 Using Search URL: {search_url}")
        # Connect to Apify API
        print("🔗 Connecting to Apify API...")
        apify_client = ApifyClient(TOKEN)
        actor_client = apify_client.actor('curious_coder/apollo-io-scraper')
        # print(formatted_cookies)
        print("🔗 Logging in with " + APOLLO_EMAIL)
        input_data = {
            # "cookie": formatted_cookies,
            "email": APOLLO_EMAIL,
            "password": APOLLO_PASSWORD,
            "count": 1,
            "getEmails": True,
            "guessedEmails": False,
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"]
            },
            "searchUrl": search_url,
            "startPage": 1,
            "waitForVerification": False
        }
        time.sleep(10)
        print("🚀 Starting Apollo scraper actor...")
        call_result = actor_client.call(run_input=input_data)
        # Fetch results from the Apify actor's dataset
        dataset_client = apify_client.dataset(call_result['defaultDatasetId'])
        # time.sleep(100)
        list_items_result = dataset_client.list_items().items  # Extract actual list of items
        print(f'✅ Retrieved {len(list_items_result)} results from Apollo.')
        if not list_items_result:
            print("⚠️ No leads found. Exiting without writing CSV.")
            return
        # Extract relevant fields for CSV
        csv_data = []
        for lead in list_items_result:
            csv_data.append({
                "Name": lead.get("name", ""),
                "Email": lead.get("email", ""),
                "Job Title": lead.get("title", ""),
                "Company": lead.get("organization", {}).get("name", ""),
                "Company Size": lead.get("organization", {}).get("num_employees", ""),
                "Industry": lead.get("organization", {}).get("industry", ""),
                "Location": lead.get("location", "")
            })
        # Define CSV filename
        csv_filename = f"./leads/apollo_leads_{int(time.time())}.csv"
        # Write data to CSV file
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"📂 Leads saved to {csv_filename}")
        with open(csv_filename, "rb") as file:
            response = requests.post(webhook_url, files={"file": csv_filename})
        webhook_url = "https://hook.us2.make.com/j27vxnv4bqy4y7nxaxmh6hfdir97x0qf"
        if response.status_code == 200:
            print("File sent successfully!")
        else:
            print(f"Failed to send file. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    end_time = time.time()
    total_time = end_time - start_time
    print(f"⏰ Total execution time: {total_time:.2f} seconds.")