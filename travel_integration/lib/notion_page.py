import re

from notion_block import load_block
from notion_client import NotionApiClient
from notion_object import (NObj)


class NPage(NObj):
    """
    Header contiene sia la versione delle API che il secret token.
    Block_id contiene la stringa con l' id, serve per il patch, il delete e il get

    per recuperare il blocco: block.get_content()
    per aggiornare il blocco: block.update_content(update_data)
    """
    obj_type = "page"
    pattern = re.compile(r"notion\.so/[^/?]*-([0-9a-f]{32})")

    def __init__(self, header: dict, page_id: str):
        super().__init__(header=header)
        match = self.pattern.search(page_id)
        if match:
            page_id = match.group(1)
        self.page_id = page_id.replace('-', '')  # inserito per quanto si recupera la pagina da un database
        if len(self.page_id) != 32:
            raise ValueError('Token Length is Incorrect')
        self.get_url = f"https://api.notion.com/v1/pages/{self.page_id}"
        self.update_url = f"https://api.notion.com/v1/pages/{page_id}"
        self.get_property_url = f"https://api.notion.com/v1/pages/{page_id}/properties/" # + f"{property_id}"
        self.trash_url = f"https://api.notion.com/v1/pages/{page_id}" # patch
        self.get_children_url = f"https://api.notion.com/v1/blocks/{self.page_id}/children"
        self.append_children_url = f"https://api.notion.com/v1/blocks/{self.page_id}/children"
        self.create_url = f"https://api.notion.com/v1/pages"
        self.body = self.get_content()

    def get_content(self):
        super().get_content()
        children = []
        children_data = self._get(api_url=self.get_children_url, headers=self.header)  # noqa
        for child in children_data.data['results']:
            children.append(load_block(self.header, child['id']))
        for child in children:
            child.get_content()
        return children


if __name__ == "__main__":
    id_ = "https://www.notion.so/dsdada-29b9b4f7b3cd8046a867e2e5d52c5ad5?source=copy_link"
    api_ = NotionApiClient(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0")

    page = NPage(header=api_.headers, page_id=id_)
    pass