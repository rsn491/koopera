import nbformat
from flask import Flask, jsonify, send_from_directory
from nbconvert import HTMLExporter
from .config import JWT_SECRET_KEY, ALLOW_CORS
from datetime import datetime

from src.backend.code_comment import CodeComment
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


class APIService:

    @staticmethod
    def get() -> Flask:
        app = Flask(__name__)

        if ALLOW_CORS:
            from flask_cors import CORS

            CORS(app, resources={r'/*': {'origins': '*'}})

        app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
        JWTManager(app)

        @app.route('/img/<path>')
        def get_img_file(path):
            return send_from_directory('static/img', path)

        @app.route('/js/<path>')
        def get_js_file(path):
            return send_from_directory('static/js', path)

        @app.route('/css/<path>')
        def get_css_file(path):
            return send_from_directory('static/css', path)

        @app.route('/')
        @app.route('/login')
        @app.route('/coderepositories/<code_repository_id>/pullrequests')
        @app.route('/coderepositories/<code_repository_id>/pullrequests/<pull_request_number>')
        def index(code_repository_id=None, pull_request_number=None):
            return app.send_static_file('index.html')

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

        @app.route('/api/coderepositories')
        @jwt_required
        def get_code_repositories():
            github = Github(get_jwt_identity())
            code_repos: Iterable[Repository] = github.get_user().get_repos()

            return jsonify({
                "codeRepositories": list(map(lambda repo: {
                    "id": repo.id,
                    "name": repo.name,
                    "openPullRequestCount": repo.get_pulls().totalCount
                }, code_repos))
            })

        @app.route('/api/coderepositories/<code_repository_id>/pullrequests')
        @jwt_required
        def get_pull_requests(code_repository_id: int):
            github = Github(get_jwt_identity())
            code_repository = github.get_repo(full_name_or_id=int(code_repository_id))

            return jsonify({
                "pullRequests": list(map(lambda pull_request: {
                    "id": pull_request.id,
                    "number": pull_request.number,
                    "title": pull_request.title,
                    "userName": pull_request.user.name
                }, code_repository.get_pulls().get_page(0)))
            })

        @app.route('/api/coderepositories/<code_repository_id>/pullrequests/<pull_request_id>')
        @jwt_required
        def get_pull_request(code_repository_id, pull_request_id):
            github = Github(get_jwt_identity())
            code_repository: Repository = github.get_repo(full_name_or_id=int(code_repository_id))
            pull_request = code_repository.get_pull(number=int(pull_request_id))

            code_comments = map(lambda code_comment: CodeComment.from_github_code_comment(
                    code_comment), pull_request.get_comments())

            return jsonify({
                "comments": list(map(lambda code_comment: code_comment.__dict__,
                                          filter(lambda code_comment: code_comment is not None, code_comments))),
                "files": list(map(lambda file: {
                    "path": file.filename,
                    "ref": pull_request.base.ref if file.status == 'removed' else pull_request.head.ref,
                    "rawUrl": file.raw_url,
                      "status": file.status,
                    "sha": file.sha
                }, pull_request.get_files()))
            })

        @app.route('/api/coderepositories/<code_repository_id>/pullrequests/<pull_request_id>/comment', methods=['POST'])
        @jwt_required
        def add_comment(code_repository_id, pull_request_id):
            body = request.json

            github = Github(get_jwt_identity())

            code_comment = CodeComment(
                file_path=body['path'],
                code_block_id=body['codeBlockId'],
                body=body['comment'],
                author=github.get_user().name,
                updated_at=datetime.utcnow())
                
            code_repo: Repository = github.get_repo(int(code_repository_id))
            pull_request = code_repo.get_pull(number=int(pull_request_id))
            commit = code_repo.get_commit(pull_request.head.sha)

            pull_request.create_comment(
                code_comment.get_github_comment(), 
                commit, 
                code_comment.get_github_path(),
                code_comment.get_github_position())

            return '', 200

        @app.route('/api/coderepositories/<code_repository_id>/file')
        @jwt_required
        def get_file(code_repository_id):
            file_path = request.args.get("path")
            file_sha = request.args.get("sha")

            github = Github(get_jwt_identity())
            code_repo: Repository = github.get_repo(int(code_repository_id))

            file_blob = code_repo.get_git_blob(file_sha)
            file_content = base64.b64decode(file_blob.content)

            if file_path.endswith('.ipynb'):
                html_exporter = HTMLExporter()
                html_exporter.template_file = 'basic'
                notebook = nbformat.reads(file_content, as_version=4)
                (body, resources) = html_exporter.from_notebook_node(notebook)
            else:
                lexer = guess_lexer_for_filename(file_path, '', stripall=True)
                formatter = HtmlFormatter(linenos='inline', full=True, noclasses=False, nobackground=True, lineseparator="<br/>", classprefix='koopera-code-viewer')
                body = highlight(file_content, lexer, formatter)

            return jsonify({
                'body': body
            })

        return app
