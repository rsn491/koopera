from flask import Blueprint, jsonify, request, redirect
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import create_engine
from github import Github, Repository
from sqlalchemy.orm import sessionmaker
from src.backend.config import DATABASE_URI
from src.backend.model.notebook import Notebook
from src.backend.model.code_repository import CodeRepository

Session = sessionmaker(create_engine(DATABASE_URI))

notebooks_blueprint = Blueprint('notebooks', __name__)

@notebooks_blueprint.route('/notebooks')
@jwt_required
def get_all_notebooks():
    session = Session()

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

@notebooks_blueprint.route('/notebooks/<notebook_id>')
@jwt_required
def get_notebook(notebook_id):
    session = Session()

    notebook = session.query(Notebook).get(int(notebook_id))

    if notebook is None:
        return jsonify({}), 404

    return redirect(f'/api/coderepositories/{notebook.code_repo_id}/file?path={notebook.path}&sha={notebook.sha}')

@notebooks_blueprint.route('/notebooks/<notebook_id>', methods=['DELETE'])
@jwt_required
def delete_notebook(notebook_id):
    session = Session()

    session.query(Notebook).filter(Notebook.id == int(notebook_id)).delete()
    session.commit()

    return jsonify({})

@notebooks_blueprint.route('/notebooks', methods=['POST'])
@jwt_required
def importNotebooks():
    session = Session()
    body = request.json if request.data  else None

    github = Github('118756d7c72752efee9f066e4083e86af86517c9')

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
