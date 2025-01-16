import requests

# Webhook URL from Make.com
webhook_url = "https://hook.us2.make.com/j27vxnv4bqy4y7nxaxmh6hfdir97x0qf"

# Path to the CSV file
file_path = r"C:\New folder\CSV\example.csv"

# Send the CSV file to the webhook
with open(file_path, "rb") as file:
    response = requests.post(webhook_url, files={"file": file})

# Print the response
if response.status_code == 200:
    print("File sent successfully!")
else:
    print(f"Failed to send file. Status code: {response.status_code}, Response: {response.text}")
