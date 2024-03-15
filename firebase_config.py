# firebase_config.py
import os
import json
from firebase_admin import credentials, initialize_app
from dotenv import load_dotenv

load_dotenv()

# Load Firebase service account credentials from environment variable
service_account_key_json = json.loads(os.environ["SERVICE_ACCOUNT_KEY_JSON"])

# Initialize Firebase app with the credentials
cred = credentials.Certificate(service_account_key_json)
firebase_app = initialize_app(cred)
