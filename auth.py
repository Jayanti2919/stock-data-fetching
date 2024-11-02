import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Define the required parameters
url = 'https://api.upstox.com/v2/login/authorization/token'
auth_code = os.getenv('AUTH_CODE')
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
redirect_uri = 'http://localhost:8000'

# Set up the payload
payload = {
    'code': auth_code,
    'client_id': api_key,
    'client_secret': api_secret,
    'redirect_uri': redirect_uri,
    'grant_type': 'authorization_code'
}

# Set up the headers
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Make the POST request
response = requests.post(url, headers=headers, data=payload)

# Check if the request was successful and print the result
if response.status_code == 200:
    # Print the JSON response containing the access token
    print("Access Token:", response.json())
else:
    print("Failed to get access token:", response.status_code, response.text)
