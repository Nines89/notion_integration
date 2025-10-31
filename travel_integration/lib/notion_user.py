
import re

from notion_client import NotionApiClient
from notion_object import NObj

from utils import BotType

class UserError(Exception):
    pass


def load_user(header: dict, block_id: str):
    block = NUser(header, block_id)
    block.get_content()
    if block.data['type'] == "person":
        return NPerson(header, block_id)
    elif block.data['type'] == "bot":
        return NBot(header, block_id)
    return block


class NUser(NObj):
    """
    Header contiene sia la versione delle API che il secret token.
    Block_id contiene la stringa con l' id, serve per il patch, il delete e il get
    """
    obj_type = "user"

    def __init__(self, header: dict, block_id: str = None):
        if block_id:
            self.block_id = block_id.replace('-', '')  # inserito per quanto si recupera la pagina da un database
            self.get_url = f"https://api.notion.com/v1/users/{block_id}"
            if len(self.block_id) != 32:
                raise ValueError('Token Length is Incorrect')
        self.get_all_users_url = f"https://api.notion.com/v1/users"
        self.get_bot_user_url = f"https://api.notion.com/v1/users/me"
        super().__init__(header=header)
        if block_id:
            self.get_content() # crea un oggetto NGET in self.data
            if self.data['object'] != self.obj_type:
                raise UserError(f"The Object {self.block_id} is not an user")
            self.name = self.data['name']
            self.avatar = self.data['avatar_url']
            self.request_id = self.data['request_id']

    def get_bot_user(self):
        self.data = load_user(self.header,
                          self._get(
                              api_url=self.get_bot_user_url,
                            )['id']
                          )


class NPerson(NUser):
    user_type = "person"
    def __init__(self, header: dict, block_id: str):
        super().__init__(header, block_id) # richiama la init di NUser
        self.email = self.data['person']['email']


class NBot(NUser):
    user_type = "bot"
    def __init__(self, header: dict, block_id: str):
        super().__init__(header, block_id)
        self.owner = self.data['bot']['owner']
        if self.owner['type'] == BotType.USER.value:
            self.user = NUser(header=self.header, block_id=self.owner['user']['id'])
            self.bot_workspace = None
        else:
            self.workspace = None
            self.workspace_name = self.data['bot']['workspace_name'] #TODO



if __name__ == '__main__':
    api = NotionApiClient(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0")
    blockId = "8711f079-8ae4-4748-89a7-d2daf31ff8fe"
    user = load_user(header=api.headers, block_id=blockId)
    user.get_bot_user()
    print(user.data.workspace_name) # noqa
    pass


