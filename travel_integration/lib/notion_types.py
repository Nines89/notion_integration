
from datetime import datetime
from abc import ABC, abstractmethod


class SchemaError(Exception):
    pass


class Ntype(ABC):
    def __init__(self, data: dict):
        self.data = data

    def to_dict(self):
        return self.data

class NDate(Ntype):
    def __init__(self, data: str | datetime): # noqa
        if isinstance(data, str):
            self.data = datetime.fromisoformat(data.replace("Z", "+00:00"))

    def to_dict(self):
        return self.data.isoformat(timespec="milliseconds").replace("+00:00", "Z")

    def __repr__(self):
        return f"{self.data}"


class NText(Ntype):
    """
    "text": {
    "content": "Some words ",
    "link": null
    },
    """
    @property
    def content(self):
        return self.data['content']

    @property
    def link(self):
        if self.data['link']:
            return self.data['link']['url']
        return None

    def __repr__(self):
        return f"Content: {self.content}\nLink: {self.link}"


class NEquation(Ntype):
    """
        "equation": {
        "expression": "E = mc^2"
      },
    """
    @property
    def equation(self):
        return self.data['equation']['expression']

    def __repr__(self):
        return f"Equation: {self.equation}\n"


class NMention(Ntype):
    #TODO: add mentions type
    @property
    def type(self):
        return self.data['type']

    def __repr__(self):
        return f"Mention is: {self.type}\n"


class NRichText(Ntype):
    """
        {
      "type": "equation",
      "equation": {
        "expression": "E = mc^2"
      },
      "annotations": {
        "bold": false,
        "italic": false,
        "strikethrough": false,
        "underline": false,
        "code": false,
        "color": "default"
      },
      "plain_text": "E = mc^2",
      "href": null
    }
    """
    def __init__(self, data: dict): # noqa
        self.data = {}
        self.basic_schema = {
          "type": "",
          "annotations": {
            "bold": False,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": ""
          },
          "plain_text": "",
          "href": ""
        }
        if isinstance(data, dict):
            for key, item in data.items():
                self.data[key] = item
                if key == 'type':
                    self.basic_schema[item] = {}
                if key == 'text':
                    self.data[key] = NText(item)
                elif key == 'equation':
                    self.data[key] = NEquation(item)
                elif key == 'mention':
                    self.data[key] = NMention(item)
        if self.data.keys() != self.basic_schema.keys():
            raise SchemaError(f"Received Keys are not the expected: {self.basic_schema.keys()}")

    @property
    def type(self):
        return self.data['type']

    @property
    def obj(self):
        return self.data[self.type]

    @property
    def annotations(self):
        return self.data['annotations']

    @property
    def plain_text(self):
        return self.data['plain_text']

    @property
    def href(self):
        return self.data['href']

    def __getitem__(self, item):
        return self.data[item]

    def __repr__(self):
        return f"Plain Text: {self.plain_text}"


class NRichList(list):
    def append(self, item: NRichText):
        if not isinstance(item, NRichText):
            raise ValueError(f"{item} is not a NRichText, but {type(item)}")
        super().append(item)


def rich_list_text(array: NRichList):
    return ''.join([element.plain_text for element in array])


if __name__ == '__main__':
    l = NRichList()
    list_of_rich = [
        {'type': 'text', 'text': {'content': 'Ci mettiamo di sicuro ', 'link': None}, 'annotations': {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}, 'plain_text': 'Ci mettiamo di sicuro ', 'href': None},
        {'type': 'text', 'text': {'content': 'un testo, in parte', 'link': None}, 'annotations': {'bold': True, 'italic': True, 'strikethrough': True, 'underline': True, 'code': False, 'color': 'orange'}, 'plain_text': 'un testo, in parte', 'href': None},
        {'type': 'text', 'text': {'content': ' colorato e con un ', 'link': None}, 'annotations': {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}, 'plain_text': ' colorato e con un ', 'href': None},
        {'type': 'text', 'text': {'content': 'code ', 'link': None}, 'annotations': {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': True, 'color': 'default'}, 'plain_text': 'code ', 'href': None},
        {'type': 'text', 'text': {'content': 'dentro', 'link': None}, 'annotations': {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}, 'plain_text': 'dentro', 'href': None}]
    for el in list_of_rich:
        l.append(NRichText(el))
    print(rich_list_text(l))
    print(l)
    pass
