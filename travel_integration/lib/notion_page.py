import re
from pprint import pprint

from lib.notion_block import NotionBlockGet
from lib.notion_types import (
    n_file, n_icon,
    NUser, NDate
)

from lib.notion_client import NGET, NotionApiClient


class NotionError(Exception):
    pass


class NotionPageGet(NotionBlockGet):
    page_info = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_url = f"https://api.notion.com/v1/pages/{self.token}"  # noqa
        self.get_page_content()

    def get_page_content(self):
        self.page_info = self.get_page_info()
        if 'page' != self.is_page:
            raise NotionError("Page Class are being used for a not page object")
        # self.page_properties = self.get_page_properties()
        # self.page_children = self.get_page_children()

    def get_page_info(self):
        return NGET(self.api_url, self.headers)

    @property
    def is_page(self):
        return self.page_info['object']

    @property
    def is_archived(self):
        return self.page_info['archived']

    @property
    def is_trash(self):
        return self.page_info['in_trash']

    @property
    def is_locked(self):
        return self.page_info['is_locked']

    @property
    def retrieve_id(self):
        return self.page_info['id']

    @property
    def retrieve_cover(self):
        return n_file(self.page_info['cover'])

    @property
    def creation_info(self):
        return {'user': NUser(self.page_info['created_by'])['id'],
                'create_time': NDate(self.page_info['created_time'])['time']}

    @property
    def last_edit_info(self):
        return {'user': NUser(self.page_info['last_edited_by'])['id'],
                'create_time': NDate(self.page_info['last_edited_time'])['time']}

    @property
    def retrieve_icon(self):
        return n_icon(self.page_info['icon'])

    @property
    def retrieve_url(self):
        return self.page_info['url']

    @property
    def retrieve_pubblic_url(self):
        if not self.page_info['public_url']:
            return 'Page is not pubblished'
        return self.page_info['public_url']

    def retrieve_all_info(self, stamp: bool = False):
        output_dict = {
            'is_page': self.is_page,
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




