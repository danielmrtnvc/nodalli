import json
import logging
import pandas as pd
from flask import Flask, request, jsonify

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Path to the Excel file where data will be saved
excel_file_path = 'form_data.xlsx'

def save_to_excel(name, email, message):
    # Create a DataFrame with the new data
    new_data = pd.DataFrame([[name, email, message]], columns=['Name', 'Email', 'Message'])
    try:
        # Try to load the existing Excel file if it exists
        df = pd.read_excel(excel_file_path)
        # Append the new data
        df = pd.concat([df, new_data], ignore_index=True)
    except FileNotFoundError:
        # If the file does not exist, start a new DataFrame
        df = new_data
    # Save the DataFrame to the Excel file
    df.to_excel(excel_file_path, index=False)
    logging.info(f"Data saved to Excel: Name: {name}, Email: {email}, Message: {message}")

@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        # Log the incoming form data for debugging
        logging.debug("Received form data: %s", request.form)
        logging.debug("Raw request data: %s", request.form.get('rawRequest'))
        # Get the raw request data (which is a JSON string)
        raw_request = request.form.get('rawRequest')
        # If the raw request exists, parse it
        if raw_request:
            data = json.loads(raw_request)

            # Extract the relevant fields from the parsed JSON
            name = data.get('q12_name')
            email = data.get('q13_email')
            message = data.get('q16_message')

            # Check if required fields are present
            if not name:
                return jsonify({"error": "Missing name"}), 400
            if not email:
                return jsonify({"error": "Missing email"}), 400
            if not message:
                return jsonify({"error": "Missing message"}), 400

            # Save the data to the Excel file
            save_to_excel(name, email, message)

            # Log the form data (instead of inserting into MySQL)
            logging.info(f"Received data - Name: {name}, Email: {email}, Message: {message}")

            # Return a success response (without database insertion)
            return jsonify({"message": "Data processed successfully!", "data": {"name": name, "email": email, "message": message}}), 200
        else:
            logging.error("No raw request data found.")
            return jsonify({"error": "No raw request data found."}), 400
    except Exception as e:
        # Log the error for debugging
        logging.error("Error occurred: %s", e)
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
if __name__ == '__main__':
    # Make sure Flask listens on all IP addresses
    app.run(debug=True, host='0.0.0.0', port=50)



# Norbert
# Something like:
# MAKE_WEBHOOK_URL = "https://hook.integromat.com/unique-webhook-id"

# @app.route('/send-data', methods=['POST'])
# def send_csv_to_make():
    # Example data to convert into CSV
    # data = [
    #     {"user_id": 1, "name": "John Doe", "email": "johndoe@example.com"},
    #     {"user_id": 2, "name": "Jane Smith", "email": "janesmith@example.com"},
    # ]

    # Convert data to CSV
    # csv_buffer = io.StringIO()
    # writer = csv.DictWriter(csv_buffer, fieldnames=["user_id", "name", "email"])
    # writer.writeheader()
    # writer.writerows(data)
    # csv_data = csv_buffer.getvalue()

    # Send CSV to Make.com webhook
    # headers = {
    #     "Content-Type": "text/csv"
    # }
    # response = requests.post(MAKE_WEBHOOK_URL, data=csv_data, headers=headers)

    # if response.status_code == 200:
    #     return jsonify({"message": "CSV sent to Make.com successfully!"}), 200
    # else:
    #     return jsonify({"error": "Failed to send CSV", "details": response.text}), 500