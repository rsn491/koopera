from typing import Optional
from datetime import datetime
from github.PullRequestComment import PullRequestComment


class CodeComment:

    def __init__(self, file_path: str, code_block_id: int, body: str, author: str, updated_at: datetime, id: Optional[int] = None):
        self.id = id
        self.filePath = file_path
        self.codeBlockId = code_block_id
        self.body = body
        self.author = author
        self.updatedAt = updated_at

    @classmethod
    def is_ipynb_file(cls, path):
        return path.endswith('.ipynb')

    def get_github_path(self) -> int:
        return self.filePath

    def get_github_position(self) -> int:
        if self.is_ipynb_file(self.filePath):
            return 1

        return self.codeBlockId + 1

    def get_github_comment(self) -> str:
        if self.is_ipynb_file(self.filePath):
            return f'[{self.codeBlockId}] {self.body}'

        return self.body

    @classmethod
    def from_github_code_comment(cls, code_comment: PullRequestComment):
        body = code_comment.body

        if cls.is_ipynb_file(code_comment.path):
            separator_index = body.find(']')
            code_block_id = body[1: separator_index]

            if code_block_id.isdigit() is False:
                return None

            code_block_id = int(code_block_id)
            body = body[separator_index + 2: body.__len__()]
        else:
            code_block_id = code_comment.position - 1 if code_comment.position is not None else 1

        return CodeComment(
            id=code_comment.id,
            file_path=code_comment.path,
            code_block_id=code_block_id,
            body=body,
            author=code_comment.user.name,
            updated_at=code_comment.updated_at.timestamp())
