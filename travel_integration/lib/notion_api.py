import re

from notion_types import (
    n_file, n_icon,
    NUser, NDate
)
from notion_request import NGET


class NotionError(Exception):
    pass


class NotionApi:
    def __init__(self, key, version: str = "2022-06-28"):
        self.key = key
        self.headers = {
            "Authorization": "Bearer " + self.key,
            "Content-Type": "application/json",
            "Notion-Version": version,
            "accept": "application/json",
        }


class NotionPage(NotionApi):
    pattern = re.compile(r"notion\.so/[^/\?]*-([0-9a-f]{32})")  # noqa

    def __init__(self, page_token: str, *args, **kwargs):
        match = self.pattern.search(page_token)
        if match:
            page_token = match.group(1)
        page_token = page_token.replace('-', '')  # inserito per quanto si recupera la pagina da un database
        if len(page_token) != 32:
            raise ValueError('Page Token Length is Incorrect')
        super().__init__(*args, **kwargs)
        self.api_url = f"https://api.notion.com/v1/pages/{page_token}"  # noqa
        self.page_info = self.get_page_content()
        if 'page' != self.is_page:
            raise NotionError("Page Class are being used for a not page object")

    def get_page_content(self):
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


if __name__ == "__main__":

    page = NotionPage(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0",
                      page_token="https://www.notion.so/Integration-Example-28f9b4f7b3cd80588296e08e56e45b75")

    print(page.retrieve_all_info(True))

    # 'icon': {'type': 'external',
    #          'external': {'url': 'https://www.notion.so/icons/activity_gray.svg'}},


# TODO: passaggi per il test
# run debug
# per vedere i vari campi
# from pprint import pprint
# pprint(page.page_info.response)
# siamo arrivati alle page_properties - da fare da zero

# Parent - fallo in un secondo momento - https://developers.notion.com/reference/parent-object

