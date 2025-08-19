import copy
import re
import requests
from datetime import datetime
import pandas as pd
from setuptools.errors import CompileError

"""
sempre in riferimento alla documentazione ufficiale
1. -> Notion Integration Class - solo init
2. -> Notion page: ereditarietà + init (page e response) -> fallo con il debug
                   @property + get_properties
                   __str__
                   update_properties + Notion Integration TYPES 
                   load_properties
                   retrieve_children
3. -> Notion database: __init__
                       query a column
                       query all columns            
"""

def id_by_link(url: str):
    pattern = re.compile(r"notion\.so/[^/\?]*-([0-9a-f]{32})") # type: ignore
    match = pattern.search(url)
    if match:
        return match.group(1)
    else:
        raise CompileError("Url is not matching predefined Formula")


class NotionIntegration:
    TYPES = {
        'date': {'start': 'PLACE-HERE', 'end': None, 'time_zone': None},
        'rich_text': [{'type': 'text', 'text': {'content': 'PLACE-HERE', 'link': None},
                       'annotations': {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False,
                                       'code': False, 'color': 'default'}, 'plain_text': 'PLACE-HERE',
                       'href': None}],
        'number': -1,
        'checkbox': False,
        'title': [{'type': 'text', 'text': {'content': 'PLACE-HERE', 'link': None},
                   'annotations': {'bold': False, 'italic': False, 'strikethrough': False, 'underline': False,
                                   'code': False, 'color': 'default'}, 'plain_text': 'PLACE-HERE', 'href': None}]
    }

    def __init__(self, key):
        self.key = key
        self.headers = {
            "Authorization": "Bearer " + self.key,
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
            "accept": "application/json",
        }



class NotionPage(NotionIntegration):
    def __init__(self, page_token: str, *args, **kwargs):
        self.children = None
        page_token = page_token.replace('-', '')
        if len(page_token) != 32:
            raise ValueError('Page Token Length is Incorrect')
        super().__init__(*args, **kwargs)
        self.page = f"https://api.notion.com/v1/pages/{page_token}"
        self.response = self.get_page()
        self.page_properties = self.get_page_properties()

    def get_page(self):
        response = requests.get(self.page, headers=self.headers)
        if response:
            return response.json()
        else:
            raise ConnectionError(f"Function Failed with: {response}:\n\t\t {response.json()['message']}")

    def get_page_properties(self):
        return self.response['properties']

    def is_archived(self):
        return self.response['archived']

    def is_trash(self):
        return self.response['in_trash']

    @property
    def creator(self):
        return self.response['created_by']['id']

    @property
    def creation_date(self):
        return self.response['created_time']

    @property
    def page_id(self):
        return self.response['id']

    @property
    def object_type(self):
        return self.response['object']

    @property
    def parent(self):
        parent_info = []
        for k, v in self.response['parent'].items():
            parent_info.append(v)
        return {parent_info[0]: parent_info[1]}

    @property
    def url(self):
        return self.response['url']

    @property
    def request_id(self):
        return self.response['request_id']

    def update_property(self, prop_name: str, new_value):
        for prop, values in self.page_properties.items():
            if prop == prop_name:
                to_modify = copy.deepcopy(self.TYPES[values['type']])
                if values['type'] == 'rich_text':
                    if isinstance(new_value, str):
                        to_modify[0]['text']['content'] = new_value
                        to_modify[0]['plain_text'] = new_value
                        values['rich_text'] = to_modify
                    else:
                        raise ValueError('New Element have to be a string')
                elif values['type'] == 'date':
                    if isinstance(new_value, list) and len(new_value) < 3:
                        for idx, value in enumerate(new_value):
                            if isinstance(value, datetime):
                                if idx:
                                    to_modify['end'] = value.strftime("%Y-%m-%dT%H:%M:%S.000+02:00")
                                else:
                                    to_modify['start'] = value.strftime("%Y-%m-%dT%H:%M:%S.000+02:00")
                            else:
                                raise ValueError("element list have to be a datetime object")
                        values['date'] = to_modify
                    else:
                        raise ValueError("New Element have to be a list of two datetime elements")
                elif values['type'] == 'number':
                    if isinstance(new_value, int) or isinstance(new_value, float) :
                        values['number'] = new_value
                elif values['type'] == 'title':
                    if isinstance(new_value, str):
                        to_modify[0]['text']['content'] = new_value
                        values['title'] = to_modify
                    else:
                        raise ValueError('New Element have to be a string')
                break
        else:
            raise ValueError('Property Name does not exist')

    def load_properties(self):
        response = requests.patch(self.page, json={'properties': self.page_properties}, headers=self.headers)
        if not response:
            raise ValueError(f"Patch failed with: {response}:\n\t\t {response.json()['message']}")

    def retrieve_children(self):
        url = f"https://api.notion.com/v1/blocks/{self.page_id}/children?page_size=200"
        response = requests.get(url, headers=self.headers)
        if response:
            self.children = response.json()['results']
        else:
            raise ValueError(f"Get failed with: {response}:\n\t\t {response.json()['message']}")

    def __str__(self):
        ret_str = ""
        for key, value in self.page_properties.items():
            ret_str += f"{key}: "
            for kk, vv in value.items():
                ret_str += f"\t{kk}: {vv}\t\t"
            ret_str += '\n'
        return ret_str


class NotionDatabase(NotionIntegration):
    def __init__(self, db_token, *args, **kwargs):
        self.children_pages = []
        self.token = db_token
        self.db_link = f'https://api.notion.com/v1/databases/{db_token}'
        super().__init__(*args, **kwargs)
        self.db_properties = {}
        self.get_db_properties()

    def get_db_properties(self):
        response = requests.get(self.db_link, headers=self.headers)
        if response:
            for name, infos in response.json()['properties'].items():
                self.db_properties[name] = infos['id']
        else:
            raise ValueError(f"Get failed with: {response}:\n\t\t {response.json()['message']}")

    def query_a_property(self, prop_name, prop_id):
        column = {prop_name: []}
        query = self.db_link + f"/query?filter_properties={prop_id}"
        response = requests.post(query, headers=self.headers)
        if response:
            datas = response.json()['results'] # list
            type_ = datas[0]['properties'][prop_name]['type']
            for data in datas:
                id_ = data['id']
                if type_ == 'rich_text':
                    value = data['properties'][prop_name]['rich_text'][0]['plain_text']
                elif type_ == 'number':
                    value = data['properties'][prop_name]['number']
                elif type_ == 'date':
                    if data['properties'][prop_name]['date']['end']:
                        value = (data['properties'][prop_name]['date']['start'],
                                 data['properties'][prop_name]['date']['start'])
                    else:
                        value = data['properties'][prop_name]['date']['start']
                elif type_ == 'title':
                    value = data['properties'][prop_name]['title'][0]['plain_text']
                elif type_ == 'checkbox':
                    value = data['properties'][prop_name]['checkbox']
                else:
                    raise ValueError(f"Type {type_} is not managed")
                column[prop_name].append((id_, value))
        column[prop_name].reverse()
        return column

    def query_all_columns(self):
        all_columns = []
        if self.db_properties:
            for prop, obj_id in self.db_properties.items():
                all_columns.append(self.query_a_property(prop, obj_id))
            structured = {}
            for item in all_columns:
                for key, values in item.items():
                    for id_, value in values:
                        if id_ not in structured:
                            structured[id_] = {}
                        structured[id_][key] = value
            df = pd.DataFrame.from_dict(structured, orient='index')
            df.index.name = 'ID'
            return df
        else:
            raise ValueError('Retrieve properties is needed')

    def retrieve_children_ids(self):
        url = query = self.db_link + f"/query"
        response = requests.post(query, headers=self.headers)
        if response:
            for page in response.json()['results']:
                self.children_pages.append(page['id'])
        else:
            raise ValueError(f"Get failed with: {response}:\n\t\t {response.json()['message']}")

