import uuid
import json
from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, render_template, request, redirect, url_for, session
from backend.auth.decorator import login_required, role_required
from backend.extensions import mongo
from functools import wraps
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from config import Config
from flask_smorest import Api

def create_app():
    app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/statics')
    app.config.from_object(Config)
    mongo.init_app(app)

    api = Api(app)

    from backend.api.medpay_api import medpay_bp
    api.register_blueprint(medpay_bp)

    from backend.api.clinical_api import clinical_bp
    api.register_blueprint(clinical_bp)

    from backend.api.admin_api import admin_bp
    api.register_blueprint(admin_bp)

    from backend.auth.auth_route import auth_bp
    api.register_blueprint(auth_bp)
    return app
