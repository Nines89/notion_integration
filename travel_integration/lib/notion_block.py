from lib.notion_client import NotionApiClient
from lib.utils import BlockType

import re


class NotionBlock:
    @classmethod
    def get(cls, *args, **kwargs):
        return NotionBlockGet(*args, **kwargs)


class NotionBlockGet(NotionApiClient):
    pattern = re.compile(r"notion\.so/[^/\?]*-([0-9a-f]{32})")  # noqa

    def __init__(self, token: str, *args, **kwargs):
        match = self.pattern.search(token)
        if match:
            token = match.group(1)
        self.token = token.replace('-', '')  # inserito per quanto si recupera la pagina da un database
        if len(token) != 32:
            raise ValueError('Token Length is Incorrect')
        super().__init__(*args, **kwargs)

        # self.get_page_content()