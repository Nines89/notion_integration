from notion_types import Ntype


def n_file(_obj: dict, **kwargs) -> Ntype:
    type_of_object = _obj['type']
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
        return f"ExpiryTime: {self.expiry_time}\nLink: {self.url}"


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
        return f"ID: {self._id}\n"


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
        return self.data['id']

    def __repr__(self):
        return f"Url: {self.url}\n"


if __name__ == "__main__":
    file = n_file({"type": "file"}, url="asd", expiry_time="jpg")
    print(file.to_dict())