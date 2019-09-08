from typing import Optional
from datetime import datetime
from github.IssueComment import IssueComment


class CodeComment:

    def __init__(self, file_path: str, code_block_id: int, body: str, author: str, updated_at: datetime):
        self.filePath = file_path
        self.codeBlockId = code_block_id
        self.body = body
        self.author = author
        self.updatedAt = updated_at

    def to_github_issue_comment_body(self):
        return "[%s|%s] %s" % (self.filePath, self.codeBlockId, self.body)

    @staticmethod
    def from_github_issue_comment(issue_comment: IssueComment) -> Optional['CodeComment']:
        body = issue_comment.body
        first_separator_index = body.find('|')
        second_separator_index = body.find(']')

        if first_separator_index == -1 \
                or second_separator_index == -1 \
                or first_separator_index > second_separator_index \
                or body.__len__() < 3 \
                or body[0] != '[':
            return None

        code_block_id = body[first_separator_index + 1:second_separator_index]

        if code_block_id.isdigit() is False:
            return None

        return CodeComment(
            file_path=body[1:first_separator_index],
            code_block_id=int(code_block_id),
            body=body[second_separator_index + 2:body.__len__()],
            author=issue_comment.user.name,
            updated_at=issue_comment.updated_at.timestamp())
