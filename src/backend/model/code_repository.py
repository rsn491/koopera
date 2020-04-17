from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

CodeRepositoryBase = declarative_base()


class CodeRepository(CodeRepositoryBase):
    __tablename__ = 'code_repositories'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner = Column(String)
