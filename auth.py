import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Defining the required parameters
url = 'https://api.upstox.com/v2/login/authorization/token'
auth_code = os.getenv('AUTH_CODE')
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
redirect_uri = 'http://localhost:8000'

# Setting up the payload
payload = {
    'code': auth_code,
    'client_id': api_key,
    'client_secret': api_secret,
    'redirect_uri': redirect_uri,
    'grant_type': 'authorization_code'
}

# Setting up the headers
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Making the POST request
response = requests.post(url, headers=headers, data=payload)

# Checking if the request was successful and print the result
if response.status_code == 200:
    # Printing the JSON response containing the access token
    print("Access Token:", response.json())
else:
    print("Failed to get access token:", response.status_code, response.text)
