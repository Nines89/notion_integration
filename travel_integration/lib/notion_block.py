import re

from utils import Color, Language
from notion_object import NObj, ObjectError
from notion_client import NotionApiClient
from notion_types import (
    NRichList, NRichText, Ntype, NText, NIcon
)
from notion_file import n_file

class LanguageCodeError(Exception):
    pass


def load_block(header: dict, block_id: str, block_tipe: str = None):
    BLOCK_TYPES = {
        "paragraph": NParagraph,
        "divider": NDivider,
        "bulleted_list_item": NBulletListItem,
        "bookmark": NBookmark,
        "breadcrumb": NBreadcrumb,
        "callout": NCallout,
        "child_database": NChildDatabase,
        "child_page": NChildPage,
        "code": NCode,
        "column_list": NColumnList,
        "column": NColumn,
        "embed": NEmbed,
        "equation": NEquation,
        "file": NFile,
        "external": NFile,
        "file_upload": NFile,
        "heading_1": NHeading1,
        "heading_2": NHeading2,
        "heading_3": NHeading3,
        "image": NImage,
        "numbered_list_item": NNumberedListItem,
        "pdf": NPdf,
        "quote": NQuote,
        "synced_block": NSyncedBlock,
        "table": NTable,
        "table_row": NTableRow,
        "table_of_contents": NTableOfContent,
        "to_do": NToDo,
        "toggle": NToggle,
        # aggiungi altri tipi se servono
    }
    if not block_tipe:
        block = NBlock(header, block_id)
        block.get_content()
        bl = block.block_type
    else:
        bl = block_tipe
    cls = BLOCK_TYPES.get(bl)
    if cls:
        return cls(header, block_id)
    raise TypeError(f"Unsupported block type: {bl}")


class NBlock(NObj):
    """
    Header contiene sia la versione delle API che il secret token.
    Block_id contiene la stringa con l' id, serve per il patch, il delete e il get

    per recuperare il blocco: block.get_content()
    per aggiornare il blocco: block.update_content(update_data)
    """
    _rich_text: NRichList
    obj_type = "block"
    pattern = re.compile(r"([0-9a-f]{32})\Z")

    def __init__(self, header: dict, block_id: str):
        super().__init__(header=header)
        match = self.pattern.search(block_id)
        if match:
            block_id = match.group(1)
        self.block_id = block_id.replace('-', '')  # inserito per quanto si recupera la pagina da un database
        if len(self.block_id) != 32:
            raise ValueError('Token Length is Incorrect')
        self.get_url = f"https://api.notion.com/v1/blocks/{self.block_id}"
        self.update_url = f"https://api.notion.com/v1/blocks/{self.block_id}"
        self.get_children_url = f"https://api.notion.com/v1/blocks/{self.block_id}/children"
        self.append_children_url = f"https://api.notion.com/v1/blocks/{self.block_id}/children"
        self.delete_url = f"https://api.notion.com/v1/blocks/{self.block_id}"

    @property
    def block_type(self):
        if not self.data:
            self.get_content()
        return self.data['type']

    def update_block(self):
        self.update_content(self._get_spec_dict())

    def append_children(self, blocks: list):
        new_list = []
        for block in blocks:
            new_list.append(block._get_spec_dict())
        self.append_contents(new_list)

    def delete_block(self):
        self.delete_content()

    def _get_spec_dict(self) -> dict:
        return {}

    ## =============================== RICH TEXT BLOCK ================================================================
    def _get_rich_text(self):
        if "data" not in self.__dict__.keys():
            self.get_content()
        rich_text = NRichList()
        for rich in self.data[self.block_type]['rich_text']:
            rich_text.append(NRichText(rich))
        self._rich_text = rich_text

    @staticmethod
    def _create_rich_obj(types: str = None,
                         obj: Ntype = None,
                         annotation: dict = None,
                         plain_text: str = None,
                         href: str = None,
                         full_data: dict = None):
        if full_data:
            return NRichText(full_data)
        data = {
            'type': types,
            types: obj.to_dict(),
            'annotations': annotation,
            'plain_text': plain_text,
            'href': href,
        }
        return NRichText(data)

    @property
    def rich_text(self):
        if not self._rich_text:
            self._get_rich_text()
        return self._rich_text


    @rich_text.setter
    def rich_text(self,
                  value: NRichList | dict
                  ):
        """
        dict param:
          types: str,
          object: Ntype,
          annotation: str = None,
          plain_text: str = None,
          href: str = None
        """
        if isinstance(value, NRichList):
            self._rich_text = value
        else:
            if not self._rich_text:
                self._rich_text = NRichList()
            self._rich_text.append(self._create_rich_obj(**value))

    @property
    def text(self):
        if not self._rich_text:
            self._get_rich_text()
        return self._rich_text.text

    def _get_rich_text_dict(self, att: NRichList = None):
        if att is None:
            att = self._rich_text
        return att.to_dict()
        # rt = []
        # try:
        #     for r in att:
        #         rd = r.to_dict()
        #         for j, item in rd.items():
        #             if isinstance(item, Ntype):
        #                 rd[j] = item.to_dict()
        #         if rd['annotations'] is None:
        #             rd['annotations'] = {
        #                     "bold": False,
        #                     "italic": False,
        #                     "strikethrough": False,
        #                     "underline": False,
        #                     "code": False,
        #                     "color": "default"
        #                   }
        #         rt.append(rd)
        # except TypeError as e:
        #     raise  TypeError(f"Error: {e}, rich could be empty, try to call self.get_rich_text or use rich_text setter!")
        # return rt
    ## =================================================================================================================


"""
Blocchi specifici:
    - inizializziamo gli attributi specifici per l' oggetto
            self._attr = None
    - getter e setter per ogni attributo
    - get_content() andrà anche a riempire tutti i valori correnti
    - _get_spec_dict(self) -> dizionario con tutti i parametri che andranno riempiti come si può!
    prova il blocco:
        _id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75?source=copy_link#2999b4f7b3cd806daf4bf09f78a83a04"
        api = NotionApiClient(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0")
        # block = NBlock(header=api.headers, block_id=_id)
        block = load_block(header=api.headers, block_id=_id)
        block.get_content()
        print('------------------ CLASS NAME ---------------------------')
        print(block.__class__.__name__)
        print('------------------ BLOCK - DATA ---------------------------')
        print(block.data)
        print('------------------ GET - DICT ----------------------------')
        from pprint import pprint
        pprint(block._get_spec_dict())
        print('----------------------------------------------')
"""


class NBookmark(NBlock):
    block_type = "bookmark"

    def __init__(self, header: dict, block_id: str):
        """
        self._caption -> list of richeText Objects
        self._url -> url string
        """
        super().__init__(header, block_id)
        self._caption = None
        self._url = None

    @property
    def caption(self):
        if not hasattr(self, "data"):
            self.get_content()
        rich_list = NRichList()
        for rich in self.data[self.block_type]['caption']:
            rich_list.append(NRichText(rich))
        self._caption = rich_list
        return self._caption

    @caption.setter
    def caption(self, value: NRichList):
        self._caption = value

    @property
    def url(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._url = self.data[self.block_type]['url']
        return self._url

    @url.setter
    def url(self, value: str):
        self._url = value

    def _get_spec_dict(self):
        par_dict = {
                "caption": self._get_rich_text_dict(att=self._caption),
                "url": self._url,
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': 'bookmark',
            'bookmark': par_dict
        }


class NBreadcrumb(NBlock):
    block_type = "breadcrumb"
    def _get_spec_dict(self): # noqa
        return {
            'type': 'breadcrumb',
            'breadcrumb': {}
        }


class NCallout(NBlock):
    block_type = "callout"

    def __init__(self, header: dict, block_id: str):
        """
        self._rich_text -> list of richeText Objects
        self._icon -> callout icon -> NIcon(Ntype)
        self._color -> callout color -> Color
        """
        super().__init__(header, block_id)
        self._icon = None
        self._color = None
        self._rich_text = None

    @property
    def icon(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._icon = NIcon(self.data[self.block_type]['icon'])
        return self._icon

    @icon.setter
    def icon(self, value: NIcon):
        self._icon = value

    @property
    def color(self):
        if not hasattr(self, "data"):
            self.get_content()
        if self.data[self.block_type]['color'] not in Color:
            raise ObjectError("The color of the paragraph is not allowed.")
        self._color = self.data[self.block_type]['color']
        return self._color

    @color.setter
    def color(self, value: Color | str):
        if not isinstance(value, Color):
            if value in Color:
                self._color = value
        else:
            self._color = value.value()

    def _get_spec_dict(self):
        par_dict = {
                "rich_text": self._get_rich_text_dict(),
                "icon": self._icon.to_dict(),
                "color": self._color,
            }
        return {
            'type': 'callout',
            'callout': par_dict
        }


class NCode(NBlock):
    block_type = "code"

    def __init__(self, header: dict, block_id: str):
        """
        self._caption -> list of richeText Objects
        self._rich_text -> rich_text object
        self._language -> language string
        """
        super().__init__(header, block_id)
        self._caption = None
        self._rich_text = None
        self._language = None

    @property
    def caption(self):
        if not hasattr(self, "data"):
            self.get_content()
        rich_list = NRichList()
        for rich in self.data[self.block_type]['caption']:
            rich_list.append(NRichText(rich))
        self._caption = rich_list
        return self._caption

    @caption.setter
    def caption(self, value: NRichList):
        self._caption = value

    @property
    def language(self):
        if not hasattr(self, "data"):
            self.get_content()
        if self.data[self.block_type]['language'] in Language._value2member_map_:
            self._language = self.data[self.block_type]['language']
            return self._language
        raise LanguageCodeError(f"Language Code {self.data[self.block_type]['language']} not supported.")

    @language.setter
    def language(self, value: str):
        if value not in Language._value2member_map_:
            raise LanguageCodeError(f"Language Code {self.data[self.block_type]['language']} not supported.")
        self._language = value

    def _get_spec_dict(self):
        par_dict = {
                "caption": self._get_rich_text_dict(att=self._caption),
                "rich_text": self._get_rich_text_dict(),
                "language": self._language,
            }

        return {
            'type': 'code',
            'code': par_dict
        }


class NColumn(NBlock):
    block_type = "column"

    def __init__(self, header: dict, block_id: str):
        """
        self._width_ratio -> column section
        """
        super().__init__(header, block_id)
        self._width_ratio = None

    @property
    def width_ratio(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._width_ratio = self.data[self.block_type]['width_ratio']
        return self._width_ratio

    @width_ratio.setter
    def width_ratio(self, value: float):
        self._width_ratio = value

    def _get_spec_dict(self):
        par_dict = {
                "width_ratio": self._width_ratio
        }
        return {
            'type': 'column',
            'column': par_dict
        }


class NColumnList(NBlock):
    block_type = "column_list"
    def _get_spec_dict(self): # noqa
        return {
            'type': 'column_list',
            'column_list': {}
        }


class NDivider(NBlock):
    block_type = "divider"
    def _get_spec_dict(self): # noqa
        return {
            'type': 'divider',
            'divider': {}
        }


class NEmbed(NBlock):
    block_type = "embed"

    def __init__(self, header: dict, block_id: str):
        """
        self._url -> url string
        """
        super().__init__(header, block_id)
        self._url = None

    @property
    def url(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._url = self.data[self.block_type]['url']
        return self._url

    @url.setter
    def url(self, value: str):
        self._url = value

    def _get_spec_dict(self):
        par_dict = {
                "url": self._url,
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': 'embed',
            'embed': par_dict
        }


class NEquation(NBlock):
    block_type = "equation"

    def __init__(self, header: dict, block_id: str):
        """
        self._expression -> equation expression
        """
        super().__init__(header, block_id)
        self._expression = None

    @property
    def expression(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._expression = self.data[self.block_type]['expression']
        return self._expression

    @expression.setter
    def expression(self, value: str):
        self._expression = value

    def _get_spec_dict(self):
        par_dict = {
                "expression": self._expression
        }
        return {
            'type': 'equation',
            'equation': par_dict
        }


class NFile(NBlock):
    block_type = "file"

    def __init__(self, header: dict, block_id: str):
        """
        self._caption -> list of richeText Objects
        self._type -> url string
        self._object -> type of file
        self._name -> name of file
        """
        super().__init__(header, block_id)
        self._caption = None
        self._name = None
        self._file_object = None

    @property
    def caption(self):
        if not hasattr(self, "data"):
            self.get_content()
        rich_list = NRichList()
        for rich in self.data[self.block_type]['caption']:
            rich_list.append(NRichText(rich))
        self._caption = rich_list
        return self._caption

    @caption.setter
    def caption(self, value: NRichList):
        self._caption = value

    @property
    def name(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._name = self.data[self.block_type]['name']
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def file_object(self):
        if not hasattr(self, "data"):
            self.get_content()
        self.block_type = self.data['type']
        type_dict = dict(self.data['file'][self.block_type])
        type_dict.update({'type': self.block_type})
        self._file_object = n_file(type_dict)
        return self._file_object

    @file_object.setter
    def file_object(self, value: dict):
        self._file_object = value

    def _get_spec_dict(self):
        par_dict = {
                "caption": self._get_rich_text_dict(att=self._caption),
                "name": self._name,
                "type": self.block_type,
                f'{self.block_type}': self._file_object.to_dict(),
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': 'file',
            'file': par_dict
        }


class NHeading1(NBlock):
    block_type = "heading_1"

    def __init__(self, header: dict, block_id: str):
        """
        self._rich_text -> list of richeText Objects
        self._color -> paragraph base color
        self._is_toggleable -> if true it has children
        """
        super().__init__(header, block_id)
        self._rich_text = None
        self._is_toggleable = None
        self._color = None


    @property
    def is_toggleable(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._is_toggleable = bool(self.data[self.block_type]['is_toggleable'])
        return self._is_toggleable

    @is_toggleable.setter
    def is_toggleable(self, value: bool):
        self._is_toggleable = value


    @property
    def color(self):
        if not hasattr(self, "data"):
            self.get_content()
        if self.data[self.block_type]['color'] not in Color:
            raise ObjectError("The color of the paragraph is not allowed.")
        self._color = self.data[self.block_type]['color']
        return self._color

    @color.setter
    def color(self, value: Color | str):
        if not isinstance(value, Color):
            if value in Color:
                self._color = value
        else:
            self._color = value.value()

    def _get_spec_dict(self):
        par_dict = {
                "rich_text": self._get_rich_text_dict(),
                "color": self._color,
                "is_toggleable": self.is_toggleable,
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': f'{self.block_type}',
            f'{self.block_type}' : par_dict
        }


class NHeading2(NBlock):
    block_type = "heading_2"

    def __init__(self, header: dict, block_id: str):
        """
        self._rich_text -> list of richeText Objects
        self._color -> paragraph base color
        self._is_toggleable -> if true it has children
        """
        super().__init__(header, block_id)
        self._rich_text = None
        self._is_toggleable = None
        self._color = None


    @property
    def is_toggleable(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._is_toggleable = bool(self.data[self.block_type]['is_toggleable'])
        return self._is_toggleable

    @is_toggleable.setter
    def is_toggleable(self, value: bool):
        self._is_toggleable = value


    @property
    def color(self):
        if not hasattr(self, "data"):
            self.get_content()
        if self.data[self.block_type]['color'] not in Color:
            raise ObjectError("The color of the paragraph is not allowed.")
        self._color = self.data[self.block_type]['color']
        return self._color

    @color.setter
    def color(self, value: Color | str):
        if not isinstance(value, Color):
            if value in Color:
                self._color = value
        else:
            self._color = value.value()

    def _get_spec_dict(self):
        par_dict = {
                "rich_text": self._get_rich_text_dict(),
                "color": self._color,
                "is_toggleable": self.is_toggleable,
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': f'{self.block_type}',
            f'{self.block_type}' : par_dict
        }


class NHeading3(NBlock):
    block_type = "heading_3"

    def __init__(self, header: dict, block_id: str):
        """
        self._rich_text -> list of richeText Objects
        self._color -> paragraph base color
        self._is_toggleable -> if true it has children
        """
        super().__init__(header, block_id)
        self._rich_text = None
        self._is_toggleable = None
        self._color = None


    @property
    def is_toggleable(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._is_toggleable = bool(self.data[self.block_type]['is_toggleable'])
        return self._is_toggleable

    @is_toggleable.setter
    def is_toggleable(self, value: bool):
        self._is_toggleable = value


    @property
    def color(self):
        if not hasattr(self, "data"):
            self.get_content()
        if self.data[self.block_type]['color'] not in Color:
            raise ObjectError("The color of the paragraph is not allowed.")
        self._color = self.data[self.block_type]['color']
        return self._color

    @color.setter
    def color(self, value: Color | str):
        if not isinstance(value, Color):
            if value in Color:
                self._color = value
        else:
            self._color = value.value()

    def _get_spec_dict(self):
        par_dict = {
                "rich_text": self._get_rich_text_dict(),
                "color": self._color,
                "is_toggleable": self.is_toggleable,
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': f'{self.block_type}',
            f'{self.block_type}' : par_dict
        }


class NImage(NBlock):
    block_type = "image"

    def __init__(self, header: dict, block_id: str):
        """
        self._caption -> list of richeText Objects
        self._type -> url string
        self._object -> type of file
        self._name -> name of file
        """
        super().__init__(header, block_id)
        self._file_object = None
        self._caption = None

    @property
    def caption(self):
        if not hasattr(self, "data"):
            self.get_content()
        rich_list = NRichList()
        for rich in self.data[self.block_type]['caption']:
            rich_list.append(NRichText(rich))
        self._caption = rich_list
        return self._caption

    @caption.setter
    def caption(self, value: NRichList):
        self._caption = value

    @property
    def file_object(self):
        if not hasattr(self, "data"):
            self.get_content()
        type_dict = dict(self.data[self.block_type][self.data[self.block_type]['type']])
        type_dict.update({'type': self.data[self.block_type]['type']})
        self._file_object = n_file(type_dict)
        return self._file_object

    @file_object.setter
    def file_object(self, value: dict):
        self._file_object = value

    def _get_spec_dict(self):
        par_dict = {
                "caption": self._get_rich_text_dict(att=self._caption),
                "type": self.data[self.block_type]['type'],
                f'{self.data[self.block_type]['type']}': self._file_object.to_dict(),
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': 'image',
            'image': par_dict
        }


class NSyncedBlock(NBlock):
    block_type = "synced_block"

    def __init__(self, header: dict, block_id: str):
        super().__init__(header, block_id)
        self._synced_from = None
        self._sync_parent_id = None

    @property
    def synced_from(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._synced_from = self.data[self.block_type]['synced_from']
        return self._synced_from

    @synced_from.setter
    def synced_from(self, value: str):
        self._synced_from = {
            "block_id": value
        }

    @property
    def sync_parent_id(self):
        if not hasattr(self, "data"):
            self.get_content()
        if not self.synced_from:
            return None
        return self.data[self.block_type]['synced_from']['block_id']

    def _get_spec_dict(self):
        par_dict = {
            "synced_from": self.synced_from,
        }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': 'synced_block',
            'synced_block': par_dict
        }


class NPdf(NBlock):
    block_type = "pdf"

    def __init__(self, header: dict, block_id: str):
        """
        self._caption -> list of richeText Objects
        self._type -> url string
        self._object -> type of loaded pdf
        """
        super().__init__(header, block_id)
        self._caption = None
        self._file_object = None

    @property
    def caption(self):
        if not hasattr(self, "data"):
            self.get_content()
        rich_list = NRichList()
        for rich in self.data[self.block_type]['caption']:
            rich_list.append(NRichText(rich))
        self._caption = rich_list
        return self._caption

    @caption.setter
    def caption(self, value: NRichList):
        self._caption = value

    @property
    def file_object(self):
        if not hasattr(self, "data"):
            self.get_content()
        self.block_type = self.data['type']
        type_dict = dict(self.data['file'][self.block_type])
        type_dict.update({'type': self.block_type})
        self._file_object = n_file(type_dict)
        return self._file_object

    @file_object.setter
    def file_object(self, value: dict):
        self._file_object = value

    def _get_spec_dict(self):
        par_dict = {
                "caption": self._get_rich_text_dict(att=self._caption),
                "type": self.block_type,
                f'{self.block_type}': self._file_object.to_dict(),
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': 'pdf',
            'pdf': par_dict
        }


class NTableOfContent(NBlock):
    block_type = "table_of_contents"

    def __init__(self, header: dict, block_id: str):
        """
        self._color -> paragraph base color
        """
        super().__init__(header, block_id)
        self._color = None

    @property
    def color(self):
        if not hasattr(self, "data"):
            self.get_content()
        if self.data[self.block_type]['color'] not in Color:
            raise ObjectError("The color of the paragraph is not allowed.")
        self._color = self.data[self.block_type]['color']
        return self._color

    @color.setter
    def color(self, value: Color | str):
        if not isinstance(value, Color):
            if value in Color:
                self._color = value
        else:
            self._color = value.value()

    def _get_spec_dict(self):
        par_dict = {
                "color": self._color,
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': f'{self.block_type}',
            f'{self.block_type}' : par_dict
        }


class NChildDatabase(NBlock):
    block_type = "child_database"

    def __init__(self, header: dict, block_id: str):
        """
        self._title -> database title
        """
        super().__init__(header, block_id)
        self._title = None

    @property
    def title(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._title = self.data[self.block_type]['title']
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    def _get_spec_dict(self):
        par_dict = {
                "title": self._title
        }
        return {
            'type': 'child_database',
            'child_database': par_dict
        }


class NChildPage(NBlock):
    block_type = "child_page"

    def __init__(self, header: dict, block_id: str):
        """
        self._title -> database title
        """
        super().__init__(header, block_id)
        self._title = None

    @property
    def title(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._title = self.data[self.block_type]['title']
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    def _get_spec_dict(self):
        par_dict = {
                "title": self._title
        }
        return {
            'type': 'child_page',
            'child_page': par_dict
        }


class NParagraph(NBlock):
    """
    NParagraph Retrieving Example:
    >>> api = NotionApiClient(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0")
    >>> contentId = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75?source=copy_link#28f9b4f7b3cd8056a2bcd75e2eec5387"
    >>> updateId = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75?source=copy_link#2929b4f7b3cd80679a55f7d8a15cfeca"
    >>> parag = load_block(api.headers, contentId)
    >>> parag.get_content()
    >>> parag._get_rich_text()
    >>> parag.text
    'Ci mettiamo di sicuro un testo, in parte colorato e con un code dentro'
    >>> parag.rich_text
    [Plain Text: Ci mettiamo di sicuro , Plain Text: un testo, in parte, Plain Text:  colorato e con un , Plain Text: code , Plain Text: dentro]
    >>> for t in parag.rich_text:
    ...    print(t.annotations)
    ...
    {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}
    {'bold': True, 'italic': True, 'strikethrough': True, 'underline': True, 'code': False, 'color': 'orange'}
    {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}
    {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': True, 'color': 'default'}
    {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}

    NParagraph Updating Example:
    >>> te = 'text'
    >>> ob = NText({
            "content": "Some words ",
            "link": None
            })
    >>> pt = "This is a plain text"
    >>> _id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75?source=copy_link#2939b4f7b3cd80c7917ec9d71c5039eb"
    >>> api = NotionApiClient(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0")
    >>> parag = NParagraph(header=api.headers, block_id=_id)
    >>> parag.get_content()
        To add text and format to a paragraph
    >>> parag._get_rich_text()
    >>> parag.rich_text = {'types': te, 'obj': ob, 'plain_text': 'Some words '}
    >>> parag.update_content(parag._get_spec_dict())
        To substitute the text of a paragraph
    >>> parag.rich_text = {'types': te, 'obj': ob, 'plain_text': 'Some words '}
    >>> parag.update_content(parag._get_spec_dict())
    """
    block_type = "paragraph"

    def __init__(self, header: dict, block_id: str):
        """
        self._rich_text -> list of richeText Objects
        self._color -> paragraph base color
        """
        super().__init__(header, block_id)
        self._rich_text = None
        self._color = None

    @property
    def color(self):
        if not hasattr(self, "data"):
            self.get_content()
        if self.data[self.block_type]['color'] not in Color:
            raise ObjectError("The color of the paragraph is not allowed.")
        self._color = self.data[self.block_type]['color']
        return self._color

    @color.setter
    def color(self, value: Color | str):
        if not isinstance(value, Color):
            if value in Color:
                self._color = value
        else:
            self._color = value.value()

    def _get_spec_dict(self):
        par_dict = {
                "rich_text": self._get_rich_text_dict(),
                "color": self._color,
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': 'paragraph',
            'paragraph': par_dict
        }


class NToggle(NBlock):
    block_type = "toggle"

    def __init__(self, header: dict, block_id: str):
        """
        self._rich_text -> list of richeText Objects
        self._color -> paragraph base color
        """
        super().__init__(header, block_id)
        self._rich_text = None
        self._color = None

    @property
    def color(self):
        if not hasattr(self, "data"):
            self.get_content()
        if self.data[self.block_type]['color'] not in Color:
            raise ObjectError("The color of the paragraph is not allowed.")
        self._color = self.data[self.block_type]['color']
        return self._color

    @color.setter
    def color(self, value: Color | str):
        if not isinstance(value, Color):
            if value in Color:
                self._color = value
        else:
            self._color = value.value()

    def _get_spec_dict(self):
        par_dict = {
                "rich_text": self._get_rich_text_dict(),
                "color": self._color,
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': 'toggle',
            'toggle': par_dict
        }


class NToDo(NBlock):
    block_type = "to_do"

    def __init__(self, header: dict, block_id: str):
        """
        self._rich_text -> list of richeText Objects
        self._color -> paragraph base color
        self._checked -> if to-do is checked or not
        """
        super().__init__(header, block_id)
        self._rich_text = None
        self._color = None
        self._checked = False

    @property
    def checked(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._checked = self.data[self.block_type]['checked']
        return self._checked

    @checked.setter
    def checked(self, checked: bool):
        self._checked = checked

    @property
    def color(self):
        if not hasattr(self, "data"):
            self.get_content()
        if self.data[self.block_type]['color'] not in Color:
            raise ObjectError("The color of the paragraph is not allowed.")
        self._color = self.data[self.block_type]['color']
        return self._color

    @color.setter
    def color(self, value: Color | str):
        if not isinstance(value, Color):
            if value in Color:
                self._color = value
        else:
            self._color = value.value()

    def _get_spec_dict(self):
        par_dict = {
                "rich_text": self._get_rich_text_dict(),
                "color": self._color,
                "checked": self._checked,
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': 'to_do',
            'to_do': par_dict
        }


class NQuote(NParagraph):
    block_type = "quote"

    def _get_spec_dict(self):
        par_dict = {
                "rich_text": self._get_rich_text_dict(),
                "color": self._color,
            }
        if self.children:
            par_dict['children'] = self.children
        return {
            'type': 'quote',
            'quote': par_dict
        }


class NBulletListItem(NParagraph):
    block_type = "bulleted_list_item"

    def _get_spec_dict(self):
        bl_dict = {
                "rich_text": self._get_rich_text_dict(),
                "color": self._color,
            }
        if self.children:
            bl_dict['children'] = self.children
        return {
            'type': 'bulleted_list_item',
            'bulleted_list_item': bl_dict
        }


class NNumberedListItem(NParagraph):
    block_type = "numbered_list_item"

    def _get_spec_dict(self):
        bl_dict = {
                "rich_text": self._get_rich_text_dict(),
                "color": self._color,
            }
        if self.children:
            bl_dict['children'] = self.children
        return {
            'type': 'numbered_list_item',
            'numbered_list_item': bl_dict
        }


class NTable(NBlock):
    block_type = "table"

    def __init__(self, header: dict, block_id: str):
        """
        self._rich_text -> list of richeText Objects
        self._color -> paragraph base color
        Special table example
            --------------------------------------------------------------------------------------
            _id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75?source=copy_link#2999b4f7b3cd8093a664f26f6cd38deb"
            api = NotionApiClient(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0")
            # block = NBlock(header=api.headers, block_id=_id)
            block = load_block(header=api.headers, block_id=_id)
            block.get_content()
            print('------------------ CLASS NAME ---------------------------')
            print(block.__class__.__name__)
            print('------------------ BLOCK - DATA ---------------------------')
            print(block.data)
            print('------------------ GET - DICT ----------------------------')
            print('rows: ', block.get_row_plain_text())
            block.update_cells([['10,10', '10,20', '10,30'], ['20,10', '20,20', '20,30'], ['30,10', '30,20', '30,30']])
            print('rows: ', block.get_row_plain_text())
            ----------------------------------------------------------------------------------------
        """
        super().__init__(header, block_id)
        self._table_width = None
        self._has_column_header = None
        self._has_row_header = None

    @property
    def table_width(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._table_width = self.data[self.block_type]['table_width']
        return self._table_width

    @table_width.setter
    def table_width(self, value: int):
        self._table_width = value

    @property
    def has_column_header(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._has_column_header = self.data[self.block_type]['has_column_header']
        return self._has_column_header

    @has_column_header.setter
    def has_column_header(self, value: bool):
        self._has_column_header = value

    @property
    def has_row_header (self):
        if not hasattr(self, "data"):
            self.get_content()
        self._has_row_header = self.data[self.block_type]['has_row_header']
        return self._has_row_header

    @has_row_header .setter
    def has_row_header (self, value: bool):
        self._has_row_header = value

    def get_row_plain_text(self):
        rows = []
        for child in self.children:
            row = []
            for val in child['table_row']['cells']:
                rich_list = NRichList()
                for obj in val:
                    rich_list.append(NRichText(obj))
                row.append(rich_list.text)
            rows.append(row)
        return rows

    def update_cells(self, data: list[list]):
        """
        data:
            [
                [1, 2, 3]
                [4, 5, 6]
            ] -> 2 rows - 3 columns
        """
        n_col = len(data[0])
        for d in data:
            if len(d) != n_col:
                raise ValueError("Check the number of columns in all data")
        if n_col != self.table_width:
            raise ValueError("Check the number of columns in all data")
        # per ogni riga
        for idx, new_data in enumerate(data):
            """
            (self.children[0].data['table_row']['cells'] -> lista di child
            child è una lista: [{'type': 'text', 
                                'text': {'content': '1,1', 'link': None}, 
                                'annotations': {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False, 'code': False, 'color': 'default'}, 
                                'plain_text': '1,1', 
                                'href': None}]
            new_data è una lista: [1, 2, 3]
            table cell can contains just test
            """
            self.children[idx].cells = new_data

    def _get_spec_dict(self):
        bl_dict = {
                "has_row_header": self._has_row_header,
                "has_column_header": self._has_column_header,
            }
        return {
            'type': 'table',
            'table': bl_dict
        }


class NTableRow(NBlock):
    block_type = "table_row"

    def __init__(self, header: dict, block_id: str):
        """
        self._rich_text -> list of richeText Objects
        self._color -> paragraph base color
        """
        super().__init__(header, block_id)
        self._cells = None

    @property
    def cells(self):
        if not hasattr(self, "data"):
            self.get_content()
        self._cells = []
        for cells in self.data[self.block_type]['cells']:
            cell_list = NRichList()
            for cell in cells:
                cell_list.append(NRichText(cell))
            self._cells.append(NRichList(cell_list))
        return self._cells

    @cells.setter
    def cells(self, cells: list):
        if self._cells:
            if len(self._cells[0]) != 1:
                raise ValueError("Text formatting have to be the same for the all table")
            if len(cells) != len(self._cells):
                raise ValueError("Number of columns doesn't match")
            for jdx, el in enumerate(self._cells):
                el[0]['text'].data['content'] = cells[jdx]
                el[0].data['plain_text'] = cells[jdx]
            self.update_block()
        else:
            self._cells = []
            for cell in cells:
                cell_rich = NRichList()
                cell_obj = NRichText(
                    {
                        "type": "text",
                        "text": {
                            "content": str(cell),
                            "link": None
                        },
                        "annotations": {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default"
                        },
                        "plain_text": str(cell),
                        "href": None
                    }
                )
                cell_rich.append(cell_obj)
                self._cells.append(cell_rich)
            self.cells = cells

    def add_row(self, value: NRichList):
        load_data = []
        for v in value:
            row_list = []
            for row in v:
                row_list.append(row.to_dict())
            load_data.append(row_list)
        self._cells = load_data

    def _get_spec_dict(self):
        cells = []
        for cell in self._cells:
            cells.append(self._get_rich_text_dict(cell))
        bl_dict = {
                "cells": cells,
            }

        return {
            'type': 'table_row',
            'table_row': bl_dict
        }

class NTitle(NBlock):
    block_type = "title"

    def __init__(self, header: dict, block_id: str):
        """
        self._rich_text -> list of richeText Objects
        self._icon -> callout icon -> NIcon(Ntype)
        self._color -> callout color -> Color
        """
        super().__init__(header, block_id)
        self._rich_text = None

    def _get_spec_dict(self):
        return {
            'type': 'title',
            'title': self._get_rich_text_dict()
        }


if __name__ == '__main__':
    id_ = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75?source=copy_link#2999b4f7b3cd8093a664f26f6cd38deb"
    api_ = NotionApiClient(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0")
    block_ = load_block(header=api_.headers, block_id=id_)
    block_.get_content()
    print('------------------ CLASS NAME ---------------------------')
    print(block_.__class__.__name__)
    print('------------------ BLOCK - DATA ---------------------------')
    print(block_)
    print('------------------ MODS ----------------------------')
    block_.update_cells([['10,10', '10,20', '10,30'], ['20,10', '20,20', '20,30'], ['30,10', '30,20', '30,30']])
    print('------------------ GET - DICT ----------------------------')
    from pprint import pprint
    block_.update_block() # noqa
    pprint(block_)
    print('----------------------------------------------')

#TODO: Table -> https://developers.notion.com/reference/block#table







