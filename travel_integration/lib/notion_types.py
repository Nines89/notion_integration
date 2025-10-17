from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Any


class FileError(Exception):
    pass


class BASECLASSS(ABC):
    data = None

    @abstractmethod
    def get_file_info(self, blck_info: dict):
        pass

    @abstractmethod
    def create_file_info_block(self, *args, **kwargs):
        pass

    def __getitem__(self, key):
        if self.data:
            if key in self.data:
                return self.data[key]
            raise FileError(f"The key {key} does not exist")
        raise FileError(f"Please get file info first.")

    def __str__(self):
        out = ""
        for key, item in self.data.items():
            out += f"{key}: {item}\n"
        return out


class NDate(BASECLASSS):
    def __init__(self, block: dict | str = None):
        self.data: dict[str, str | datetime | None] = {
            "time": None,
        }
        self.get_file_info(block)

    def get_file_info(self, blck_info: dict | str):
        self.data['time'] = datetime.fromisoformat(
            blck_info.
            replace("Z", "+00:00")
        )

    def create_file_info_block(self, date: str):
        return date


class NFileTypeFile(BASECLASSS):
    def __init__(self, block: dict = None):
        self.data : dict[str, datetime | None] = {
            "url": None,
            "expiry_time": None
        }
        self.get_file_info(block)

    def get_file_info(self, blck_info: dict):
        self.data['url'] = blck_info['file']['url']
        self.data['expiry_time'] = NDate(blck_info['file']['expiry_time'])['time']

    def create_file_info_block(self, url: str, expiry_time: str):
        """
        expiry_time: '2025-10-17T09:37:00.000Z'
        """
        return {
            "type": "file",
            "file": {
                "url": url,
                "expiry_time": expiry_time
            }
        }


class NFileTypeUpload(BASECLASSS):
    def __init__(self, block: dict = None):
        self.data: dict[str, datetime | None] = {
            "id": None,
        }
        self.get_file_info(block)


    def get_file_info(self, blck_info: dict):
        self.data['id'] = blck_info['file_upload']['id']

    def create_file_info_block(self, file_id: str):
        return {
              "type": "file_upload",
              "file_upload": {
                "id": file_id
              }
            }


class NFileTypeExternal(BASECLASSS):
    def __init__(self, block: dict = None):
        self.data: dict[str, datetime | None] = {
            "url": None,
        }
        self.get_file_info(block)

    def get_file_info(self, blck_info: dict):
        self.data['url'] = blck_info['external']['url']

    def create_file_info_block(self, url):
        return {
              "type": "external",
              "external": {
                "url": url
              }
            }


def n_file(_obj: dict) -> BASECLASSS:
    type_of_object = _obj['type']
    mapping = {
        "file": NFileTypeFile,
        "file_upload": NFileTypeUpload,
        "external": NFileTypeExternal
    }
    try:
        return mapping[type_of_object](_obj)
    except KeyError:
        raise TypeError("Unknown object type")


class NUser(BASECLASSS):
    def __init__(self, block: dict = None):
        if block['object'] is not 'user':
            raise ValueError("Block object must be 'user', you're using the wrong class")
        self.data: dict[str, datetime | None] = {
            "id": None,
        }
        self.get_file_info(block)

    def get_file_info(self, blck_info: dict):
        self.data['id'] = blck_info['id']

    def create_file_info_block(self, _id: str):
        return {
            "object": "user",
            "id": _id
        }

