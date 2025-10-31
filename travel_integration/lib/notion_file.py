from notion_types import Ntype


def n_file(_obj: dict, **kwargs) -> Ntype:
    try:
        type_of_object = _obj['type'] if 'type' in _obj else kwargs['type']
    except KeyError:
        raise KeyError("Type of file must be defined!")
    mapping = {
        "file": NFileTypeFile,
        "file_upload": NFileTypeUpload,
        "external": NFileTypeExternal
    }
    try:
        _obj.pop('type')
        return mapping[type_of_object](_obj, **kwargs)
    except KeyError:
        raise TypeError("Unknown object type")


def n_icon(_obj: dict) -> Ntype:
    type_of_object = _obj['type']
    mapping = {
        "external": n_file,
        "file_upload": n_file,
        "emoji": NEmoji,
    }
    try:
        return mapping[type_of_object](_obj)
    except KeyError:
        raise TypeError("Unknown object type")


class NEmoji(Ntype):
    def __init__(self, _obj: dict, **kwargs) -> None:
        if kwargs:
            if ('url' or 'expiry_time') not in kwargs.keys():
                raise TypeError("You must specify just: 'url' and 'expiry_time'")
            data = {
                'type': 'emoji',
                'emoji': kwargs['emoji']
            }
            super().__init__(data)
        else:
            super().__init__(_obj)

    @property
    def emoji(self):
        return self.data['emoji']

    @emoji.setter
    def emoji(self, value: str):
        self.data['emoji'] = value

    def __repr__(self):
        return f"Emoji: \n\t{self.emoji}\n"


class NFileTypeFile(Ntype):
    def __init__(self, _obj: dict, **kwargs) -> None:
        if kwargs:
            if ('url' or 'expiry_time') not in kwargs.keys():
                raise TypeError("You must specify just: 'url' and 'expiry_time'")
            data = {
                'type': 'file',
                'file': {
                    'url': kwargs['url'],
                    "expiry_time": kwargs['expiry_time']
                }}
            super().__init__(data)
        else:
            super().__init__(_obj)

    @property
    def url(self):
        return self.data['file']['url']

    @property
    def expiry_time(self):
        return self.data['file']['expiry_time']

    def __repr__(self):
        return f"Type: File:\n\tExpiryTime: {self.expiry_time}\n\tLink: {self.url}"


class NFileTypeUpload(Ntype):
    def __init__(self, _obj: dict, **kwargs) -> None:
        if kwargs:
            if 'id' not in kwargs.keys():
                raise TypeError("You must specify just: 'id'")
            data = {
                'type': 'file_upload',
                'file_upload': {
                    'id': kwargs['id'],
                }}
            super().__init__(data)
        else:
            super().__init__(_obj)

    @property
    def _id(self):
        return self.data['id']

    def __repr__(self):
        return f"Type: Upload:\n\tID: {self._id}\n"


class NFileTypeExternal(Ntype):
    def __init__(self, _obj: dict, **kwargs) -> None:
        if kwargs:
            if 'url' not in kwargs.keys():
                raise TypeError("You must specify just: 'url'")
            data = {
                'type': 'external',
                'external': {
                    'url': kwargs['url'],
                }}
            super().__init__(data)
        else:
            super().__init__(_obj)

    @property
    def url(self):
        return self.data['external']['url']

    def __repr__(self):
        return f"Type: External:\n\tUrl: {self.url}\n"


if __name__ == "__main__":
    file = n_file({"type": "file"}, url="asd", expiry_time="jpg")
    print(file.to_dict())