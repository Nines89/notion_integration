from abc import ABC


from notion_types import NDate
from notion_client import (
    NDEL, NGET, NPATCH, NPOST
)

class ObjectError(Exception):
    pass


class NObj(ABC):
    """
    Classe che riguarda l' oggetto vero e proprio.
    Gestisce solo quello che deriva dall' oggetto:
        se deve essere creato, aggiornato, letto o eliminato
    """
    def __init__(self, header: dict):
        self.header = header

    def _get(self, api_url: str):
        return NGET(api_url, self.header)

    def _create(self, api_url: str, data: dict):
        return NPOST(header=self.header, url=api_url, data=data)

    def _update(self, api_url: str, data: dict):
        return NPATCH(header=self.header, url=api_url, data=data)

    def _delete(self, api_url: str):
        return NDEL(header=self.header, url=api_url)

    def get_content(self):
        self.data = self._get(api_url=self.get_url) # noqa
        for a in list(self.__dict__.keys()):
            if a.startswith('_'):
                getattr(self, a[1:])

    def update_content(self, data: dict):
        self.data = self._update(api_url=self.update_url, data=data) # noqa

    def append_contents(self, data: list[dict]):
        self.data = self._update(api_url=self.append_children_url, data=data) # noqa

    def delete_content(self):
        self._delete(api_url=self.delete_url) # noqa

    ## =============================== CHILDREN BLOCK ==================================================================
    def _get_children(self):
        from notion_block import load_block
        self.children_data = []
        children_data = self._get(api_url=self.get_children_url)  # noqa
        for child in children_data.response['results']:
            print("Create block for: ", child['type'])
            self.children_data.append(load_block(self.header, child['id'], child['type']))
            self.children_data[-1].get_content()

    def get_children(self):
        if self.object_type == "block":
            if self.has_children:
                self._get_children()
            else:
                self.children_data = None # noqa
        elif self.object_type == "page":
            self._get_children()

    @property
    def children(self):
        if "children_data" not in self.__dict__.keys():
            self.get_children()
        return self.children_data
    ## =====================================================================================================================

    @property
    def parent(self):
        if not hasattr(self, "data"):
            self.get_content()
        return self.data['parent']['type'], self.data['parent'][self.data['parent']['type']]

    @property
    def object_type(self):
        if not hasattr(self, "data"):
            self.get_content()
        return self.data['object']

    @property
    def _id(self):
        if not hasattr(self, "data"):
            self.get_content()
        return self.data['id']

    @property
    def has_children(self):
        if not hasattr(self, "data"):
            self.get_content()
        return self.data['has_children']

    @property
    def is_archived(self):
        if not hasattr(self, "data"):
            self.get_content()
        return self.data['archived']

    @property
    def in_trash(self):
        if not hasattr(self, "data"):
            self.get_content()
        return self.data['in_trash']

    @property
    def create_info(self):
        from notion_user import load_user
        if not hasattr(self, "data"):
            self.get_content()
        return {'create_time': NDate(self.data['created_time']),
                'create_user': load_user(self.header, self.data['created_by']['id'])}

    @property
    def last_edit_info(self):
        from notion_user import load_user
        if not hasattr(self, "data"):
            self.get_content()
        return {'last_edited_time': NDate(self.data['created_time']),
                'create_user': load_user(self.header, self.data['last_edited_by']['id'])}

    def __repr__(self):
        if not hasattr(self, "data"):
            self.get_content()
        return (f"\n-------- {self.__class__.__name__} properties -------------"
                f"\n{self.data.__repr__()}---------------------\n")

    def __getitem__(self, item):
        return self.data.__getitem__(item)


