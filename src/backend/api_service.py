from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (JWTManager, create_access_token,
                                get_jwt_identity, jwt_required)
from github import Github, NamedUser, BadCredentialsException

from src.backend.api.code_repositories import CODE_REPOSITORIES_BLUEPRINT
from src.backend.api.notebooks import NOTEBOOKS_BLUEPRINT

from .config import ALLOW_CORS, JWT_SECRET_KEY


class APIService:

    @staticmethod
    def get() -> Flask:
        app = Flask(__name__)

        if ALLOW_CORS:
            CORS(app, resources={r'/*': {'origins': '*'}})

        app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
        JWTManager(app)

        app.register_blueprint(CODE_REPOSITORIES_BLUEPRINT, url_prefix='/api')
        app.register_blueprint(NOTEBOOKS_BLUEPRINT, url_prefix='/api')

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
        @jwt_required(optional=True)
        def login():
            personal_access_token = request.json['personalAccessToken']
            github = Github(personal_access_token)

            try:
                github.get_user().login
            except BadCredentialsException:
                return '', 401

            access_token = create_access_token(identity=personal_access_token)
            return jsonify(accessToken=access_token), 200

        @app.route('/api/me')
        @jwt_required()
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
