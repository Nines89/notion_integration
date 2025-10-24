from abc import ABC, abstractmethod

from notion_types import NDate
from notion_client import (
    NDEL, NGET, NPATCH, NPOST
)

from utils import Color

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

    def _get(self, api_url: str, *args, **kwargs):
        return _NObjGet(self.header, api_url, *args, **kwargs)

    def _create(self, api_url: str, *args, **kwargs):
        return _NObjPost(self.header, api_url, *args, **kwargs)

    def _update(self, api_url: str, *args, **kwargs):
        return _NObjPatch(self.header, api_url, *args, **kwargs)

    def _delete(self, api_url: str, *args, **kwargs):
        return _NObjDel(self.header, api_url, *args, **kwargs)

    def get_content(self):
        self.data = self._get(api_url=self.get_url, headers=self.header) # noqa
        for a in list(self.__dict__.keys()):
            if a.startswith('_'):
                getattr(self, a[1:])

    def update_content(self, data: dict):
        self.data = self._update(api_url=self.update_url, data=data) # noqa

    ## =============================== CHILDREN BLOCK ==================================================================
    def get_children(self):
        if self.has_children:
            self.children_data = self._get(api_url=self.get_children_url, headers=self.header) # noqa
        else:
            self.children_data = None # noqa

    @property
    def children(self):
        if "children_data" not in self.__dict__.keys():
            self.get_children()
        return self.children_data
    ## =====================================================================================================================

    @property
    def object_type(self):
        if self.data is None:
            self.get_content()
        return self.data['object']

    @property
    def object_id(self):
        if self.data is None:
            self.get_content()
        return self.data['id']

    @property
    def has_children(self):
        if self.data is None:
            self.get_content()
        return self.data['has_children']

    @property
    def is_archived(self):
        if self.data is None:
            self.get_content()
        return self.data['archived']

    @property
    def in_trash(self):
        if self.data is None:
            self.get_content()
        return self.data['in_trash']

    @property
    def object_parent(self):
        if self.data is None:
            self.get_content()
        return self.data['parent'] # TODO

    @property
    def object_create_info(self):
        from notion_user import load_user
        if self.data is None:
            self.get_content()
        return {'create_time': NDate(self.data['created_time']),
                'create_user': load_user(self.header, self.data['created_by']['id'])}

    @property
    def object_last_edit_info(self):
        from notion_user import load_user
        if self.data is None:
            self.get_content()
        return {'last_edited_time': NDate(self.data['created_time']),
                'create_user': load_user(self.header, self.data['last_edited_by']['id'])}

    def __repr__(self):
        return self.data.__repr__()

    def __getitem__(self, item):
        return self.data.__getitem__(item)


class _NObjReq(ABC):
    """
    Questa classe è l' astrazione per le classi che implementano le richieste
    """
    data = None

    def __init__(self, header: dict, url: str, *args, **kwargs):
        self.header = header
        self.url = url

    def __getitem__(self, key):
        if self.data:
            if key in self.data:
                return self.data[key]
            raise ObjectError(f"The key {key} does not exist")
        raise ObjectError(f"Please get file info first.")

    def __str__(self):
        out = ""
        for key, item in self.data.items():
            out += f"{key}: {item}\n"
        return out

    def __repr__(self):
        out = ""
        for key, item in self.data.items():
            out += f"{key}: {item}\n"
        return out


class _NObjGet(_NObjReq):
    def __init__(self, header: dict, url: str, *args, **kwargs):
        super().__init__(header, url, *args, **kwargs)
        self.data = self.get_obj().response

    def get_obj(self):
        return NGET(self.url, self.header)


class _NObjPost(_NObjReq):
    def __init__(self, header: dict, url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_obj(self):
        """To Implement"""
        pass


class _NObjPatch(_NObjReq):
    def __init__(self, header: dict, url: str, *args, **kwargs):
        super().__init__(header, url, *args, **kwargs)
        self.data = self.update_obj(*args, **kwargs).response

    def update_obj(self, *args, **kwargs):
        return NPATCH(self.url, self.header, *args, **kwargs)


class _NObjDel(_NObjReq):
    def __init__(self, header: dict, url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def delete_obj(self, *args, **kwargs):
        """To Implement"""
        pass





