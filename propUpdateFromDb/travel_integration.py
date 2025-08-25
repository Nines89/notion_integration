import time
from typing import Any
import requests

from datetime import datetime
from basic_class import NotionPage, NotionDatabase, id_by_link
from my_app_script_classes import ExecuteScriptWithoutResponse

r"""
1. -> class traffic specific
2. -> init con secret nella classe
3. -> get section id
4. -> build calculation (fino all' id)
5. -> schema: data -> Date[0]
              durata -> Data[-1] - Data[0] + Durata[-1]
              costo -> sum(costo)
              partenza -> partenza[0]
              arrivo -> arrivo[-1]
6. -> lavoro con il df
7. -> ch_prop - chiavi = nomi degli attributi
8. -> update parent

9. -> id_by_link
        regex - regex 101
        notion\.so/ → assicura che la regex cerchi solo nelle URL di Notion
        [^/\?]*- → ignora qualsiasi testo tra lo slash (/) e il trattino che precede l’ID
        ([0-9a-f]{32}) → cattura una stringa di 32 caratteri esadecimali (da 0–9 e a–f) nell’unica cattura disponibile
        
10. -> class Travel Button -> questa la facciamo dopo aver inserito il terzo database alla pagina
11. -> fil choice - modifica a get_dbs - add checkbox in notion page - post con json
12. -> aggiungi le funzioni main

13. -> modifica modify_db_page per riempire la matrice google_script_matrix e poi crea la classe 
       UpdateSpreadsheet e chiamala nella stessa funzione con i giusti parametri definiti all' inizio
       DEP_SS, BACK_SS, SCOPES, REQUEST
"""

DEP_SS = '1fHsrb8oRcN13gh0lAoou1Kz43nSELVHVZufN9ps5O6k'
RET_SS = '1wPeMl4liRc-7Kk9Z7IQhnvRrnhSp6c9GliwC_h_Vyhc'
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
REQUEST = {"function": "fillExcel", "parameters": [ None,
                                                    None
                                                    ]}
SCRIPT_ID = "AKfycbzYnNkuoQGFB7qsvFnzw-YHQ125k5BILWUuYdMTWa9D6fL7Nnn4C4LdwZjz3WZjK7rE"

def date_parser(date: str) -> (int, int, int, int, int, int, int):
    return int(date[0:4]), int(date[5:7]), int(date[8:10]), int(date[11:13]), int(date[14:16]), int(date[17:19])


class UpdateSpreadsheet(ExecuteScriptWithoutResponse):
    pass

class TravelButton(NotionPage):
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
                        travel_page = TravelSpecific(page_token=page)
                        travel_page.build_calculation()
                        google_script_matrix.append([
                            travel_page.page_properties['Travel Method']['title'][0]['plain_text'],
                            (lambda h: int(h.split(':')[0]) * 60 + int(h.split(':')[1]))(travel_page.ch_prop['Duration - hh:mm']),
                            travel_page.ch_prop['Total Amount']
                        ])
                        travel_page.update_parent()
                    if idx == 2:
                        REQUEST['parameters'][0] = RET_SS
                    elif idx == 1:
                        REQUEST['parameters'][0] = DEP_SS
                    else:
                        continue
                    REQUEST['parameters'][1] = google_script_matrix
                    UpdateSpreadsheet(scopes=SCOPES, scrip_id=SCRIPT_ID, request=REQUEST)
                else:
                    print('No pages in DB')
        else:
            raise ValueError('No DB-ID are saved')

    def fil_choices(self):
        dep_met = None
        tot_amount = 0
        back_met = None

        if self.dbs_id:
            for idx, db_id in enumerate(self.dbs_id):
                db = NotionDatabase(db_token=db_id, key=self.SECRET)
                for prop, obj_id in db.db_properties.items():
                    if prop == 'Choice':
                        column = db.query_a_property(prop, obj_id)
                        for kind in column['Choice']:
                            if kind[1]:
                                chosen_one_id = kind[0]
                                chosen_one_page = TravelSpecific(chosen_one_id)
                                chosen_props = chosen_one_page.page_properties
                                tot_amount += float(chosen_props['Total Amount']['number'])
                                method = chosen_props['Travel Method']['title'][0]['plain_text']
                                if idx == 0:
                                    dep_met = method
                                elif idx == 1:
                                    back_met = method
            if self.choice_id and tot_amount and back_met and dep_met:
                # Copia dalle API ################################################################
                url = 'https://api.notion.com/v1/pages'
                data_info = {
                              "parent": { "database_id": self.choice_id.replace('-', '') },
                              "properties": {
                                    "Back and Forth": {
                                        "title": [
                                            {
                                                "text": {
                                                    "content": "Travel To"
                                                }
                                            }
                                        ]
                                    },
                                    "Departure Method": {
                                        "rich_text": [
                                            {
                                                "text": {
                                                    "content": dep_met
                                                }
                                            }
                                        ]
                                    },
                                    "Return Method": {
                                        "rich_text": [
                                            {
                                                "text": {
                                                    "content": back_met
                                                }
                                            }
                                        ]
                                    },
                                    "Total Travel Amount": { "number": tot_amount },
                                },
                            }
                ################################################################
                response = requests.post(url, json=data_info, headers=self.headers)
                if not response:
                    raise ConnectionError(
                        f"Function Failed with: {response}:\n\t\t {response.json()['message']}")


class TravelSpecific(NotionPage):
    section_db = None
    SECRET = "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"
    ch_prop: dict[str, Any] = {
        "Departure Date": None,
        'Duration - hh:mm': None,
        "Total Amount": None,
        "Starting Address": None,
        "Ending Address": None
    }

    def __init__(self, *args, **kwargs):
        super().__init__(key=self.SECRET, *args, **kwargs)
        self.get_db()

    def get_sections_db_id(self):
        self.retrieve_children()
        return self.children[0]['id']

    def get_db(self):
        self.section_db = NotionDatabase(key=self.SECRET, db_token=self.get_sections_db_id())

    def build_calculation(self):
        df = self.section_db.query_all_columns()
        self.ch_prop["Departure Date"] = [datetime(*date_parser(df['Date'].to_list()[0]))]
        travel_time = datetime(*date_parser(df['Date'].to_list()[-1])) - datetime(*date_parser(df['Date'].to_list()[0]))
        total_time_in_minute = int(travel_time.seconds / 60) + int(df['Duration (min)'].to_list()[-1])
        self.ch_prop['Duration - hh:mm'] = str(total_time_in_minute // 60) + ':' + str(total_time_in_minute % 60)
        self.ch_prop["Total Amount"] = sum(df['Costo'].to_list())
        self.ch_prop["Starting Address"] = df['Departure Address'].to_list()[0]
        self.ch_prop["Ending Address"] = df['Arrival Address'].to_list()[-1]

    def update_parent(self):
        if self.ch_prop["Starting Address"]:
            for prop, val in self.ch_prop.items():
                self.update_property(prop, val)
            self.load_properties()
        else:
            raise ValueError("Property dictionary is empty")


def main_build_info(page_link: str):
    button_page = TravelButton(page_token=id_by_link(
        page_link
    ))
    button_page.retrieve_children()
    button_page.modify_db_page()


def main_fil_choice(page_link: str):
    button_page = TravelButton(page_token=id_by_link(
        page_link
    ))
    button_page.fil_choices()


if __name__ == '__main__':
    st_time = time.time()
    main_build_info("https://www.notion.so/Travel-24cb7a8f729480739e5fcc7e132a943a?source=copy_link")
    # main_fil_choice("https://www.notion.so/Travel-24cb7a8f729480739e5fcc7e132a943a?source=copy_link")
    print('TOT time: ', time.time() - st_time)




# travel_page = TravelSpecific(page_token=id_by_link(
#     "https://www.notion.so/Travel-24cb7a8f729480739e5fcc7e132a943a?source=copy_link"
# )
# travel_page.build_calculation()
# travel_page.update_parent()

