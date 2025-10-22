from notion_page import NotionPage
from pprint import pprint


if __name__ == "__main__":
    page = NotionPage.get(
        key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0",
        token="https://www.notion.so/Integration-Example-28f9b4f7b3cd80588296e08e56e45b75"
    )
    # pprint(page.page_info.response['properties'])
    children = page.get_block_children()
    inner_block = children.get(
        key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0",
        token=children.id_
    )


# TODO: passaggi per il test
# run debug
# per vedere i vari campi
# from pprint import pprint
# pprint(page.page_info.response)
# siamo arrivati a notion block - trasforma tutti i notion type in notion Block

# Parent - fallo in un secondo momento - https://developers.notion.com/reference/parent-object
# Page properties - fallo in un secondo momento -
