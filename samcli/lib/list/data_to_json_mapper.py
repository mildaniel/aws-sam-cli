"""
Implementation of the data to json mapper
"""
from typing import Dict
import json
from samcli.lib.list.list_interfaces import Mapper, DataFilter


class DataToJsonMapper(Mapper):
    def map(self, data: Dict[str, str], data_filter: DataFilter = None, filter_string: str = None) -> str:
        if data_filter:
            data = data_filter.filter_data(data, filter_string)
        output = json.dumps(data, indent=2)
        return output
