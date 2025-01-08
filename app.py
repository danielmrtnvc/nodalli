
import json
import logging
import pymysql
from flask import Flask, request, jsonify

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# MySQL database connection details
MYSQL_HOST = 'localhost'  # Replace with your host
MYSQL_USER = 'root'       # Replace with your username
MYSQL_PASSWORD = '18002672001'  # Replace with your password
MYSQL_DB = 'form_data_db'  # Replace with your database name

# Function to save form data to the MySQL database
def save_to_mysql(name, email, message):
    try:
        # Connect to the MySQL database
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )

        with connection.cursor() as cursor:
            # Create the SQL query to insert data
            query = "INSERT INTO form_data (name, email, message) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, message))

            # Commit the changes to the database
            connection.commit()

        logging.info(f"Data saved to MySQL: Name: {name}, Email: {email}, Message: {message}")

    except Exception as e:
        logging.error(f"Error saving to database: {e}")
    finally:
        if connection:
            connection.close()

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

            # Save the data to the MySQL database
            save_to_mysql(name, email, message)

            # Log the form data (now saved to MySQL)
            logging.info(f"Received data - Name: {name}, Email: {email}, Message: {message}")

            # Return a success response
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
