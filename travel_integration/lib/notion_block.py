import re
from typing import Any

from lib.notion_client import NotionApiClient, NGET
from lib.notion_types import (
    NUser, NDate, BASECLASSS
)


class BlockError(Exception):
    pass


class NotionBlock:
    id_ = None

    @classmethod
    def get(cls, *args, **kwargs):
        return NotionBlockGet(*args, **kwargs)


class NotionBlockGet(NotionApiClient):
    info = None
    children = []
    pattern = re.compile(r"notion\.so/[^/\?]*-([0-9a-f]{32})")  # noqa
    block_type = 'block'

    def __init__(self, token: str, *args, **kwargs):
        match = self.pattern.search(token)
        if match:
            token = match.group(1)
        self.token = token.replace('-', '')  # inserito per quanto si recupera la pagina da un database
        if len(self.token) != 32:
            raise ValueError('Token Length is Incorrect')
        super().__init__(*args, **kwargs)
        self.api_url = f"https://api.notion.com/v1/blocks/{self.token}"  # noqa

    def get_block_content(self):
        self.info = NGET(self.api_url, self.headers)
        if self.block_type != self.is_block:
            raise BlockError("Page Class are being used for a not page object")
        # self.page_properties = self.get_page_properties()
        # self.page_children = self.get_page_children()

    @property
    def is_block(self):
        return self.info['object']

    @property
    def is_archived(self):
        return self.info['archived']

    @property
    def is_trash(self):
        return self.info['in_trash']

    @property
    def is_locked(self):
        return self.info['is_locked']

    @property
    def retrieve_id(self):
        return self.info['id']

    @property
    def creation_info(self):
        return {'user': NUser(self.info['created_by'])['id'],
                'create_time': NDate(self.info['created_time'])['time']}

    @property
    def last_edit_info(self):
        return {'user': NUser(self.info['last_edited_by'])['id'],
                'create_time': NDate(self.info['last_edited_time'])['time']}

    def get_block_children(self, size: int = 100):
        url = f"https://api.notion.com/v1/blocks/{self.token}/children?page_size={size}"  # noqa
        children = NGET(url, self.headers)['results']  # torniamo automaticamente la lista di blocchi
        for child in children:
            # block = create_block(block_type_str=child['type'],
            #                      block=child,
            #                      )
            pass # block.id_ = child['id']


class Divider(NotionBlock, BASECLASSS):
    """
    Possiamo anche fare la get su questo blocco:
                    inner_block = block.get(
                                        key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0",
                                        token=block.id_
                                    )
                """
    block_type = 'divider'

    def __init__(self, block: dict | str = None, *args, **kwargs):
        self.data: dict[str, Any] = {
            "divider": None,
        }
        super().__init__(*args, **kwargs)
        self.get_info(block)

    def get_info(self, blck_info: dict):
        self.data['divider'] = blck_info['divider']

    def create_info_block(self):
        return {
                  "type": "divider",
                  "divider": {}
                }


BLOCK_CLASS_MAP = {
    # "bookmark": BookmarkBlock,
    # "breadcrumb": BreadcrumbBlock,
    # "bulleted_list_item": BulletedListItemBlock,
    # "callout": CalloutBlock,
    # "child_database": ChildDatabaseBlock,
    # "child_page": ChildPageBlock,
    # "column": ColumnBlock,
    # "column_list": ColumnListBlock,
    "divider": Divider,
    # "embed": EmbedBlock,
    # "equation": EquationBlock,
    # "file": FileBlock,
    # "heading_1": Heading1Block,
    # "heading_2": Heading2Block,
    # "heading_3": Heading3Block,
    # "image": ImageBlock,
    # "link_preview": LinkPreviewBlock,
    # "numbered_list_item": NumberedListItemBlock,
    # "paragraph": ParagraphBlock,
    # "pdf": PdfBlock,
    # "quote": QuoteBlock,
    # "synced_block": SyncedBlock,
    # "table": TableBlock,
    # "table_of_contents": TableOfContentsBlock,
    # "table_row": TableRowBlock,
    # "template": TemplateBlock,
    # "to_do": ToDoBlock,
    # "toggle": ToggleBlock,
    # "unsupported": UnsupportedBlock,
    # "video": VideoBlock,
}


def create_block(block_type_str, block, **kwargs):
    cls = BLOCK_CLASS_MAP.get(block_type_str)
    if cls:
        return cls(**kwargs)
    return None


if __name__ == "__main__":
    block_ = NotionBlock.get(
        key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0",
        token="https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75?source=copy_link#2919b4f7b3cd8084af9febd2696e4973"
    )
