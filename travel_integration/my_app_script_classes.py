import json
import os.path
from abc import ABC, abstractmethod

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


JSON_FOLDER = 'auth_json'
CREDENTIAL_FILE = os.path.join(JSON_FOLDER, 'credentials.json')
MATCH_FILE = os.path.join(JSON_FOLDER, 'match_file.json')


def find_file_by_scopes(scopes: list[str]) -> str:
    """
    Given scopes in input return the file desired name for that auths
    :param scopes: ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/script.scriptapp"]
    :return: token_calendar_script-scriptapp.json
    """
    last_names = []
    for url in scopes:
        last_names.append(url.split('/')[-1].replace('.', '-'))
    return 'token_' + '_'.join(last_names) + '.json'


"""
Token File Generation is a class problem
Credential Generation is an instance problem
When an instance is created the respective token already exists
"""
class ScriptAuth(ABC):
    _token = os.path.join(JSON_FOLDER, 'token.json')
    _scopes = ["https://www.googleapis.com/auth/script.projects"]
    response = None

    def __new__(cls, *args, scopes=None, **kwargs):
        if not scopes:
            raise ValueError(
                """
                Please enter a list of valid scopes - see 
                https://www.notion.so/Googla-App-Script-2409b4f7b3cd8087b004cdef92c2389e?source=copy_link#2419b4f7b3cd8039bc28d14eb37da24c  
                for documentation.
                """
            )

        if not os.path.exists(MATCH_FILE):
            with open(MATCH_FILE, "w") as f:
                json.dump({'file.json': []}, f)

        if os.path.exists(cls._token):
            if cls._scopes == scopes:
                print('Everything is ok')
            else:
                cls._scopes = scopes
                with open(MATCH_FILE, "r") as f:
                    existing_files = json.load(f)  # type: ignore
                for file, auths in existing_files.items():
                    if scopes == auths:
                        cls._token = os.path.join(JSON_FOLDER, file)
                        break
                else:
                    file_name = find_file_by_scopes(scopes)
                    existing_files[file_name] = scopes
                    cls._token = os.path.join(JSON_FOLDER, file_name)
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIAL_FILE, scopes
                    )
                    creds = flow.run_local_server(port=0)
                    # save the new token file
                    with open(cls._token, "w") as token:
                        token.write(creds.to_json())
                    # update the matching file with the new token
                    with open(MATCH_FILE, "w") as f:
                        json.dump(existing_files, f)
        return super().__new__(cls)

    def __init__(self, scopes):
        self.creds = Credentials.from_authorized_user_file(self._token, self._scopes)
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())

    def __repr__(self):
        return f'token: {self._token}\nscopes: {self._scopes}\ncred: {self.creds}'



class ExecuteScriptWithoutResponse(ScriptAuth, ABC):
    """
    Usage Input example:
    SCOPES = ["https://www.googleapis.com/auth/script.projects",
          "https://www.googleapis.com/auth/calendar",
          "https://www.googleapis.com/auth/calendar.readonly"]
    request_ = {"function": "fromCalendar", "parameters": ['Cose da fare']}
    script_id_ = "AKfycbwB5sjD3aqbZk6upxIXfvCCz4LptXNcmRrH1Tui8QCN"
    """
    def __init__(self, scrip_id: str, request: dict, scopes: list[str]):
        """
        :param scrip_id: from app.script/settings/ID, e.g. "AKfycbwB5sjD3aqbZk6upxIXfvCCz4LptXNcmRrH1Tui8QCN"
        :param request: what to run, e.g.: {"function": "fromCalendar"}
        :param scopes: list of authorization, e.g.: ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/script.scriptapp"]
        """
        super().__init__(scopes)
        self.request = request
        self.script_id = scrip_id
        self.service = build("script", "v1", credentials=self.creds)
        self.get_script_response()

    def get_script_response(self):
        response = self.service.scripts().run(scriptId=self.script_id, body=self.request).execute()
        if "error" in response:
            error = response["error"]["details"][0]
            print(f"Script error message: {0}.{format(error['errorMessage'])}")
            if "scriptStackTraceElements" in error:
                print("Script error stacktrace:")
                for trace in error["scriptStackTraceElements"]:
                    print(f"\t{0}: {1}.{format(trace['function'], trace['lineNumber'])}")
        else:
            folder_set = response["response"].get("result", {})
            if not folder_set:
                print("No folders returned!")
            else:
                self.response = folder_set


class ExecuteScriptWithResponse(ExecuteScriptWithoutResponse, ABC):
    @abstractmethod
    def printResponse(self):
        pass

    @abstractmethod
    def retrievedResponse(self):
        pass


class GetsAllMyEvent(ExecuteScriptWithResponse):
    def printResponse(self):
        for folder_id, folder in self.response.items():
          for event in folder:
              print(event[0], ' -> ' , event[2])

    def retrievedResponse(self):
        return self.response.value()[0]


class CreateEvent(ExecuteScriptWithoutResponse):
    pass



if __name__ == '__main__':

    # SCOPES = ["https://www.googleapis.com/auth/script.scriptapp",
    #           "https://www.googleapis.com/auth/calendar"]
    #
    # request_ = {"function": "crea_evento", "parameters": ['Allenamento', 'provaPython', '07/31/2025 14:00', '07/31/2025 15:00', 'descrizione di prova creata con lo script Python']}
    # script_id_ = "AKfycbwB5sjD3aqbZk6upxIXfvCCz4LptXNcmRrH1Tui8QCN"
    #
    # script_1 = CreateEvent(scopes=SCOPES, request=request_, scrip_id=script_id_)
    #
    # request_ = {"function": "fromCalendar"}
    # script_2 = GetsAllMyEvent(scopes=SCOPES, request=request_, scrip_id=script_id_)
    # script_2.printResponse()


    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    request_ = {"function": "fillExcel", "parameters": ['1fHsrb8oRcN13gh0lAoou1Kz43nSELVHVZufN9ps5O6k',
                                                        [
                                                            ['via Aereo', 123, 330],
                                                            ['Via Auto', 12, 20],
                                                            ['Via Piedi', 64, 0]
                                                        ]
                                                        ]}
    script_id_ = "AKfycbzYnNkuoQGFB7qsvFnzw-YHQ125k5BILWUuYdMTWa9D6fL7Nnn4C4LdwZjz3WZjK7rE"

    script_1 = CreateEvent(scopes=SCOPES, request=request_, scrip_id=script_id_)

