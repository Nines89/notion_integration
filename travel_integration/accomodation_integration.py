import math
import time
from typing import Any
import requests

from datetime import datetime
from basic_class import NotionPage, NotionDatabase, id_by_link
from my_app_script_classes import ExecuteScriptWithoutResponse

r"""
1. -> incolla da travel_integration.py
2. -> cambia nomi classi
3. -> modifica accommodation specific
4. -> modifica accommodation button
5. -> modify_db_page (commenta tutto quello che riguarda i grafici)
"""

ACC_SS = '1dTVnF0qZypEtE8LM_fUSPcxFfhMfipo_KdpdnO7WUaE'
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
REQUEST = {
    "function": "fillExcel",
    "parameters": [None, None]
}
SCRIPT_ID = "AKfycbw_Dmw3BJgBEDDUpSeDd3N32YaG2yW3JhkLZlVJdLWg6VGRrELRECSKq231R-1Wsa4J"


def date_parser(date: str) -> (int, int, int, int, int, int, int):
    return int(date[0:4]), int(date[5:7]), int(date[8:10]), int(date[11:13]), int(date[14:16]), int(date[17:19])


class UpdateSpreadsheet(ExecuteScriptWithoutResponse):
    pass


class AccommodationButton(NotionPage):
    dbs_id = []
    SECRET = "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"
    choice_id = None

    def __init__(self, *args, **kwargs):
        super().__init__(key=self.SECRET, *args, **kwargs)
        self.get_dbs()

    def get_dbs(self):
        if not self.children:
            self.retrieve_children()
        for child in self.children:
            if child['type'] == 'child_database':
                if child['child_database']['title'].strip() != 'Choices':
                    self.dbs_id.append(child['id'])
                else:
                    self.choice_id = child['id']

    def modify_db_page(self):
        if self.dbs_id:
            for idx, db_id in enumerate(self.dbs_id):
                google_script_matrix = []
                db = NotionDatabase(db_token=db_id, key=self.SECRET)
                db.retrieve_children_ids()
                if db.children_pages:
                    for page in db.children_pages:
                        accom_page = AccommodationSpecific(page_token=page)
                        accom_page.build_calculation()
                        google_script_matrix.append([
                            accom_page.page_properties['Name']['title'][0]['plain_text'],
                            accom_page.ch_prop['Total Price'],
                            accom_page.ch_prop['Distance From (m)'],
                        ])
                        accom_page.update_parent()
                    REQUEST['parameters'][0] = ACC_SS
                    REQUEST['parameters'][1] = google_script_matrix
                    UpdateSpreadsheet(scopes=SCOPES, scrip_id=SCRIPT_ID, request=REQUEST)
                else:
                    print('No pages in DB')
        else:
            raise ValueError('No DB-ID are saved')

    def fil_choices(self):
        res_name = None
        tot_amount = 0
        address = None

        if self.dbs_id:
            for db_id in self.dbs_id:
                db = NotionDatabase(db_token=db_id, key=self.SECRET)
                for prop, obj_id in db.db_properties.items():
                    if prop == 'Choice':
                        column = db.query_a_property(prop, obj_id)
                        for kind in column['Choice']:
                            if kind[1]:
                                chosen_one_id = kind[0]
                                chosen_one_page = AccommodationSpecific(chosen_one_id)
                                chosen_props = chosen_one_page.page_properties
                                tot_amount = float(chosen_props['Total Price']['number'])
                                res_name = chosen_props['Name']['title'][0]['plain_text']
                                address = chosen_props['Address']['rich_text'][0]['plain_text']

            if self.choice_id and tot_amount and res_name:
                # Copia dalle API ################################################################
                url = 'https://api.notion.com/v1/pages'
                data_info = {
                    "parent": {"database_id": self.choice_id.replace('-', '')},
                    "properties": {
                        "Name": {
                            "title": [
                                {
                                    "text": {
                                        "content": res_name
                                    }
                                }
                            ]
                        },
                        "Address": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": address
                                    }
                                }
                            ]
                        },
                        "Total Price": {"number": tot_amount},
                    },
                }
                ################################################################
                response = requests.post(url, json=data_info, headers=self.headers)
                if not response:
                    raise ConnectionError(
                        f"Function Failed with: {response}:\n\t\t {response.json()['message']}")


class AccommodationSpecific(NotionPage):
    section_db = None
    SECRET = "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"
    ch_prop: dict[str, Any] = {
        "Address": None,
        'Total Price': None,
        "Distance From (m)": None,
        "Check - In": None,
        "Check - Out": None
    }

    def __init__(self, *args, **kwargs):
        super().__init__(key=self.SECRET, *args, **kwargs)
        self.get_db()

    def get_sections_db_id(self):
        self.retrieve_children()
        return self.children[0]['id']

    def get_db(self):
        self.section_db = NotionDatabase(key=self.SECRET, db_token=self.get_sections_db_id())

    """
    {'Distance From (m)': {'25ab7a8f-7294-8046-bccd-c38eb4d21680': '1000'},
     'Name': {'25ab7a8f-7294-8046-bccd-c38eb4d21680': 'hotel 1'},
     'Price Per Night': {'25ab7a8f-7294-8046-bccd-c38eb4d21680': 30},
     'check in': {'25ab7a8f-7294-8046-bccd-c38eb4d21680': '2025-08-25T14:00:00.000+02:00'},
     'check out': {'25ab7a8f-7294-8046-bccd-c38eb4d21680': '2025-08-30T10:00:00.000+02:00'}}
     'address'
    """

    def build_calculation(self):
        df = self.section_db.query_all_columns()
        self.ch_prop["Check - In"] = [datetime(*date_parser(df['check in'].to_list()[0]))]
        self.ch_prop['Check - Out'] = [datetime(*date_parser(df['check out'].to_list()[-1]))]
        self.ch_prop["Distance From (m)"] = int(sum(df['Distance From (m)'].to_list()) / len(df['Distance From (m)'].to_list()))
        nights = []
        for d in range(len(df['check out'].to_list())):
            date_for_days = datetime(*date_parser(df['check out'].to_list()[d])) - datetime(*date_parser(df['check in'].to_list()[d]))
            # Con total_seconds()/86400 ottieni i giorni come numero decimale,
            # Con ceil li porti al numero intero superiore, che corrisponde alle notti effettive.
            nights.append(math.ceil(date_for_days.total_seconds() / 86400))
        self.ch_prop["Total Price"] = sum(
            map(
                lambda n_p: n_p[0] * n_p[1], zip(nights, df['Price Per Night'].to_list())
            )
        )
        self.ch_prop["Address"] = '-'.join(add for add in df['address'].to_list())


    def update_parent(self):
        if self.ch_prop["Address"]:
            for prop, val in self.ch_prop.items():
                self.update_property(prop, val)
            self.load_properties()
        else:
            raise ValueError("Property dictionary is empty")

def main_build_info(page_link: str):
    button_page = AccommodationButton(page_token=id_by_link(
        page_link
    ))
    button_page.retrieve_children()
    button_page.modify_db_page()

def main_fil_choice(page_link: str):
    button_page = AccommodationButton(page_token=id_by_link(
        page_link
    ))
    button_page.fil_choices()


if __name__ == '__main__':
    st_time = time.time()
    # main_fil_choice("https://www.notion.so/Accommodation-248b7a8f729480e79e36cf24462f8348?source=copy_link")
    main_build_info("https://www.notion.so/Accommodation-248b7a8f729480e79e36cf24462f8348?source=copy_link")
    print('TOT time: ', time.time() - st_time)

# travel_page = TravelSpecific(page_token=id_by_link(
#     "https://www.notion.so/Travel-24cb7a8f729480739e5fcc7e132a943a?source=copy_link"
# )
# travel_page.build_calculation()
# travel_page.update_parent()


# accommodation_page = AccomodationSpecific(
#         id_by_link('https://www.notion.so/Accommodation-Specific-25ab7a8f729480d18826d4d06a40a019?source=copy_link'))
# accommodation_page.build_calculation()
# accommodation_page.update_parent()


# acc_button = AccommodationButton(
#          id_by_link('https://www.notion.so/Accommodation-248b7a8f729480e79e36cf24462f8348?source=copy_link'))
# acc_button.fil_choices()

