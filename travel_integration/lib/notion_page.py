import re

from lib.notion_types import simple_rich_text_list
from notion_file import n_file, n_icon
from notion_client import NotionApiClient
from notion_object import (NObj)

class Counter:
    t = 0

    @classmethod
    def incr(cls):
        cls.t += 1
        return cls.t


class NPage(NObj):
    """
    Header contiene sia la versione delle API che il secret token.
    Block_id contiene la stringa con l' id, serve per il patch, il delete e il get

    per recuperare il blocco: block.get_content()
    per aggiornare il blocco: block.update_content(update_data)
    """
    obj_type = "page"
    pattern = re.compile(r"notion\.so/[^/?]*-([0-9a-f]{32})")

    def __init__(self, header: dict, page_id: str = None):
        super().__init__(header=header)
        if page_id:
            match = self.pattern.search(page_id)
            if match:
                page_id = match.group(1)
            self.page_id = page_id.replace('-', '')  # inserito per quanto si recupera la pagina da un database
            if len(self.page_id) != 32:
                raise ValueError('Token Length is Incorrect')
            self.get_url = f"https://api.notion.com/v1/pages/{self.page_id}"
            self.update_url = f"https://api.notion.com/v1/pages/{self.page_id}"
            self.get_property_url = f"https://api.notion.com/v1/pages/{self.page_id}/properties/" # + f"{property_id}"
            self.trash_url = f"https://api.notion.com/v1/pages/{self.page_id}" # patch
            self.get_children_url = f"https://api.notion.com/v1/blocks/{self.page_id}/children"
            self.append_children_url = f"https://api.notion.com/v1/blocks/{self.page_id}/children"
            self.body = None
            self._icon = None
            self._cover = None
        else:
            self.create_url = f"https://api.notion.com/v1/pages"
            print('To create a page object an ID have to be given. For the creation is ok!')

    def get_body(self):
        self.get_children()  # noqa
        self.body = self.children_data

    @property
    def icon(self):
        if not hasattr(self, "data"):
            self.get_content()
        if self.data['icon']:
            self._icon = n_icon(self.data['icon'])
            return self._icon
        return None

    @icon.setter
    def icon(self, value: dict):
        """
        value examples:
        {
          "type": "emoji",
          "emoji": "😻"
        }
        ---------------------
        // File uploaded via the Notion API
        {
          "type": "file_upload",
          "file_upload": {
            "id": "43833259-72ae-404e-8441-b6577f3159b4"
          }
        }

        // External file
        {
          "type": "external",
          "external": {
            "url": "https://example.com/image.png"
          }
        }
        """
        if isinstance(value, dict):
            raise TypeError("Icon object must be a dict, please see documentation!")
        self.data.response['icon'] = value

    @property
    def cover(self):
        if not hasattr(self, "data"):
            self.get_content()
        if self.data['cover']:
            self._cover = n_file(self.data['cover'])
            return self._cover
        return None

    @cover.setter
    def cover(self, value: dict):
        """
        value examples:
        {
          "type": "file",
          "file": {
            "url": "<https://s3.us-west-2.amazonaws.com/...">,
            "expiry_time": "2025-04-24T22:49:22.765Z"
          }
        }

        // File uploaded via the Notion API
        {
          "type": "file_upload",
          "file_upload": {
            "id": "43833259-72ae-404e-8441-b6577f3159b4"
          }
        }

        // External file
        {
          "type": "external",
          "external": {
            "url": "<https://example.com/image.png">
          }
        }
        """
        if isinstance(value, dict):
            raise TypeError("Cover object must be a dict, please see documentation!")
        self.data.response['cover'] = value

    @property
    def public_url(self):
        if not hasattr(self, "data"):
            self.get_content()
        return self.data['public_url']

    def create_page(self,
                    properties: dict,
                    parent_id: str,
                    parent: str,
                    title: str = None,
                    icon: str = None,
                    cover: str = None,
                    ):
        parents_type = ["database_id", "page_id"]
        if hasattr(self, "page_id"):
            raise AttributeError("A Page ID is set, create cannot be called.")
        if parent not in parents_type:
            raise AttributeError(f"Parent must be one of {" ".join(x for x in parents_type)}")
        if parent == "database_id":
            self._create(self.create_url, {
                "parent": {
                    f"{parent}": parent_id,
                },
                "icon": icon,
                "cover": cover,
                "properties": properties})
        else:
            self._create(self.create_url, {
                  "parent": {f"{parent}": parent_id},
                  "icon": icon,
                  "cover": cover,
                  "properties": {
                  "title": [
                      {
                          "type": "text",
                          "text": {"content": title}
                      }
                  ]
                  }
            })



if __name__ == "__main__":
    id_ = "https://www.notion.so/dsdada-29b9b4f7b3cd8046a867e2e5d52c5ad5?source=copy_link" # "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75"
    api_ = NotionApiClient(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0")
    #######################################################################################
    page = NPage(header=api_.headers, page_id=id_)
    page.get_content()
    # page.get_body()
    #######################################################################################
    # in database
    # prop = {"Name": {
    #     "id": "title",
    #     "type": "title",
    #     "title": simple_rich_text_list("bot title").to_dict(),
    # }}
    # paren_id = "2969b4f7b3cd8050a849f1bc4b9684d7"
    # NPage(header=api_.headers).create_page(properties=prop,
    #                                        parent_id=paren_id,
    #                                        parent="database_id",
    #                                        title="bot title",
    #                                        )
    # # in page
    # NPage(header=api_.headers).create_page(properties={},
    #                                        parent_id=paren_id,
    #                                        parent="page_id",
    #                                        title="bot title",
    #                                        )
    #######################################################################################
    pass
    # TODO: properties
    # prop = {"Name": {
    #     "id": "title",
    #     "type": "title",
    #     "title": simple_rich_text_list("bot title").to_dict(),
    # }}