import json
import requests
import logging
from datetime import datetime
from supabase import create_client, Client

# 🔑 Supabase API Details
SUPABASE_URL = "https://nifvuvksezrvlididxmq.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5pZnZ1dmtzZXpydmxpZGlkeG1xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzUzNDAyOTMsImV4cCI6MjA1MDkxNjI5M30.iiSvxsIH0A8h96udUyeNognYbDGoEcIx1UB6TDgxEU8"
SUPABASE_TABLE = "form_data"

# 🔗 Make.com Webhook URL
MAKE_WEBHOOK_URL = "https://hook.us2.make.com/749hod1anyl3qyq2f8o2xrdcocytaqvb"

# 📝 Setup logging
logging.basicConfig(level=logging.INFO)

# 🔗 Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

def fetch_leads():
    """Fetch new leads from Supabase."""
    try:
        logging.info("📡 Fetching new leads from Supabase...")
        
        # Fetch records (modify filters as needed)
        response = supabase.table(SUPABASE_TABLE).select("*").eq("status", "new").execute()

        if response.data:
            logging.info(f"✅ Retrieved {len(response.data)} new leads.")
            return response.data
        else:
            logging.info("ℹ️ No new leads found.")
            return []
    
    except Exception as e:
        logging.error(f"❌ Error fetching leads: {e}")
        return []

def send_to_make(leads):
    """Send lead data to Make.com webhook."""
    try:
        logging.info("🚀 Sending data to Make.com...")

        # Prepare the payload
        payload = {"leads": leads}

        # Send data
        response = requests.post(MAKE_WEBHOOK_URL, json=payload)

        # Check response
        if response.status_code == 200:
            logging.info("✅ Successfully sent data to Make.com!")
        else:
            logging.error(f"❌ Make.com Error: {response.text}")

    except Exception as e:
        logging.error(f"❌ Error sending data: {e}")

if __name__ == "__main__":
    # Fetch leads
    leads = fetch_leads()

    # If leads exist, send to Make.com
    if leads:
        send_to_make(leads)