import json
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from fetch_leads import fetch_leads

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Supabase API details
  # Keep this secret!
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_TABLE = "form_data"

# Supabase REST API endpoint
SUPABASE_ENDPOINT = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"

# Helper function to format date from dictionary
def format_date(date_dict):
    try:
        # Ensure all parts are present and combine them into a string
        if 'month' in date_dict and 'day' in date_dict and 'year' in date_dict:
            date_str = f"{date_dict['month']}/{date_dict['day']}/{date_dict['year']}"
            return datetime.strptime(date_str, "%m/%d/%Y").date()
        else:
            logging.error(f"Missing parts for date: {date_dict}")
            return None
    except ValueError:
        logging.error(f"Invalid date format: {date_dict}")
        return None

@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        # Log incoming request
        logging.debug("Request Content-Type: %s", request.content_type)
        logging.debug("Request Data: %s", request.data)

        # Parse the form data (JotForm sends multipart/form-data)
        data = request.form.to_dict()

        # Log the parsed data
        logging.debug("Parsed form data: %s", data)

        # Check if rawRequest field is present
        raw_request = data.get('rawRequest')
        if not raw_request:
            return jsonify({"error": "Missing rawRequest data"}), 400

        # Parse the rawRequest JSON string
        try:
            raw_data = json.loads(raw_request)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing rawRequest JSON: {e}")
            return jsonify({"error": "Invalid JSON in rawRequest"}), 400

        # Now, you can extract the necessary fields from raw_data
        extracted_data = {
            "full_name": f"{raw_data.get('q3_fullName3', {}).get('first', '')} {raw_data.get('q3_fullName3', {}).get('last', '')}",
            "phone_number": raw_data.get('q5_phoneNumber5', {}).get('full', ''),
            "email": raw_data.get('q6_email6', ''),
            "education_level": raw_data.get('q36_educationLevel', ''),
            "program": raw_data.get('q46_program', ''),
            "start_date": format_date(raw_data.get('q50_startDate', {})),  # Handle start date as dictionary
            "end_date": format_date(raw_data.get('q51_endDate', {})),  # Handle end date as dictionary
            "awards": raw_data.get('q52_awards', ''),
            "networking_purpose": raw_data.get('q33_whatIs', ''),
            "preferred_industries": raw_data.get('q55_canYou55', ''),
            "preferred_company_size": raw_data.get('q59_whatIs59', ''),
            "preferred_location": raw_data.get('q61_whereIs', {}).get('city', ''),
            "job_titles": raw_data.get('q62_potentialJob', []),
        }

        # Log the extracted data
        logging.debug("Extracted Data: %s", extracted_data)

        # Validate required fields
        required_fields = [
            "full_name", "phone_number", "email", "education_level", "program", 
            "start_date", "end_date", "awards", "networking_purpose", 
            "preferred_industries", "preferred_company_size", "preferred_location", 
            "job_titles"
        ]
        missing_fields = [field for field in required_fields if not extracted_data.get(field)]
        if missing_fields:
            return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

        # Convert start_date and end_date to string for JSON serialization
        if extracted_data['start_date']:
            extracted_data['start_date'] = extracted_data['start_date'].strftime("%Y-%m-%d")
        if extracted_data['end_date']:
            extracted_data['end_date'] = extracted_data['end_date'].strftime("%Y-%m-%d")

        # Send data to Supabase
        headers = {
            "Content-Type": "application/json",
            "apikey": SUPABASE_API_KEY,
            "Authorization": f"Bearer {SUPABASE_API_KEY}"
        }
        response = requests.post(SUPABASE_ENDPOINT, json=extracted_data, headers=headers)


        # Handle Supabase response
        if response.status_code in [200, 201]:
            logging.info("Data saved successfully!")
            leads = fetch_leads()
            # Log or return lead data if needed
            logging.info(f"Fetched {len(leads)} leads from Apollo.")
            return jsonify({"message": "Data saved successfully!", "leads_count": len(leads)}), 200
        else:
            logging.error(f"Supabase Error: {response.text}")
            return jsonify({"error": "Failed to save data", "details": response.text}), 500

    except Exception as e:
        logging.error(f"Error occurred: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=50)
