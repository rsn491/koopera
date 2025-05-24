from flask import Blueprint, jsonify, redirect, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from github import Github
from sqlalchemy import create_engine, select, delete, and_
from sqlalchemy.orm import sessionmaker

from src.backend.config import DATABASE_URI
from src.backend.model.code_repository import CodeRepository
from src.backend.model.notebook import Notebook

# pylint: disable=no-member
# Remove this when pylint no longer shows a false-positive "no-member" for SQLAlchemy "Session"
# Issue: https://github.com/PyCQA/pylint/issues/3610

SESSION = sessionmaker(create_engine(DATABASE_URI))

NOTEBOOKS_BLUEPRINT = Blueprint('notebooks', __name__)

@NOTEBOOKS_BLUEPRINT.route('/notebooks')
@jwt_required()
def get_all_notebooks():
    session = SESSION()
    stmt = select(Notebook)
    notebooks_result = session.execute(stmt).scalars().all()
    return jsonify({
        "notebooks": list(
            map(
                lambda notebook: {
                    'id': notebook.id,
                    'title': notebook.title,
                    'summary': notebook.summary,
                    'sha': notebook.sha,
                    'repoId': notebook.code_repo_id,
                    'repoName': notebook.code_repo.name
                },
                notebooks_result))
    })


@NOTEBOOKS_BLUEPRINT.route('/notebooks/<notebook_id>')
@jwt_required()
def get_notebook(notebook_id):
    session = SESSION()
    notebook = session.get(Notebook, int(notebook_id))

    if notebook is None:
        return jsonify({}), 404

    return redirect(
        f'/api/coderepositories/{notebook.code_repo_id}/file?path={notebook.path}&sha={notebook.sha}'
    )


@NOTEBOOKS_BLUEPRINT.route('/notebooks/<notebook_id>', methods=['DELETE'])
@jwt_required()
def delete_notebook(notebook_id):
    session = SESSION()
    stmt = delete(Notebook).where(Notebook.id == int(notebook_id))
    session.execute(stmt)
    session.commit()

    return jsonify({})


@NOTEBOOKS_BLUEPRINT.route('/notebooks', methods=['POST'])
@jwt_required()
def import_notebooks():
    session = SESSION()
    body = request.json if request.data else None

    github = Github(get_jwt_identity())

    if body and 'codeRepositories' in body:
        code_repos_req = body['codeRepositories']
        code_repos_ids = set(map(lambda repo: repo['id'], code_repos_req))
        code_repos_owners = set(map(lambda repo: repo['owner'], code_repos_req))
    else:
        # no repos passed!
        # update notebooks for current repos
        stmt_cr = select(CodeRepository)
        code_repos_db = session.execute(stmt_cr).scalars().all()
        code_repos_ids = set(map(lambda repo: repo.id, code_repos_db))
        code_repos_owners = set(map(lambda repo: repo.owner, code_repos_db))

    notebooks_added = 0
    notebooks_updated = 0

    for owner in code_repos_owners:
        # Assuming github.search_code returns objects with a .repository.id and .path, .sha, .name
        # This part interacts with an external API (github.search_code) and its filtering logic remains unchanged.
        notebooks_from_github = filter(
            lambda nb_gh: nb_gh.repository.id in code_repos_ids,
            github.search_code(f'user:{owner} extension:ipynb'))

        for notebook_gh in notebooks_from_github:
            stmt_nb_check = select(Notebook).where(
                and_(Notebook.path == notebook_gh.path,
                     Notebook.code_repo_id == notebook_gh.repository.id)
            )
            notebook_db = session.execute(stmt_nb_check).scalar_one_or_none()

            if notebook_db:
                notebook_db.sha = notebook_gh.sha
                notebooks_updated += 1
            else:
                if session.get(CodeRepository, notebook_gh.repository.id) is None:
                    # create repo
                    session.add(
                        CodeRepository(id=notebook_gh.repository.id,
                                       name=notebook_gh.repository.name,
                                       owner=owner))

                session.add(
                    Notebook(code_repo_id=notebook_gh.repository.id,
                             sha=notebook_gh.sha,
                             path=notebook_gh.path,
                             title=notebook_gh.name,
                             summary=''))
                notebooks_added += 1

    session.commit()

    return jsonify({
        'notebooksAdded': notebooks_added,
        'notebooksUpdated': notebooks_updated
    })
