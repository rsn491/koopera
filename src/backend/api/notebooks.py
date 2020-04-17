from flask import Blueprint, jsonify, redirect, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from github import Github
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.backend.config import DATABASE_URI
from src.backend.model.code_repository import CodeRepository
from src.backend.model.notebook import Notebook

SESSION = sessionmaker(create_engine(DATABASE_URI))

NOTEBOOKS_BLUEPRINT = Blueprint('notebooks', __name__)

@NOTEBOOKS_BLUEPRINT.route('/notebooks')
@jwt_required
def get_all_notebooks():
    session = SESSION()

    return jsonify({
        "notebooks": list(map(lambda notebook: {
            'id': notebook.id,
            'title': notebook.title,
            'summary': notebook.summary,
            'sha': notebook.sha,
            'repoId': notebook.code_repo_id,
            'repoName': notebook.code_repo.name
        }, session.query(Notebook).all()))
    })

@NOTEBOOKS_BLUEPRINT.route('/notebooks/<notebook_id>')
@jwt_required
def get_notebook(notebook_id):
    session = SESSION()

    notebook = session.query(Notebook).get(int(notebook_id))

    if notebook is None:
        return jsonify({}), 404

    return redirect(f'/api/coderepositories/{notebook.code_repo_id}/file?path={notebook.path}&sha={notebook.sha}')

@NOTEBOOKS_BLUEPRINT.route('/notebooks/<notebook_id>', methods=['DELETE'])
@jwt_required
def delete_notebook(notebook_id):
    session = SESSION()

    session.query(Notebook).filter(Notebook.id == int(notebook_id)).delete()
    session.commit()

    return jsonify({})

@NOTEBOOKS_BLUEPRINT.route('/notebooks', methods=['POST'])
@jwt_required
def import_notebooks():
    session = SESSION()
    body = request.json if request.data  else None

    github = Github(get_jwt_identity())

    if body and 'codeRepositories' in body:
        code_repos = body['codeRepositories']
        code_repos_ids = set(map(lambda repo: repo['id'], code_repos))
        code_repos_owners = set(map(lambda repo: repo['owner'], code_repos))
    else:
        # no repos passed!
        # update notebooks for current repos
        code_repos = session.query(CodeRepository).all()
        code_repos_ids = set(map(lambda repo: repo.id, code_repos))
        code_repos_owners = set(map(lambda repo: repo.owner, code_repos))

    notebooks_added = 0
    notebooks_updated = 0

    for owner in code_repos_owners:
        notebooks = filter(lambda notebook: notebook.repository.id in code_repos_ids,
            github.search_code(f'user:{owner} extension:ipynb'))

        for notebook in notebooks:
            notebook_db = session.query(Notebook).filter(
                Notebook.path == notebook.path and Notebook.code_repo_id == notebook.repository.id).first()

            if notebook_db:
                notebook_db.sha = notebook.sha
                notebooks_updated += 1
            else:
                if session.query(CodeRepository).get(notebook.repository.id) is None:
                    # create repo
                    session.add(CodeRepository(
                        id=notebook.repository.id,
                        name=notebook.repository.name,
                        owner=owner))

                session.add(Notebook(
                    code_repo_id=notebook.repository.id,
                    sha=notebook.sha,
                    path=notebook.path,
                    title=notebook.name,
                    summary=''))
                notebooks_added += 1

    session.commit()

    return jsonify({
        'notebooksAdded': notebooks_added,
        'notebooksUpdated': notebooks_updated
    })
