import re
from datetime import datetime

from lib.notion_types import NDate
from notion_page_properties import load_prop_item
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
            self.get_property_url = f"https://api.notion.com/v1/pages/{self.page_id}/properties/"  # + f"{property_id}"
            self.trash_url = f"https://api.notion.com/v1/pages/{self.page_id}"  # patch
            self.get_children_url = f"https://api.notion.com/v1/blocks/{self.page_id}/children"
            self.append_children_url = f"https://api.notion.com/v1/blocks/{self.page_id}/children"
            self.body = None
            self._icon = None
            self._cover = None
            self.properties = {}
        else:
            self.create_url = f"https://api.notion.com/v1/pages"
            print('To create a page object an ID have to be given. For the creation is ok!')

    def get_body(self):
        self.get_children()  # noqa
        self.body = self.children_data

    #################### PROPERTIES #############################################################
    def get_property_item(self, prop_id: str, name: str):
        """
        API endpoint to retrieve a property object from id and name
        """
        prop_url_with_id = self.get_property_url + prop_id
        properties = self._get(prop_url_with_id)
        properties.response['name'] = name
        return load_prop_item(properties.response)

    def get_properties(self):
        """
        Save all properties as the correct Python item
        """
        if hasattr(self, 'data'):
            self.get_content()
        for name, obj in self.data.response['properties'].items():
            self.properties[name] = self.get_property_item(prop_id=obj['id'], name=name)

    def read_properties(self, name: str):
        """
        Read an imported page property given the name
        """
        return self.properties[name].to_dict()

    def to_properties_dict(self):
        """
        Return the dictionary {'properties': {[...]}} of the page
        """
        properties = {'properties': {}}
        for prop in self.properties.keys():
            if self.properties[prop].updatable:
                properties['properties'].update(page.properties[prop].to_dict())
        return properties

    ##############################################################################################

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
            if 'type' not in self.data['cover']:
                self.data['cover'].update({'type': list(self.data['cover'].keys())[0]})
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

    def update_page(self):
        """
        update the properties of the page (prop if it exists + cover + icon + )
        """
        element_to_update = self.to_properties_dict()
        if self.cover is not None:
            element_to_update.update({'cover': self.cover.to_dict()})
        if self.icon is not None:
            element_to_update.update({'icon': self.icon.to_dict()})
        return self._update(api_url=self.update_url, data=element_to_update)


if __name__ == "__main__":
    id_ = "https://www.notion.so/dsdada-2a7b7a8f729481ffadcfe600364f3fd4"  # "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75"
    api_ = NotionApiClient(key="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")
    #######################################################################################
    page = NPage(header=api_.headers, page_id=id_)
    page.get_content()
    # page.get_body()
    ############################## Create Page Test #########################################################
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
    ############################## Work with properties Test ####################################################
    page.get_properties()
    properties_ = {'properties': {}}
    for prop_ in page.properties.keys():
        print(page.read_properties(page.properties[prop_]._name))
        if page.properties[prop_].updatable:
            properties_['properties'].update(page.properties[prop_].to_dict())
    print('---------------------------------------------------------')
    from pprint import pprint
    pprint(page.to_properties_dict())
    print('---------------------------------------------------------')
    new_date = datetime(1934, 4, 24, 22, 49, 22)
    page.properties['Date'].startDate = NDate(new_date)
    page.properties['Email'].email = 'paolo@yahoo.it'
    page.properties['Multi-select'].multiselect = 'Quarto'
    page.properties['Name'].title = 'New Title 2: The revenge'
    page.properties['Number'].number = 1
    page.properties['Phone'].number = '3333333365'
    page.properties['Select'].select = 'OptVERO'
    page.properties['Status'].select = 'Done'
    page.properties['Text'].text = "A brand new Rich Text Again"
    page.properties['URL'].url = "itsdone.it"
    page.properties['check'].checkbox = True
    page.properties['relationDB'].clear_page('2a7b7a8f-7294-8026-b530-ffdec4d14324')
    # page.properties['relationDB'].add_page('2a7b7a8f-7294-8026-b530-ffdec4d14324')
    print('---------------------------------------------------------')
    page.update_page()
    ##############################################################################################

