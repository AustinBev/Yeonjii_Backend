# routes.py
from __future__ import print_function
from flask import render_template, request, jsonify, session, Blueprint # Flask module for handling HTTP requests and responses
from app.models.OpenAI import OpenAI as OpenAIModel # Custom OpenAI model
from app.extensions import redis_client # Redis client from extensions module
import uuid # generates unique identifiers
from pdfminer.high_level import extract_text # PDF extraction tool
import io # Handles byte streams
from firebase_admin import auth, credentials, initialize_app # Firebase admin SDK for auth and app initialization
# from app.models.pro_writing_aid import check_grammar
import json
import os

# Defines the main blueprint for routes
main = Blueprint('main', __name__)
# creates an instance of the OpenAI model
open_ai_model = OpenAIModel()

# Load the service account key from the environment variable
service_account_key_json = os.getenv('SERVICE_ACCOUNT_KEY_JSON')
if service_account_key_json:
    service_account_info = json.loads(service_account_key_json)
    cred = credentials.Certificate(service_account_info)
    firebase_app = initialize_app(cred)
else:
    print("Firebase service account key not found in environment variables.")

default_app = initialize_app

# The route decorator defines the endpoint for the root URL
@main.route('/')
def home_page():
    gpt_model = open_ai_model.get_openai_model()
    print("GPT Model:", gpt_model) 
    return render_template('index.html', gpt_model=gpt_model)

@main.route('/profile')
def profile():
    return render_template('profile.html')

@main.route('/verify_token', methods=['POST'])
def verify_token():
    id_token = request.json.get('idToken')
    try:
        # check token against firebase Auth
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        return jsonify({'success': True, 'uid': uid}), 200
    except auth.AuthError as e:
        return jsonify({'success': False, 'message': str(e)}), 401

@main.route('/get_session_id', methods=['GET'])
def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return jsonify(session_id=session['session_id'])

@main.route('/generate_letter', methods=['POST'])
def generate_cover_letter():
    data = request.get_json()
    session_id = data.get('session_id')

    if not session_id:
        return jsonify(error='Session ID not provided'), 400

    try:
        cover_letter = open_ai_model.generate_cover_letter(session_id)
        if not cover_letter:
            return jsonify(error='Error generating cover letter'), 500
        return jsonify(cover_letter=cover_letter)
    except Exception as e:
        print(f"Error during cover letter generation: {e}")
        return jsonify(error='Internal server error'), 500

# @main.route('/check_grammar', methods=['POST'])
# def check_grammar_route():
#     data = request.get_json()
#     text = data.get('text')

#     if not text:
#         return jsonify(error='No text provided'), 400

#     try:
#         # Assuming you have a method in your OpenAIModel for checking grammar
#         grammar_issues = check_grammar(text)
#         return jsonify(grammar_issues=grammar_issues)
#     except Exception as e:
#         print(f"Error checking grammar: {e}")
#         return jsonify(error='Internal error'), 500
    
@main.route('/set_resume', methods=['POST'])
def set_resume():
    data = request.get_json()
    resume = data.get('resume')
    session_id = data.get('session_id')
    if resume and session_id:
        resume_key = f"{session_id}_resume"
        redis_client.setex(resume_key, 1800, resume)
        return jsonify(message='Resume saved successfully in Redis')
    else:
        return jsonify(error='No resume data or session ID provided'), 400

@main.route('/upload_resume', methods=['POST'])
def upload_resume():
    try:
        if 'resume' not in request.files:
            return jsonify(error='No file part'), 400
        file = request.files['resume']
        if file.filename == '':
            return jsonify(error='No selected file'), 400
        if file and file.filename.endswith('.pdf'):
            session_id = request.form.get('session_id')

            # Read the file stream and extract text using PdfReader
            file_stream = io.BytesIO(file.read())
            # pdf_reader = PdfReader(file_stream)
            # text = ''
            # for page in pdf_reader.pages:
            #     text += page.extract_text()
            text = extract_text(file_stream)

            # Save extracted text to Redis
            resume_key = f"{session_id}_resume"
            redis_client.setex(resume_key, 1800, text)
            return jsonify(message='Resume uploaded and saved successfully')
        else:
            return jsonify(error='Invalid file format'), 400
    except Exception as e:
        return jsonify(error=str(e)), 500


@main.route('/set_job_description', methods=['POST'])
def set_job_description():
    data = request.get_json()
    job_description = data.get('job_description')
    session_id = data.get('session_id')
    if job_description and session_id:
        job_description_key = f"{session_id}_job_description"
        redis_client.setex(job_description_key, 1800, job_description)
        return jsonify(message='Job description saved successfully in Redis')
    else:
        return jsonify(error='No job description data provided'), 400

@main.route('/set_job_role', methods=['POST'])
def set_role():
    data = request.get_json()
    job_role = data.get('job_role')
    session_id = data.get('session_id')
    if job_role and session_id:
        job_role_key = f"{session_id}_job_role"
        redis_client.setex(job_role_key, 1800, job_role)
        return jsonify(message='Job role saved successfully in Redis')
    else:
        return jsonify(error='No job role data provided'), 400
    
@main.route('/set_company', methods=['POST'])
def set_company():
    data = request.get_json()
    company = data.get('company')
    session_id = data.get('session_id')
    if company and session_id:
        company_key = f"{session_id}_company"
        redis_client.setex(company_key, 1800, company)
        return jsonify(message='Company saved successfully in Redis')
    else:
        return jsonify(error='No company data provided'), 400

@main.route('/set_story', methods=['POST'])
def set_story():
    data = request.get_json()
    story = data.get('story')
    session_id = data.get('session_id')
    if story and session_id:
        story_key = f"{session_id}_story"
        redis_client.setex(story_key, 1800, story)
        return jsonify(message='Professional story saved successfully to Redis')
    else:
        return jsonify(error='No professional story data provided'), 400
    
@main.route('/wake_up')
def wake_up():
    return 'Backend active', 200