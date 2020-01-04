from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from .code_repository import CodeRepository

NotebookBase = declarative_base()

class Notebook(NotebookBase):
    __tablename__ = 'notebooks'

    id = Column(Integer, primary_key=True)
    code_repo_id = Column(Integer, ForeignKey(CodeRepository.id))
    sha = Column(String)
    path = Column(String)
    title = Column(String)
    summary = Column(String)

    code_repo = relationship(CodeRepository, lazy='joined')
