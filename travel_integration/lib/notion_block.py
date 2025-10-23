import re

from utils import Color
from notion_object import NObj, ObjectError
from notion_client import NotionApiClient
from notion_types import (
    NRichList, rich_list_text, NRichText, Ntype, NText
)


# creiamo una factory
def load_block(header: dict, block_id: str):
    """
    Trova automaticamente il tipo di blocco con cui si sta lavorando
    """
    block = NBlock(header, block_id)
    block.get_content()
    if block.block_type == "paragraph":
        return NParagraph(header, block_id)
    elif block.block_type == "divider":
        return NDivider(header, block_id)
    elif block.block_type == "bulleted_list_item":
        return NBulletListItem(header, block_id)
    elif block.block_type == "bookmark":
        return NBookmark(header, block_id)
    elif block.block_type == "breadcrumb":
        return NBreadcrumb(header, block_id)
    # aggiungi altri tipi se servono
    return block


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
        self.update_url = f"https://api.notion.com/v1/blocks/{block_id}"
        self.get_children_url = f"https://api.notion.com/v1/blocks/{self.block_id}/children" #TODO
        self.append_children_url = f"https://api.notion.com/v1/blocks/{self.block_id}/children" #TODO
        self.delete_url = f"https://api.notion.com/v1/blocks/{self.block_id}"

    @property
    def block_type(self):
        if not self.data:
            self.get_content()
        return self.data['type']

    def _get_spec_dict(self) -> dict:
        return {}

    # Rich text
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
        return rich_list_text(self._rich_text)

    def _get_rich_text_dict(self, att = None):
        if not att:
            att = self._rich_text
        rt = []
        try:
            for r in att:
                rd = r.to_dict()
                for j, item in rd.items():
                    if isinstance(item, Ntype):
                        rd[j] = item.to_dict()
                if rd['annotations'] is None:
                    rd['annotations'] = {
                            "bold": False,
                            "italic": False,
                            "strikethrough": False,
                            "underline": False,
                            "code": False,
                            "color": "default"
                          }
                rt.append(rd)
        except TypeError as e:
            raise  TypeError(f"Error: {e}, rich could be empty, try to call self.get_rich_text or use rich_text setter!")
        return rt
    # rich text


"""
Blocchi specifici:
    - inizializziamo gli attributi specifici per l' oggetto
            self._attr = None
    - getter e setter per ogni attributo
    - get_content() andrà anche a riempire tutti i valori correnti
    - _get_spec_dict(self) -> dizionario con tutti i parametri che andranno riempiti come si può!
    prova il blocco:
        _id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75?source=copy_link#2959b4f7b3cd8074ac6ee817503792ce"
        api = NotionApiClient(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0")
        # block = NBlock(header=api.headers, block_id=_id)
        block = load_block(header=api.headers, block_id=_id)
        block.get_content()
        print('----------------------------------------------')
        print(block.__class__.__name__)
        print('----------------------------------------------')
        print(block.data)
        print('----------------------------------------------')
        print(block._get_spec_dict())
        print('----------------------------------------------')
"""


class NDivider(NBlock):
    block_type = "divider"
    def _get_spec_dict(self): # noqa
        return {
            'type': 'divider',
            'divider': {}
        }

class NBreadcrumb(NBlock):
    block_type = "breadcrumb"
    def _get_spec_dict(self): # noqa
        return {
            'type': 'breadcrumb',
            'breadcrumb': {}
        }

class NBookmark(NBlock):
    block_type = "bookmark"

    def __init__(self, header: dict, block_id: str):
        """
        self._rich_text -> list of richeText Objects
        self._color -> paragraph base color
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
                self.color = value
        else:
            self.color = value.value()

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

class NBulletListItem(NParagraph):
    block_type = "bulleted_list_item"

    def _get_spec_dict(self):
        bl_dict = {
                "rich_text": self._get_rich_text_dict(),
                "color": self._color,
            }
        return {
            'type': 'bulleted_list_item',
            'bulleted_list_item': bl_dict
        }

if __name__ == '__main__':
    _id = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75?source=copy_link#2959b4f7b3cd8074ac6ee817503792ce"
    api = NotionApiClient(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0")
    # block = NBlock(header=api.headers, block_id=_id)
    block = load_block(header=api.headers, block_id=_id)
    block.get_content()
    print('----------------------------------------------')
    print(block.__class__.__name__)
    print('----------------------------------------------')
    print(block.data)
    print('----------------------------------------------')
    print(block._get_spec_dict())
    print('----------------------------------------------')

#TODO: Callout -> https://developers.notion.com/reference/block#bookmark







