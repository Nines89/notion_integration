import re
from pprint import pprint

from notion_block import NotionBlockGet
from notion_types import (
    n_file, n_icon,
    NUser, NDate
)

from notion_client import NGET, NotionApiClient


class PageError(Exception):
    pass


class NotionPageGet(NotionBlockGet):
    block_type = 'page'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_url = f"https://api.notion.com/v1/pages/{self.token}"  # noqa
        self.get_block_content()

    def get_block_content(self):
        super(NotionPageGet, self).get_block_content()
        if 'page' != self.is_block:
            raise PageError("Page Class are being used for a not page object")
        # self.page_properties = self.get_page_properties()
        # self.page_children = self.get_page_children()

    @property
    def retrieve_cover(self):
        return n_file(self.info['cover'])

    @property
    def retrieve_icon(self):
        return n_icon(self.info['icon'])

    @property
    def retrieve_url(self):
        return self.info['url']

    @property
    def retrieve_pubblic_url(self):
        if not self.info['public_url']:
            return 'Page is not pubblished'
        return self.info['public_url']

    def retrieve_all_info(self, stamp: bool = False):
        output_dict = {
            'is_page': self.is_block,
            'is_archived': self.is_archived,
            'is_trash': self.is_trash,
            'is_locked': self.is_locked,
            'id': self.retrieve_id,
            'icon': self.retrieve_icon,
            'cover': self.retrieve_cover,
            'url': self.retrieve_url,
            'public_url': self.retrieve_pubblic_url,
            'creation_info': self.creation_info,
            'last_edit_info': self.last_edit_info
        }

        if stamp:
            info_str = ''
            for key, item in output_dict.items():
                info_str += f"{key}: {item}\n"
            return info_str

        return output_dict


class NotionPageUpdate:
    pass


class NotionPageCreate:
    pass


class NotionPage:
    @classmethod
    def get(cls, *args, **kwargs):
        return NotionPageGet(*args, **kwargs)




