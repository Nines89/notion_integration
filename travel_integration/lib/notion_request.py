import requests

class ResponseError(Exception):
    pass

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
        raise ValueError(f"{self.name} failed with: {response}:\n\t\t {response.json()['message']}")

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

