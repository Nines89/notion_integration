from abc import ABC, abstractmethod

from lib.notion_types import simple_rich_text_list
from lib.notion_user import NPerson
from notion_types import NDate, NRichList, NRichText


class PropertyError(Exception):
    pass


def load_prop_item(input_data: dict):
    item_types = {
        "checkbox": NPCheckBoxItem,
        'created_by': NPCreatedByItem,
        'created_time': NPCreatedTimeItem,
        'date': NPDateItem,
        'email': NPEmailItem,
        'files': NPFileItem,
        'formula': NPFormulaItem,
        'last_edited_by': NPEditedTimeItem,
        'multi_select': NPMultiSelectItem,
        'number': NPNumberItem,
        'phone_number': NPPhoneNumberItem,
        'select': NPSelectItem,
        'status': NPStatusItem,
        'url': NPUrlItem,
        'unique_id': NPUniqueIDItem,
    }
    if input_data['object'] == 'list':
        item_types = {
            "people": NPPeopleItem,
            'relation': NPRelationItem,
            'rollup': NPRollUpItem,
            'rich_text': NPRichTextItem,
            'title': NPTitleItem,
        }
        try:
            if input_data['property_item']['type'] == 'rollup':
                return item_types[input_data['property_item']['type']](input_data)
            else:
                return item_types[input_data['results'][0]['type']](input_data)
        except IndexError:
            raise PropertyError("List property results are empty. "
                                "Please check the data and that integration connection is shared with the pointed values.")
    cls = item_types.get(input_data['type'])
    if not cls:
        raise KeyError(f"Invalid Property Item Type '{input_data['type']}'")
    return cls(input_data=input_data)


class NPropertyList(ABC):
    obj_type = 'list'
    updatable = False

    def __init__(self, input_data: dict):
        """
        list_obj -> rappresenta la lista degli oggetti completi
        list_fix -> rappresenta la lista di quello che ci serve per eseguire l' update per ogni oggetto
        _name -> nome della proprietà
        _type -> tipo della proprietà
        """
        self.list_obj = input_data['results']
        self.list_fix = []
        self._name = input_data['name']
        self._type = input_data['results'][0]['type']
        pass

    @abstractmethod
    def fix_list_item(self):
        pass

    def to_dict(self):
        if not self.list_fix:
            self.fix_list_item()
        ret_list = []
        for item in self.list_fix:
            ret_list.append(item)
        return {
            self._name: {self._type: ret_list},
        }


class NPropertyItem(ABC):
    obj_type = 'property_item'
    updatable = False

    def __init__(self, input_data: dict):
        self._id = input_data['id']
        self._type = input_data['type']
        self._obj = input_data[f'{self._type}']
        self._request_id = input_data['request_id']
        self._name = input_data['name']
        pass

    @abstractmethod
    def to_dict(self):
        pass


class NPCheckBoxItem(NPropertyItem):
    obj_type = 'property_item'
    updatable = True

    @property
    def checkbox(self):
        return self._obj

    @checkbox.setter
    def checkbox(self, value: bool):
        self._obj = value

    def to_dict(self):
        return {
            f"{self._name}": {
                f"checkbox": self._obj,
            }
        }


class NPEmailItem(NPropertyItem):
    obj_type = 'email'
    updatable = True

    @property
    def email(self):
        return self._obj

    @email.setter
    def email(self, value: bool):
        self._obj = value

    def to_dict(self):
        return {
            f"{self._name}": {
                f"email": self._obj,
            }
        }


class NPCreatedByItem(NPropertyItem):
    obj_type = 'created_by'
    updatable = False

    def to_dict(self):
        return self._obj


class NPCreatedTimeItem(NPropertyItem):
    obj_type = 'created_time'
    updatable = False

    def to_dict(self):
        return self._obj


class NPEditedTimeItem(NPropertyItem):
    obj_type = 'last_edited_by'
    updatable = False

    def to_dict(self):
        return self._obj


class NPFileItem(NPropertyItem):
    obj_type = 'file'
    updatable = False

    def __init__(self, input_data: dict):
        super().__init__(input_data)

    def to_dict(self):
        return self._obj


class NPDateItem(NPropertyItem):
    obj_type = 'date'
    updatable = True

    def __init__(self, input_data: dict):
        super().__init__(input_data)
        self._startDate = NDate(self._obj['start']) # noqa
        self._endDate = NDate(self._obj['end'])  # noqa

    @property
    def endDate(self):
        return self._endDate.to_dict()

    @endDate.setter
    def endDate(self, value: NDate):
        self._endDate = value

    @property
    def startDate(self):
        return self._startDate.to_dict()

    @startDate.setter
    def startDate(self, value: NDate):
        self._startDate = value

    def to_dict(self):
        inner_dict = {
        }
        if self.startDate:
            inner_dict['start'] = self.startDate
        if self.endDate:
            inner_dict['end'] = self.endDate
        if self._obj['time_zone']:
            inner_dict['time_zone'] = self._obj['time_zone']
        return {
            f"{self._name}":
                { 'date':
                    inner_dict
                }
            }


class NPFormulaItem(NPropertyItem):
    obj_type = 'file'
    updatable = False

    def __init__(self, input_data: dict):
        super().__init__(input_data)

    def to_dict(self):
        return self._obj


class NPMultiSelectItem(NPropertyItem):
    obj_type = 'multi_select'
    updatable = True

    def __init__(self, input_data: dict):
        super().__init__(input_data)
        self._multiselect = []
        for select in self._obj:
            self._multiselect.append(select['name'])

    @property
    def multiselect(self):
        return self._multiselect

    @multiselect.setter
    def multiselect(self, value: str):
        self._multiselect.append(value)

    def clear_all_selections(self):
        self._multiselect = []

    def remove_selection(self, value: str):
        try:
            self._multiselect.remove(value)
        except ValueError as e:
            print('AN error as been encountered: ', e, f'-> where x is {value}')

    def to_dict(self):
        select_dict = []
        for m in self._multiselect:
            select_dict.append({'name': m})
        return {
            f"{self._name}": {
                'multi_select': select_dict,
            }
        }


class NPNumberItem(NPropertyItem):
    obj_type = 'number'
    updatable = True

    def __init__(self, input_data: dict):
        super().__init__(input_data)

    @property
    def number(self):
        return self._obj

    @number.setter
    def number(self, value: int | float):
        self._obj = value

    def to_dict(self):
        return {
            f"{self._name}": {
                f"number": self._obj,
            }
        }


class NPPeopleItem(NPropertyList):
    updatable = False

    def fix_list_item(self):
        for el in self.list_obj:
            if {'id': el['people']['id'], 'object': 'user'} not in self.list_fix:
                self.list_fix.append({'id': el['people']['id'], 'object': 'user'})

    def add_person(self, _id: str):
        self.list_fix.append({'id': _id, 'object': 'user'})

    def clear_person(self, _id: str):
        self.list_fix.remove({'id': _id, 'object': 'user'})


class NPPhoneNumberItem(NPropertyItem):
    obj_type = 'phone_number'
    updatable = True

    @property
    def number(self):
        return self._obj

    @number.setter
    def number(self, value: str):
        self._obj = value

    def to_dict(self):
        return {
            f"{self._name}": {
                f"phone_number": self._obj,
            }
        }


class NPRelationItem(NPropertyList):
    updatable = True

    def fix_list_item(self):
        for el in self.list_obj:
            if {'id': el['relation']['id']} not in self.list_fix:
                self.list_fix.append({'id': el['relation']['id']})

    def add_page(self, _id: str):
        self.list_fix.append({'id': _id})

    def clear_page(self, _id: str):
        self.list_fix.remove({'id': _id})


class NPRollUpItem(NPropertyList):
    obj_type = 'rollup'
    updatable = False

    def fix_list_item(self):
        pass


class NPRichTextItem(NPropertyList):
    obj_type = 'rich_text'
    updatable = True

    def __init__(self, input_data: dict):
        super().__init__(input_data)
        self.list_fix = NRichList()

    def fix_list_item(self):
        rich = NRichList()
        if isinstance(self.list_obj, list):
            for el in self.list_obj:
                rich.append(NRichText(el['rich_text']))
            self.list_fix = rich

    @property
    def text(self):
        if not self.list_fix:
            self.fix_list_item()
        return self.list_fix.text

    @text.setter
    def text(self, content: str):
        self.list_obj = content
        self.list_fix = simple_rich_text_list(content)

    def to_dict(self):
        self.fix_list_item()
        return {
            f"{self._name}": {'rich_text': self.list_fix.to_dict()},
        }


class NPSelectItem(NPropertyItem):
    obj_type = 'select'
    updatable = True

    def __init__(self, input_data: dict):
        super().__init__(input_data)
        self._select = input_data['select']['name']

    @property
    def select(self):
        return self._select

    @select.setter
    def select(self, value: str):
        self._select = value

    def to_dict(self):
        return {
            f"{self._name}": {
                'select': {
                    'name': self._select,
                },
            }
        }


class NPStatusItem(NPropertyItem):
    obj_type = 'status'
    updatable = True

    def __init__(self, input_data: dict):
        super().__init__(input_data)
        self._select = input_data['status']['name']

    @property
    def select(self):
        return self._select

    @select.setter
    def select(self, value: str):
        self._select = value

    def to_dict(self):
        return {
            f"{self._name}": {
                'status': {
                    'name': self._select,
                },
            }
        }


class NPTitleItem(NPRichTextItem):
    obj_type = 'title'
    updatable = True

    def __init__(self, input_data: dict):
        super().__init__(input_data)
        pass

    def fix_list_item(self):
        rich = NRichList()
        if isinstance(self.list_obj, list):
            for el in self.list_obj:
                rich.append(NRichText(el['title']))
            self.list_fix = rich

    @property
    def title(self):
        if not self.list_fix:
            self.fix_list_item()
        return self.list_fix.text

    @title.setter
    def title(self, value: str):
        self.list_obj = value
        self.list_fix = simple_rich_text_list(value)

    def to_dict(self):
        if not self.list_fix:
            self.fix_list_item()
        return {
            f"{self._name}": {
                'id': 'title',
                'type': 'title',
                'title': self.list_fix.to_dict()
            }
        }


class NPUrlItem(NPropertyItem):
    obj_type = 'property_item'
    updatable = True

    @property
    def url(self):
        return self._obj

    @url.setter
    def url(self, value: bool):
        self._obj = value

    def to_dict(self):
        return {
            f"{self._name}": {
                f"url": self._obj,
            }
        }


class NPUniqueIDItem(NPropertyItem):
    obj_type = 'property_item'
    updatable = False

    def __init__(self, input_data: dict):
        super().__init__(input_data)
        self._id = f"{self._obj['prefix']}- {self._obj['number']}"

    def to_dict(self):
        return self._obj