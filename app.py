
"""
Try sending the request from the same machine running the Flask server 
(using localhost or 127.0.0.1 instead of 100.67.80.59):

curl: curl -X POST http://127.0.0.1:5000/submit_form -H "Content-Type: application/x-www-form-urlencoded" -d "rawRequest={\"q12_name\":\"John Doe\",\"q13_email\":\"john.doe@example.com\",\"q16_message\":\"This is a test message\"}"

"""

import json
import logging
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv(dotenv_path="C:\\Users\\ahmed\\APS105\\webhook-nod\\nodali.env")

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Flask app setup
app = Flask(__name__)

# Supabase credentials from .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to save form data to Supabase
def save_to_supabase(name, email, message):
    try:
        # Insert data into the "form_data" table

        response = supabase.table("form_data").insert({
            "name": name,
            "email": email,
            "message": message
        }).execute()
        
        # Check if the response has status_code and handle it
        if hasattr(response, 'status_code'):
            if response.status_code == 201:
                logging.info(f"Data saved to Supabase: Name: {name}, Email: {email}, Message: {message}")
                return True
            else:
                logging.error(f"Failed to save data: {response.json()}")
                return False
        else:
            logging.error(f"Response does not have a status code. Response: {response}")
            return False

    except Exception as e:
        logging.error(f"Error saving to Supabase: {e}")
        return False

@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        # Log the incoming form data
        logging.debug("Received form data: %s", request.form)
        raw_request = request.form.get('rawRequest')

        if raw_request:
            # Parse the raw request JSON
            try:
                data = json.loads(raw_request)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decoding failed: {e}")
                return jsonify({"error": "Invalid JSON format"}), 400

            # Extract fields from the parsed JSON
            name = data.get('q12_name')
            email = data.get('q13_email')
            message = data.get('q16_message')

            # Validate required fields
            if not name:
                return jsonify({"error": "Missing name"}), 400
            if not email:
                return jsonify({"error": "Missing email"}), 400
            if not message:
                return jsonify({"error": "Missing message"}), 400

            # Save the data to Supabase
            if save_to_supabase(name, email, message):
                logging.debug("Data saved to Supabase successfully.")
                # Success response
                return jsonify({"message": "Data processed successfully!", "data": {"name": name, "email": email, "message": message}}), 200
            else:
                logging.error("Failed to save data to Supabase.")
                # Failure response
                return jsonify({"error": "Failed to save data to database"}), 500
        else:
            logging.error("No raw request data found.")
            return jsonify({"error": "No raw request data found."}), 400
    except Exception as e:
        # Log the error
        logging.error("Error occurred: %s", e)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# Main entry point
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


# Norbert
# Something like this
# Make.com Webhook URL
# MAKE_WEBHOOK_URL = "https://hook.integromat.com/unique-webhook-id"
# @app.route('/send-data', methods=['POST'])
# def send_csv_to_make():
#     # Example data to convert into CSV
#     data = [
#         {"user_id": 1, "name": "John Doe", "email": "johndoe@example.com"},
#         {"user_id": 2, "name": "Jane Smith", "email": "janesmith@example.com"},
#     ]

#     # Convert data to CSV
#     csv_buffer = io.StringIO()
#     writer = csv.DictWriter(csv_buffer, fieldnames=["user_id", "name", "email"])
#     writer.writeheader()
#     writer.writerows(data)
#     csv_data = csv_buffer.getvalue()

#     # Send CSV to Make.com webhook
#     headers = {
#         "Content-Type": "text/csv"
#     }
#     response = requests.post(MAKE_WEBHOOK_URL, data=csv_data, headers=headers)

#     if response.status_code == 200:
#         return jsonify({"message": "CSV sent to Make.com successfully!"}), 200
#     else:
#         return jsonify({"error": "Failed to send CSV", "details": response.text}),

