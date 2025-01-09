
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

# Nour
# Something like:

# APIFY_BASE_URL = "https://api.apify.com/v2/actor-tasks"
# APIFY_API_TOKEN = "your_apify_api_token"

# @app.route('/run-actor', methods=['POST'])
# def run_actor():
#     try:
#         # Extract custom input parameters from the request
#         data = request.json
#         actor_id = data.get('actorId')
#         input_params = data.get('inputParams', {})

#         if not actor_id:
#             return jsonify({"error": "actorId is required"}), 400

#         # Endpoint to call the Apify actor
#         actor_run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_API_TOKEN}"

#         # Send a POST request to the Apify API with the input parameters
#         response = requests.post(actor_run_url, json={"input": input_params})

#         # Handle the response
#         if response.status_code == 201:
#             result = response.json()
#             return jsonify({
#                 "status": "Actor started successfully",
#                 "data": result
#             }), 200
#         else:
#             return jsonify({
#                 "error": "Failed to start the actor",
#                 "details": response.json()
#             }), response.status_code

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# Ahmed
# Something like:
# SUPABASE_HOST = 'your_supabase_host'  # Replace with your Supabase host (e.g., 'db.ssupabase.co')
# SUPABASE_DB = 'postgres'              # Default database name
# SUPABASE_USER = 'your_user'           # Replace with your Supabase username
# SUPABASE_PASSWORD = 'your_password'   # Replace with your Supabase password
# SUPABASE_PORT = 5432                  # Default PostgreSQL port

# # Function to save form data to the PostgreSQL database
# def save_to_postgres(name, email, message):
#     try:
#         # Connect to the Supabase PostgreSQL database
#         connection = psycopg2.connect(
#             host=SUPABASE_HOST,
#             database=SUPABASE_DB,
#             user=SUPABASE_USER,
#             password=SUPABASE_PASSWORD,
#             port=SUPABASE_PORT
#         )

#         with connection.cursor() as cursor:
#             # Define the table name and SQL query to insert data
#             query = sql.SQL("INSERT INTO {table} (name, email, message) VALUES (%s, %s, %s)").format(
#                 table=sql.Identifier('form_data')
#             )
#             cursor.execute(query, (name, email, message))

#             # Commit the changes to the database
#             connection.commit()

#         logging.info(f"Data saved to PostgreSQL: Name: {name}, Email: {email}, Message: {message}")

#     except Exception as e:
#         logging.error(f"Error saving to PostgreSQL: {e}")
#     finally:
#         if connection:
#             connection.close()

# @app.route('/submit_form', methods=['POST'])
# def submit_form():
#     try:
#         # Log the incoming form data for debugging
#         logging.debug("Received form data: %s", request.form)
#         logging.debug("Raw request data: %s", request.form.get('rawRequest'))

#         # Get the raw request data (which is a JSON string)
#         raw_request = request.form.get('rawRequest')

#         # If the raw request exists, parse it
#         if raw_request:
#             data = json.loads(raw_request)

#             # Extract the relevant fields from the parsed JSON
#             name = data.get('q12_name')
#             email = data.get('q13_email')
#             message = data.get('q16_message')

#             # Check if required fields are present
#             if not name:
#                 return jsonify({"error": "Missing name"}), 400
#             if not email:
#                 return jsonify({"error": "Missing email"}), 400
#             if not message:
#                 return jsonify({"error": "Missing message"}), 400

#             # Save the data to the PostgreSQL database
#             save_to_postgres(name, email, message)

#             # Log the form data (now saved to PostgreSQL)
#             logging.info(f"Received data - Name: {name}, Email: {email}, Message: {message}")

#             # Return a success response
#             return jsonify({"message": "Data processed successfully!", "data": {"name": name, "email": email, "message": message}}), 200
#         else:
#             logging.error("No raw request data found.")
#             return jsonify({"error": "No raw request data found."}), 400
#     except Exception as e:
#         # Log the error for debugging
#         logging.error("Error occurred: %s", e)
#         return jsonify({"error": f"Internal server error: {str(e)}"}), 500
