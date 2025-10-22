import requests



"""
FIRST STEP:

response = requests.get(self.page, headers=self.headers)
if response:
    return response.json()
else:
    raise ConnectionError(f"Function Failed with: {response}:\n\t\t {response.json()['message']}")
"""

class ResponseError(Exception):
    pass


class NotionApiClient:
    def __init__(self, key, version: str = "2025-09-03"):
        self.key = key
        self.headers = {
            "Authorization": "Bearer " + self.key,
            "Content-Type": "application/json",
            "Notion-Version": version,
            "accept": "application/json",
        }


class NotionRequest:
    name = "Request"
    response = None

    def __init__(self, url: str, header: dict = None):
        if not header:
            raise ValueError("Header info must be provided")
        self.header = header
        self.url = url

    def response_handler(self, response: requests.Response):
        if response:
            return response.json()
        raise ValueError(f"{self.name} failed with: {response}: \n\t\t\t{response.json()['message']}")


    def __getitem__(self, key):
        if self.response:
            if key in self.response:
                return self.response[key]
            raise ResponseError(f"The response key {key} does not exist")
        raise ResponseError(f"The request response doesn't exists")

    def __repr__(self):
        return self.response


class NGET(NotionRequest):
    def __init__(self, url: str, header: dict = None):
        super().__init__(url, header)
        self.response = self.response_handler(requests.get(self.url, headers=self.header))


class NPOST(NotionRequest):
    def __init__(self, url: str, header: dict, data: dict):
        super().__init__(url, header)
        self.response = self.response_handler(requests.post(self.url, json=data, headers=self.header))


class NPATCH(NotionRequest):
    def __init__(self, url: str, header: dict, data: dict):
        super().__init__(url, header)
        self.response = self.response_handler(requests.patch(self.url, json=data, headers=self.header))


class NDEL(NotionRequest):
    def __init__(self, url: str, header: dict):
        super().__init__(url, header)
        self.response = self.response_handler(requests.delete(self.url, headers=self.header))


if __name__ == '__main__':
    api = NotionApiClient(key="secret_dmenkOROoW68ilWcGvmBS7PF49k5J1dAQbOx3KPhpz0")

    block_id = "28f9b4f7b3cd8056a2bcd75e2eec5387"
    block_id_up = "2929b4f7b3cd80c180e8c8f0e569c5c1"

    url_get = f"https://api.notion.com/v1/blocks/{block_id}"
    url_up_del = f"https://api.notion.com/v1/blocks/{block_id_up}"


    req = NGET(url_get, api.headers)

    req_update = NPATCH(url_up_del, api.headers, {
                                                  "to_do": {
                                                    "rich_text": [{
                                                      "text": { "content": "try hard" }
                                                      }],
                                                    "checked": True
                                                  }
                                                })

    req_delete = NDEL(url_up_del, api.headers)



