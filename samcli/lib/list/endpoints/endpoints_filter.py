from typing import Dict, Any

from samcli.lib.list.list_interfaces import DataFilter


class EndpointsFilter(DataFilter):
    def filter_data(self, data: Dict[Any, Any], filter_string: str) -> Dict[Any, Any]:
        search_keys = self._get_search_keys(filter_string)
        logical_id = search_keys.pop(0)
        resource = self._find_resource(logical_id, data)
        search_result = self._filter_dict(search_keys, resource)
        return search_result

    @staticmethod
    def _filter_dict(search_keys, resource) -> Dict:
        while search_keys:
            key = search_keys.pop(0)
            resource = resource.get(key, {})
        return resource

    @staticmethod
    def _get_search_keys(filter_string: str):
        return filter_string.split(".")

    @staticmethod
    def _find_resource(logical_id, data):
        if not isinstance(data, list):
            raise ValueError("Change this to custom exception")

        for resource in data:
            resource_logical_id = resource.get("LogicalResourceId")
            if resource_logical_id == logical_id:
                return resource

        raise ValueError("Invalid filter, make this a custom exception")
