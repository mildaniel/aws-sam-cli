"""
Implementation of the data to json mapper
"""
import json
from abc import ABC
from typing import Dict, Optional, TypeVar

from jmespath import search

from samcli.commands.list.exceptions import ListQueryError
from samcli.lib.list.list_interfaces import Mapper

KT = TypeVar("KT")


class DataToJsonMapper(Mapper):
    def map(self, data: Dict[str, str], query: Optional[str] = None) -> str:
        if query:
            return self._filter_output(data, query)
        output = json.dumps(data, indent=2)
        return output

    @staticmethod
    def _filter_output(data: Dict[str, str], query: str) -> str:
        response = search(query, data)
        response_filter = response_filter_factory(response)
        return response_filter.filter_response(response)


class ResponseFilter(ABC):
    def filter_response(self, value: KT) -> str:
        """
        The jmespath search can return various types that need to be handled accordingly
        """


class DictResponseFilter(ResponseFilter):
    def filter_response(self, value: dict) -> str:
        return json.dumps(value)


class ListResponseFilter(ResponseFilter):
    def filter_response(self, value: list) -> str:
        if len(value) == 1 and (isinstance(value[0], str) or isinstance(value[0], int)):
            return str(value[0])
        return json.dumps(value)


class StringResponseFilter(ResponseFilter):
    def filter_response(self, value: str) -> str:
        return value


class OtherResponseFilter(ResponseFilter):
    def filter_response(self, value: KT) -> str:
        try:
            return str(value)
        except (ValueError, TypeError):
            raise ListQueryError("Unable to parse the query results.")


def response_filter_factory(response):
    if isinstance(response, dict):
        return DictResponseFilter()
    if isinstance(response, list):
        return ListResponseFilter()
    if isinstance(response, str):
        return StringResponseFilter()
    return OtherResponseFilter()
