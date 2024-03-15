# authentication/routes.py
from models import User, db
from flask import Blueprint, request, jsonify, render_template, g, make_response
from flask_cors import CORS
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests
import requests
from helpers import token_required
from flask import make_response
from flask_login import current_user

"""
- Fetch Google's public keys for verifying ID tokens.
- Define a load_user function to protect routes and load the current user from the token.
- Verify the provided Firebase ID token and extract the user's email.
- Check if the user exists in the database, and if not, allow sign-up and user creation.
- Retrieve the user's data, such as ID and token, and return it in a response.
- Use the @load_user decorator to ensure the current user is loaded for specific routes.
"""

auth = Blueprint('auth', __name__, template_folder='auth_templates', url_prefix='/auth')

# Fetch Google public keys
response = requests.get('https://www.googleapis.com/oauth2/v3/certs')
public_keys = response.json()


# Protects routes in the app by checking the validity of an authentication token
def load_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            return jsonify({'message': 'Token is missing'}), 401

        user = User.query.filter_by(token=token).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        g.current_user = user  # Set the current_user attribute in the g object
        return f(*args, **kwargs)

    return decorated_function


# verifies the provided Firebase ID token, extracts the user's email from the token,
# checks if the user exists in the database, and if so,
# returns a JSON response with the user's token
@auth.route('/token', methods=['POST'])
def get_token():
    id_token_str = request.json.get('id_token')

    if not id_token_str:
        return jsonify({'message': 'ID token is required'}), 400

    try:
        # Verify the ID token
        req = g_requests.Request()
        decoded_token = id_token.verify_firebase_token(id_token_str, req)

        # ID token is valid, extract the user's email
        user_email = decoded_token['email']

        # Check if user exists in the database
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'message': 'User does not exist'}), 401

        return jsonify({'token': user.token}), 200

    except ValueError as e:
        return jsonify({'message': str(e)}), 401


#  retrieves the user's data (specifically the user's ID and token) from the g.current_user object.
# It then creates a JSON response with the user's data
@auth.route('/userdata/<string:user_id>', methods=['GET'])
@load_user
def get_user_data(user_id):
    user_data = {
        "id": g.current_user.id,
        "token": g.current_user.token,
    }
    response = make_response(jsonify(user_data), 200)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


# renders a sign-up template and returns it
# If the verification is successful, 
# it checks if a user with the provided email already exists in the database
# If the user does not exist, it creates a new user in the database, saves the ID token,
#  and returns a JSON response indicating that the user has been created successfully
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('sign_up.html')

    if request.method == 'POST':
        data = request.json
        # print(data)
        email = data.get('email')
        id_token_str = data.get('id_token')

        if not email or not id_token_str:
            return jsonify({'message': 'Email and ID token are required'}), 400

        try:
            # Verify the ID token
            req = g_requests.Request()
            decoded_token = id_token.verify_firebase_token(id_token_str, req)

            # ID token is valid, extract the user's email
            user_email = decoded_token['email']

            if user_email != email:
                raise ValueError('Email does not match ID token email.')

        except ValueError as e:
            return jsonify({'message': str(e)}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            response = jsonify({'message': 'User already exists', 'token': existing_user.token, 'id': existing_user.id})
            return response, 409

        # Create new user and save ID token
        user = User(email=email, g_auth_verify=True) # Set g_auth_verify to True
        db.session.add(user)
        db.session.commit()

        response = jsonify({'message': 'User created successfully', 'id': user.id, 'token': user.token})
        return response, 201