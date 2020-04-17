import base64
from datetime import datetime
from typing import Iterable

import markdown
import nbformat
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from github import Github, GithubException, Repository
from mdx_gfm import GithubFlavoredMarkdownExtension
from nbconvert import HTMLExporter
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename

from src.backend.domain.code_comment import CodeComment

CODE_REPOSITORIES_BLUEPRINT = Blueprint('code_repositories', __name__)


@CODE_REPOSITORIES_BLUEPRINT.route('/coderepositories')
@jwt_required
def get_code_repositories():
    github = Github(get_jwt_identity())
    code_repos: Iterable[Repository] = github.get_user().get_repos()

    return jsonify({
        "codeRepositories": list(
            map(
                lambda repo: {
                    "id": repo.id,
                    "owner": repo.owner.login,
                    "name": repo.name,
                    "openPullRequestCount": repo.get_pulls().totalCount
                }, code_repos))
    })


@CODE_REPOSITORIES_BLUEPRINT.route(
    '/coderepositories/<code_repository_id>/pullrequests')
@jwt_required
def get_pull_requests(code_repository_id: int):
    github = Github(get_jwt_identity())
    code_repository = github.get_repo(full_name_or_id=int(code_repository_id))

    return jsonify({
        "codeRepoName": code_repository.name,
        "pullRequests": list(
            map(
                lambda pull_request: {
                    "id": pull_request.id,
                    "number": pull_request.number,
                    "title": pull_request.title,
                    "userName": pull_request.user.name
                },
                code_repository.get_pulls().get_page(0)))
    })


@CODE_REPOSITORIES_BLUEPRINT.route(
    '/coderepositories/<code_repository_id>/pullrequests/<pull_request_id>')
@jwt_required
def get_pull_request(code_repository_id, pull_request_id):
    github = Github(get_jwt_identity())
    code_repository: Repository = github.get_repo(
        full_name_or_id=int(code_repository_id))
    pull_request = code_repository.get_pull(number=int(pull_request_id))

    code_comments = map(
        lambda code_comment: CodeComment.from_github_code_comment(code_comment),
        pull_request.get_comments())

    return jsonify({
        "title": pull_request.title,
        "codeRepoName": code_repository.name,
        "userAvatarUrl": pull_request.user.avatar_url,
        "body": markdown.markdown(
            pull_request.body, extensions=[GithubFlavoredMarkdownExtension()]),
        "state": pull_request.state.capitalize(),
        "comments": list(
            map(
                lambda code_comment: code_comment.__dict__,
                filter(lambda code_comment: code_comment is not None,
                       code_comments))),
        "files": list(
            map(
                lambda file: {
                    "path": file.filename,
                    "ref": pull_request.base.ref if file.status == 'removed'
                           else pull_request.head.ref,
                    "rawUrl": file.raw_url,
                    "status": file.status,
                    "sha": file.sha
                }, pull_request.get_files()))
    })


@CODE_REPOSITORIES_BLUEPRINT.route(
    '/coderepositories/<code_repository_id>/pullrequests/<pull_request_id>/merge',
    methods=['POST'])
@jwt_required
def merge_pull_request(code_repository_id, pull_request_id):
    github = Github(get_jwt_identity())
    code_repository: Repository = github.get_repo(
        full_name_or_id=int(code_repository_id))
    pull_request = code_repository.get_pull(number=int(pull_request_id))

    merge_strategy = request.json['mergeStrategy']

    try:
        pull_request.merge(merge_method=merge_strategy)
    except GithubException as exception:
        return jsonify({'message': exception.data['message']}), 400

    return '', 200


@CODE_REPOSITORIES_BLUEPRINT.route(
    '/coderepositories/<code_repository_id>/pullrequests/<pull_request_id>/comment',
    methods=['POST'])
@jwt_required
def add_comment(code_repository_id, pull_request_id):
    body = request.json

    github = Github(get_jwt_identity())

    in_reply_to_comment_id = body['inReplyToCommentId']
    code_comment = CodeComment(file_path=body['path'],
                               code_block_id=body['codeBlockId'],
                               body=body['comment'],
                               author=github.get_user().name,
                               updated_at=datetime.utcnow())

    code_repo: Repository = github.get_repo(int(code_repository_id))
    pull_request = code_repo.get_pull(number=int(pull_request_id))

    if in_reply_to_comment_id:
        created_comment = pull_request.create_review_comment_reply(
            in_reply_to_comment_id, code_comment.get_github_comment())
    else:
        commit = code_repo.get_commit(pull_request.head.sha)
        created_comment = pull_request.create_comment(
            code_comment.get_github_comment(), commit,
            code_comment.get_github_path(), code_comment.get_github_position())

    return jsonify({'id': created_comment.id})


@CODE_REPOSITORIES_BLUEPRINT.route('/coderepositories/<code_repository_id>/file'
                                  )
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
        (body, _) = html_exporter.from_notebook_node(notebook)
    else:
        lexer = guess_lexer_for_filename(file_path, '', stripall=True)
        formatter = HtmlFormatter(linenos='inline',
                                  full=True,
                                  noclasses=False,
                                  nobackground=True,
                                  lineseparator="<br/>",
                                  classprefix='koopera-code-viewer')
        body = highlight(file_content, lexer, formatter)

    return jsonify({'body': body})
