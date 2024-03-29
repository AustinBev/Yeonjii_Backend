# authentication/routes.py
from models import User, db
from flask import Blueprint, request, jsonify, render_template
import os
from firebase_admin import auth, credentials, initialize_app, get_app
import json

# Define the Blueprint
auth_bp = Blueprint('auth', __name__, template_folder='auth_templates', url_prefix='/auth')

# Initialize Firebase Admin SDK
def initialize_firebase_app():
    try:
        # Check if the Firebase app is already initialized
        get_app()
    except ValueError as e:
        # If not, initialize the app
        service_account_key_path = os.getenv('SERVICE_ACCOUNT_KEY_PATH')
        if service_account_key_path:
            with open(service_account_key_path, 'r') as f:
                service_account_info = json.load(f)
            cred = credentials.Certificate(service_account_info)
            initialize_app(cred)
        else:
            print("Firebase service account key path not found in environment variables.")

# Call the initialization function at the start of your application
initialize_firebase_app()

@auth_bp.route('/token', methods=['POST'])
def get_token():
    id_token_str = request.json.get('id_token')
    if not id_token_str:
        return jsonify({'message': 'ID token is required'}), 400

    try:
        # Verify the ID token and extract the user's email
        decoded_token = auth.verify_id_token(id_token_str)
        user_email = decoded_token['email']

        # Check if user exists in the database
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'message': 'User does not exist'}), 401

        return jsonify({'token': user.token}), 200

    except ValueError as e:
        return jsonify({'message': str(e)}), 401

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('sign_up.html')

    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        id_token_str = data.get('id_token')

        if not email or not id_token_str:
            return jsonify({'message': 'Email and ID token are required'}), 400

        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token_str)
            user_email = decoded_token['email']

            if user_email != email:
                return jsonify({'message': 'Email does not match ID token email.'}), 400

        except ValueError as e:
            return jsonify({'message': str(e)}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'User already exists', 'id': existing_user.id}), 409

        # Create new user
        user = User(email=email, g_auth_verify=True)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User created successfully', 'id': user.id, 'token': user.token}), 201
