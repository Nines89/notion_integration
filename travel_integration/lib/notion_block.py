import re

from notion_object import NObj
from notion_client import NotionApiClient

# creiamo una factory
def load_block(header: dict, block_id: str):
    block = NBlock(header, block_id)
    block.get_content()
    if block.block_type == "paragraph":
        return NParagraph(header, block_id)
    # aggiungi altri tipi se servono
    return block

class NBlock(NObj):
    """
    Header contiene sia la versione delle API che il secret token.
    Block_id contiene la stringa con l' id, serve per il patch, il delete e il get

    per recuperare il blocco: block.get_content()
    per aggiornare il blocco: block.update_content(update_data)
    """
    obj_type = "block"
    pattern = re.compile(r"([0-9a-f]{32})\Z")

    def __init__(self, header: dict, block_id: str):
        match = self.pattern.search(block_id)
        if match:
            block_id = match.group(1)
        self.block_id = block_id.replace('-', '')  # inserito per quanto si recupera la pagina da un database
        if len(self.block_id) != 32:
            raise ValueError('Token Length is Incorrect')
        self.get_url = f"https://api.notion.com/v1/blocks/{self.block_id}"
        self.update_url = f"https://api.notion.com/v1/blocks/{block_id}"
        self.get_children = f"https://api.notion.com/v1/blocks/{self.block_id}/children" #TODO
        self.append_children = f"https://api.notion.com/v1/blocks/{self.block_id}/children" #TODO
        self.delete_url = f"https://api.notion.com/v1/blocks/{self.block_id}"
        super().__init__(header=header)


    @property
    def block_type(self):
        if not self.data:
            raise ValueError('Perform get_content to retrieve data block')
        return self.data['type']


class NParagraph(NBlock):
    block_type = "paragraph"

    def get_info(self):
        self.get_content()






if __name__ == '__main__':
    api = NotionApiClient(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0")
    contentId = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75?source=copy_link#2939b4f7b3cd80c7917ec9d71c5039eb"
    updateId = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-28f9b4f7b3cd80588296e08e56e45b75?source=copy_link#2929b4f7b3cd80679a55f7d8a15cfeca"
    parag = load_block(api.headers, contentId)

    print(parag)






