# __init__.py
from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from config import Config
from models import db as root_db, login_manager, ma
from app.models.OpenAI import OpenAI
from app.authentication.routes import auth
import redis
from flask_migrate import Migrate
from app.authentication.routes import auth_bp

load_dotenv()

def create_app():
    print(os.getenv('DATABASE_URL'))
    app = Flask(__name__)
    app.config.from_object(Config)
    root_db.init_app(app)  # Use the imported db instance from models.py
    login_manager.init_app(app)
    ma.init_app(app)
    migrate = Migrate(app, root_db)

    # Configure the session to use Redis
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_REDIS'] = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
    
    # Instantiate the OpenAI class and assign it to the app for easy access
    app.openai = OpenAI()

    # Register Blueprints
    from app.routes import main as main_blueprint
    # app.register_blueprint(site)
    app.register_blueprint(auth_bp)
    # app.register_blueprint(api)
    app.register_blueprint(main_blueprint)

    with app.app_context():
        print(app.config['SQLALCHEMY_DATABASE_URI'])

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


