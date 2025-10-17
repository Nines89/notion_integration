import re

from notion_types import n_file, NUser
from notion_request import NGET

class NotionWidget:
    def __init__(self, notion):
        self.notion = notion

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
    pattern = re.compile(r"notion\.so/[^/\?]*-([0-9a-f]{32})") # type: ignore
    def __init__(self, page_token: str, *args, **kwargs):
        match = self.pattern.search(page_token)
        if match:
            page_token =  match.group(1)
        page_token = page_token.replace('-', '') # inserito per quanto si recupera la pagina da un database
        if len(page_token) != 32:
            raise ValueError('Page Token Length is Incorrect')
        super().__init__(*args, **kwargs)
        self.api_url = f"https://api.notion.com/v1/pages/{page_token}"
        self.page_info = self.get_page_content()

    def get_page_content(self):
        return NGET(self.api_url, self.headers)

    @property
    def is_archived(self):
        return self.page_info['archived']

    @property
    def is_trash(self):
        return self.page_info['in_trash']

    @property
    def retrieve_cover(self):
        return n_file(self.page_info['cover'])

    @property
    def creation_info(self):
        return {'user': NUser(self.page_info['created_by'])}

page = NotionPage(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0",
                  page_token="https://www.notion.so/Integration-Example-28f9b4f7b3cd80588296e08e56e45b75")

print(page.api_url)
print(page.retrieve_cover)


#TODO
# run debug
# per vedere i vari campi
# from pprint import pprint
# pprint(page.page_info.response)
# siamo arrivati alle creation info a cui dobbiamo aggiungere la data -> NDate
# controlla che NDATE funzioni anche per il file!
