
from datetime import datetime

class NDate:
    def __init__(self, data: str | datetime):
        if isinstance(data, str):
            self.data = self._crate_data_object(data)
        else:
            self.data = self._create_data_string(data)

    @staticmethod
    def _crate_data_object(data: str) -> datetime:
        return datetime.fromisoformat(data.replace("Z", "+00:00"))

    @staticmethod
    def _create_data_string(data: datetime) -> str:
        return data.isoformat(timespec="milliseconds").replace("+00:00", "Z")

    def __repr__(self):
        return f"{self.data}"


if __name__ == '__main__':
    cr_by = NDate("2022-03-01T19:05:00.000Z")
    print(cr_by, type(cr_by.data))
    lu_date = NDate(cr_by.data)
    print(lu_date, type(lu_date.data))
    pass