import nbformat
from flask import Flask, jsonify, send_from_directory
from nbconvert import HTMLExporter
from .config import JWT_SECRET_KEY, ALLOW_CORS
from datetime import datetime

from src.backend.domain.code_comment import CodeComment
from pygments import highlight
import base64
from pygments.formatters.html import HtmlFormatter
from typing import Iterable
from pygments.lexers import guess_lexer_for_filename
from flask import request
from github import Github, Repository, NamedUser
from flask_jwt_extended import (
    JWTManager, jwt_required,
    create_access_token,
    get_jwt_identity,
    jwt_optional
)

from src.backend.api.code_repositories import code_repositories_blueprint
from src.backend.api.notebooks import notebooks_blueprint

class APIService:

    @staticmethod
    def get() -> Flask:
        app = Flask(__name__)

        if ALLOW_CORS:
            from flask_cors import CORS

            CORS(app, resources={r'/*': {'origins': '*'}})

        app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
        JWTManager(app)

        app.register_blueprint(code_repositories_blueprint, url_prefix='/api')
        app.register_blueprint(notebooks_blueprint, url_prefix='/api')

        @app.route('/img/<path>')
        def get_img_file(path):
            return send_from_directory('static/img', path)

        @app.route('/js/<path>')
        def get_js_file(path):
            return send_from_directory('static/js', path)

        @app.route('/css/<path>')
        def get_css_file(path):
            return send_from_directory('static/css', path)

        @app.route('/api/login', methods=['POST'])
        @jwt_optional
        def login():
            personal_access_token = request.json['personalAccessToken']
            github = Github(personal_access_token)

            try:
                github.get_user().login
            except:
                return '', 401

            access_token = create_access_token(identity=personal_access_token)
            return jsonify(accessToken=access_token), 200

        @app.route('/api/me')
        @jwt_required
        def user_info():
            github = Github(get_jwt_identity())
            user: NamedUser = github.get_user()

            return jsonify({
                "avatarUrl": user.avatar_url,
                "name": user.name,
            })

        @app.route('/')
        @app.route('/<path:path>')
        def index(path=None):
            return app.send_static_file('index.html')

        return app
