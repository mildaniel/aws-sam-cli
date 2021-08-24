"""
Provide IAC Plugins Interface && Project representation
"""

import abc
from collections import OrderedDict
from collections.abc import Callable, Mapping, MutableMapping
from copy import deepcopy
from enum import Enum
from typing import List, Any, Dict, Iterator, Optional
from uuid import uuid4
import click
import logging

from samcli.commands._utils.resources import (
    AWS_LAMBDA_FUNCTION,
    AWS_SERVERLESS_FUNCTION,
    RESOURCES_WITH_IMAGE_COMPONENT,
    RESOURCES_WITH_LOCAL_PATHS,
    NESTED_STACKS_RESOURCES,
)
from samcli.lib.utils.packagetype import IMAGE, ZIP

# pylint: disable=R0801
LOG = logging.getLogger(__name__)


# pylint: disable=R0801
class Environment:
    def __init__(self, region: Optional[str] = None, account_id: Optional[str] = None):
        self._region = region
        self._account_id = account_id

    @property
    def region(self) -> Optional[str]:
        return self._region

    @region.setter
    def region(self, region: str) -> None:
        self._region = region

    @property
    def account_id(self) -> Optional[str]:
        return self._account_id

    @account_id.setter
    def account_id(self, account_id: str) -> None:
        self._account_id = account_id


# pylint: disable=R0801
class Destination:
    def __init__(self, path: str, value: Any):
        self._path = path
        self._value = value

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path: str) -> None:
        self._path = path

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value = value


# pylint: disable=R0801
class Asset:
    def __init__(
        self,
        asset_id: Optional[str] = None,
        destinations: Optional[List[Destination]] = None,
        source_property: Optional[str] = None,
        extra_details: Optional[Dict[str, Any]] = None,
    ):
        if asset_id is None:
            asset_id = str(uuid4())
        self._asset_id = asset_id
        if destinations is None:
            destinations = []
        self._destinations = destinations
        self._source_property = source_property
        extra_details = extra_details or {}
        self._extra_details = extra_details

    @property
    def asset_id(self) -> str:
        return self._asset_id

    @asset_id.setter
    def asset_id(self, asset_id: str) -> None:
        self._asset_id = asset_id

    @property
    def destinations(self) -> List[Destination]:
        return self._destinations

    @destinations.setter
    def destinations(self, destinations: List[Destination]) -> None:
        self._destinations = destinations

    @property
    def source_property(self) -> Optional[str]:
        return self._source_property

    @source_property.setter
    def source_property(self, source_property: str) -> None:
        self._source_property = source_property

    @property
    def extra_details(self) -> Dict[str, Any]:
        return self._extra_details

    @extra_details.setter
    def extra_details(self, extra_details: Dict[str, Any]) -> None:
        self._extra_details = extra_details


# pylint: disable=R0801
class S3Asset(Asset):
    """
    Represent the S3 Assets.
    Can Represent Implicit asset for resources like Lambda Function, or explicit for added assets like HTML folders
    """

    def __init__(
        self,
        asset_id: Optional[str] = None,
        bucket_name: Optional[str] = None,
        object_key: Optional[str] = None,
        object_version: Optional[str] = None,
        source_path: Optional[str] = None,
        updated_source_path: Optional[str] = None,
        destinations: Optional[List[Destination]] = None,
        source_property: Optional[str] = None,
        extra_details: Optional[Dict[str, Any]] = None,
    ):
        self._bucket_name = bucket_name
        self._object_key = object_key
        self._object_version = object_version
        self._source_path = source_path
        self._updated_source_path = updated_source_path
        super().__init__(asset_id, destinations, source_property, extra_details)

    @property
    def bucket_name(self) -> Optional[str]:
        return self._bucket_name

    @bucket_name.setter
    def bucket_name(self, bucket_name: str) -> Optional[None]:
        self._bucket_name = bucket_name

    @property
    def object_key(self) -> Optional[str]:
        return self._object_key

    @object_key.setter
    def object_key(self, object_key: str) -> None:
        self._object_key = object_key

    @property
    def object_version(self) -> Optional[str]:
        return self._object_version

    @object_version.setter
    def object_version(self, object_version: str) -> None:
        self._object_version = object_version

    @property
    def source_path(self) -> Optional[str]:
        return self._source_path

    @source_path.setter
    def source_path(self, source_path: str) -> None:
        self._source_path = source_path

    @property
    def updated_source_path(self) -> Optional[str]:
        return self._updated_source_path

    @updated_source_path.setter
    def updated_source_path(self, updated_source_path: str) -> None:
        self._updated_source_path = updated_source_path


# pylint: disable=R0801
class ImageAsset(Asset):
    """
    Represent the Container Assets.
    """

    def __init__(
        self,
        asset_id: Optional[str] = None,
        repository_name: Optional[str] = None,
        registry: Optional[str] = None,
        image_tag: Optional[str] = None,
        source_local_image: Optional[str] = None,
        source_path: Optional[str] = None,
        docker_file_name: Optional[str] = None,
        build_args: Optional[Dict[str, str]] = None,
        destinations: Optional[List[Destination]] = None,
        source_property: Optional[str] = None,
        target: Optional[str] = None,
        extra_details: Optional[Dict[str, Any]] = None,
    ):
        """
        image uri = <registry>/repository_name:image_tag
        registry = aws_account_id.dkr.ecr.us-west-2.amazonaws.com
        """
        self._repository_name = repository_name
        self._registry = registry
        self._image_tag = image_tag
        self._source_local_image = source_local_image
        self._source_path = source_path
        self._docker_file_name = docker_file_name
        self._build_args = build_args
        self._target = target
        super().__init__(asset_id, destinations, source_property, extra_details)

    @property
    def repository_name(self) -> Optional[str]:
        return self._repository_name

    @repository_name.setter
    def repository_name(self, repository_name: str) -> None:
        self._repository_name = repository_name

    @property
    def target(self) -> Optional[str]:
        return self._target

    @target.setter
    def target(self, target: str) -> None:
        self._target = target

    @property
    def build_args(self) -> Optional[Dict[str, str]]:
        return self._build_args

    @build_args.setter
    def build_args(self, build_args: Dict[str, str]) -> None:
        self._build_args = build_args

    @property
    def registry(self) -> Optional[str]:
        return self._registry

    @registry.setter
    def registry(self, registry: str) -> None:
        self._registry = registry

    @property
    def image_tag(self) -> Optional[str]:
        return self._image_tag

    @image_tag.setter
    def image_tag(self, image_tag: str) -> None:
        self._image_tag = image_tag

    @property
    def source_local_image(self) -> Optional[str]:
        return self._source_local_image

    @source_local_image.setter
    def source_local_image(self, source_local_image: str) -> None:
        self._source_local_image = source_local_image

    @property
    def source_path(self) -> Optional[str]:
        return self._source_path

    @source_path.setter
    def source_path(self, source_path: str) -> None:
        self._source_path = source_path

    @property
    def docker_file_name(self) -> Optional[str]:
        return self._docker_file_name

    @docker_file_name.setter
    def docker_file_name(self, docker_file_name: str) -> None:
        self._docker_file_name = docker_file_name


# pylint: disable=R0801
class SectionItem:
    def __init__(
        self,
        key: Optional[str] = None,
        item_id: Optional[str] = None,
    ):
        self._key = key
        self._item_id = item_id

    @property
    def key(self) -> Optional[str]:
        return self._key

    @key.setter
    def key(self, key: str) -> None:
        self._key = key

    @property
    def item_id(self) -> Optional[str]:
        return self._item_id or self._key

    @item_id.setter
    def item_id(self, item_id: str) -> None:
        self._item_id = item_id


# pylint: disable=R0801
class SimpleSectionItem(SectionItem):
    def __init__(
        self,
        key: Optional[str] = None,
        item_id: Optional[str] = None,
        value: Any = None,
    ):
        super().__init__(key, item_id)
        self._value = value

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value = value

    def __bool__(self):
        return bool(self._value)


# pylint: disable=R0801
# pylint: disable=R0901
class DictSectionItem(SectionItem, MutableMapping, OrderedDict):
    def __init__(
        self,
        key: Optional[str] = None,
        item_id: Optional[str] = None,
        body: Any = None,
        assets: Optional[List[Asset]] = None,
        extra_details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(key, item_id)
        self._body = body or {}
        if assets is None:
            assets = []
        self._assets = assets
        extra_details = extra_details or {}
        self._extra_details = extra_details

    def copy(self) -> "DictSectionItem":
        return deepcopy(self)

    @property
    def body(self) -> Any:
        return self._body

    @property
    def assets(self) -> List[Asset]:
        return self._assets

    @assets.setter
    def assets(self, assets: List[Asset]) -> None:
        self._assets = assets

    @property
    def extra_details(self) -> Dict[str, Any]:
        return self._extra_details

    @extra_details.setter
    def extra_details(self, extra_details: Dict[str, Any]) -> None:
        self._extra_details = extra_details

    def is_packageable(self):
        """
        return if the resource is packageable
        """
        return bool(self.assets)

    def find_asset_by_source_property(self, source_property: str) -> Optional[Asset]:
        if not self.assets:
            return None
        for asset in self.assets:
            if asset.source_property == source_property:
                return asset
        return None

    def __setitem__(self, k: str, v: Any) -> None:
        self._body[k] = v

    def __delitem__(self, v: str) -> None:
        del self._body[v]

    def __getitem__(self, k: str) -> Any:
        return self._body[k]

    def __len__(self) -> int:
        return len(self._body)

    def __iter__(self) -> Iterator:
        return iter(self._body)

    def __bool__(self):
        return bool(self._body)


# pylint: disable=R0801
class Section:
    def __init__(self, section_name: Optional[str] = None):
        self._section_name = section_name

    @property
    def section_name(self) -> Optional[str]:
        return self._section_name


# pylint: disable=R0801
class SimpleSection(Section):
    def __init__(self, section_name: str, value: Any = None):
        self._value = value
        super().__init__(section_name)

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value = value

    def __bool__(self):
        return bool(self._value)


# pylint: disable=R0801
# pylint: disable=R0901
class DictSection(Section, MutableMapping, OrderedDict):
    def __init__(self, section_name: Optional[str] = None, items: Optional[List[SectionItem]] = None):
        self._items_dict = OrderedDict()
        if items:
            for item in items:
                self._items_dict[item.key] = item
        super().__init__(section_name)

    def copy(self) -> "DictSection":
        return deepcopy(self)

    @property
    def section_items(self) -> List[DictSectionItem]:
        return list(self._items_dict.values())

    def __setitem__(self, k: str, v: Any) -> None:
        if isinstance(v, DictSectionItem):
            self._items_dict[k] = v
        elif isinstance(v, Mapping):
            section_item_classes = {
                "Resources": Resource,
                "Parameters": Parameter,
            }
            item_class = section_item_classes.get(self._section_name, DictSectionItem)
            item = item_class(key=k, body=v)
            self._items_dict[k] = item
        else:
            self._items_dict[k] = SimpleSectionItem(key=k, value=v)

    def __delitem__(self, v: str) -> None:
        del self._items_dict[v]

    def __getitem__(self, k: str) -> DictSectionItem:
        v = self._items_dict[k]
        if isinstance(v, SimpleSectionItem):
            return v.value
        return v

    def __len__(self) -> int:
        return len(self._items_dict)

    def __iter__(self) -> Iterator:
        return iter(self._items_dict)

    def __bool__(self):
        return bool(self._items_dict)


# pylint: disable=R0801
class Resource(DictSectionItem):
    """
    Represents one resource in Resources section in a template
    """

    def __init__(
        self,
        key: Optional[str] = None,
        item_id: Optional[str] = None,
        body: Any = None,
        assets: Optional[List[Asset]] = None,
        nested_stack: Optional["Stack"] = None,
        extra_details: Optional[Dict[str, Any]] = None,
    ):
        self._nested_stack = nested_stack
        super().__init__(key, item_id, body, assets, extra_details)

    def copy(self):
        return deepcopy(self)

    @property
    def nested_stack(self) -> Optional["Stack"]:
        return self._nested_stack

    @nested_stack.setter
    def nested_stack(self, nested_stack: "Stack") -> None:
        self._nested_stack = nested_stack

    def is_packageable(self):
        """
        return if the resource is packageable
        NOTE: we probably want to include a condition to check if the resource is binded to a local asset
        But in samcli.lib.package.utils.upload_local_artifacts, we handle a case where local_path is None,
        we would build the parent_dir. This seems to only apply for CFN/SAM project, we can consider to move
        that logic to CfnIacPlugin. For now, just keep it as is.
        """
        if "InlineCode" in self.get("Properties", {}):
            return False
        resource_type = self.get("Type", None)
        packageable_resources = [
            NESTED_STACKS_RESOURCES,
            RESOURCES_WITH_LOCAL_PATHS,
            RESOURCES_WITH_IMAGE_COMPONENT,
        ]
        return any(resource_type in p for p in packageable_resources)


# pylint: disable=R0801
class Parameter(DictSectionItem):
    """
    Represents 1 Parameters in Parameters section in a template
    """

    def __init__(
        self,
        key: Optional[str] = None,
        item_id: Optional[str] = None,
        body: Any = None,
        added_by_iac: bool = False,
        assets: Optional[List[Asset]] = None,
        extra_details: Optional[Dict[str, Any]] = None,
    ):
        self._added_by_iac = added_by_iac
        super().__init__(key, item_id, body, assets, extra_details)

    def copy(self) -> "Resource":
        return deepcopy(self)

    @property
    def added_by_iac(self) -> bool:
        return self._added_by_iac

    @added_by_iac.setter
    def added_by_iac(self, added_by_iac: bool) -> None:
        self._added_by_iac = added_by_iac


# pylint: disable=R0801
# pylint: disable=R0901
class Stack(MutableMapping, OrderedDict):
    """
    Represents IaC Stack
    """

    def __init__(
        self,
        stack_id: Optional[str] = None,
        name: Optional[str] = None,
        origin_dir: Optional[str] = None,
        is_nested: bool = False,
        sections: Optional[Dict[str, Section]] = None,
        assets: Optional[List[Asset]] = None,
        environments: Optional[List[Environment]] = None,
        extra_details: Optional[Dict[str, Any]] = None,
    ):
        self._stack_id = stack_id
        self._name = name
        self._is_nested = is_nested
        self._origin_dir = origin_dir or "."
        if sections is None:
            sections = OrderedDict()
        self._sections = sections
        if assets is None:
            assets = []
        self._assets = assets
        if environments is None:
            environments = []
        self._environments = environments
        if extra_details is None:
            extra_details = {}
        self._extra_details = extra_details
        super().__init__()

    def copy(self) -> "Stack":
        return deepcopy(self)

    @property
    def stack_id(self) -> Optional[str]:
        return self._stack_id or self.name

    @stack_id.setter
    def stack_id(self, stack_id: str) -> None:
        self._stack_id = stack_id

    @property
    def name(self) -> str:
        return self._name or ""

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def origin_dir(self) -> str:
        return self._origin_dir

    @origin_dir.setter
    def origin_dir(self, origin_dir: str) -> None:
        self._origin_dir = origin_dir

    @property
    def is_nested(self) -> bool:
        return self._is_nested

    @is_nested.setter
    def is_nested(self, is_nested: bool) -> None:
        self._is_nested = is_nested

    @property
    def sections(self) -> Dict[str, Section]:
        return self._sections

    @property
    def assets(self) -> Optional[List[Asset]]:
        return self._assets

    @assets.setter
    def assets(self, assets: List[Asset]) -> None:
        self._assets = assets

    @property
    def environments(self) -> Optional[List[Environment]]:
        return self._environments

    @environments.setter
    def environments(self, environments: List[Environment]) -> None:
        self._environments = environments

    @property
    def extra_details(self) -> Dict[str, Any]:
        return self._extra_details

    @extra_details.setter
    def extra_details(self, extra_details: Dict[str, Any]) -> None:
        self._extra_details = extra_details

    def has_assets_of_package_type(self, package_type: str) -> bool:
        package_type_to_asset_cls_map = {
            ZIP: S3Asset,
            IMAGE: ImageAsset,
        }
        return any(isinstance(asset, package_type_to_asset_cls_map[package_type]) for asset in self.assets)

    def find_function_resources_of_package_type(self, package_type: str) -> List[Resource]:
        package_type_to_asset_cls_map = {
            ZIP: S3Asset,
            IMAGE: ImageAsset,
        }
        _function_resources = []
        for _, resource in self.get("Resources", DictSection()).items():
            if (
                resource.get("Type", "") in [AWS_SERVERLESS_FUNCTION, AWS_LAMBDA_FUNCTION]
                and resource.assets
                and isinstance(resource.assets[0], package_type_to_asset_cls_map[package_type])
            ):
                _function_resources.append(resource)
        return _function_resources

    def get_overrideable_parameters(self):
        """
        Return a dict of parameters that are override-able, i.e. not added by iac
        """
        return {key: val for key, val in self.get("Parameters", {}).items() if not val.added_by_iac}

    def as_dict(self):
        """
        return the stack as a dict for JSON serialization
        """
        return _make_dict(self)

    def __setitem__(self, k: str, v: Any) -> None:
        if isinstance(v, dict):
            section = DictSection(section_name=k)
            for key in v.keys():
                section[key] = v[key]
            self._sections[k] = section
        elif isinstance(v, Section):
            self._sections[k] = v
        else:
            self._sections[k] = SimpleSection(k, v)

    def __delitem__(self, v: str) -> None:
        del self._sections[v]

    def __getitem__(self, k: str) -> Section:
        v = self._sections[k]
        if isinstance(v, SimpleSection):
            return v.value
        return v

    def __len__(self) -> int:
        return len(self._sections)

    def __iter__(self) -> Iterator:
        return iter(self._sections)

    def __bool__(self):
        return bool(self._sections)


class SamCliProject:
    """
    Class represents the Project data that will be returned by the IaC plugins
    Project:
        environments List[Environment]
        stacks List[Stack]
    """

    def __init__(self, stacks: List[Stack], extra_details: Optional[Dict[str, Any]] = None):
        self._stacks = stacks or []
        self._extra_details = extra_details or {}

    @property
    def stacks(self) -> List[Stack]:
        return self._stacks

    @stacks.setter
    def stacks(self, stacks: List[Stack]) -> None:
        self._stacks = stacks

    @property
    def default_stack(self) -> Optional[Stack]:
        if len(self._stacks) > 0:
            return self._stacks[0]
        return None

    @property
    def extra_details(self) -> Optional[Dict[str, Any]]:
        return self._extra_details

    @extra_details.setter
    def extra_details(self, extra_details: Dict[str, Any]) -> None:
        self._extra_details = extra_details

    def find_stack_by_name(self, name: str):
        for stack in self.stacks:
            if stack.name == name:
                return stack
        return None


# pylint: disable=R0801
class LookupPathType(Enum):
    SOURCE = "Source"
    BUILD = "BUILD"


# pylint: disable=R0801
class ProjectTypes(Enum):
    CFN = "CFN"
    CDK = "CDK"


# pylint: disable=R0801
class LookupPath:
    def __init__(self, lookup_path_dir: str, lookup_path_type: LookupPathType = LookupPathType.BUILD):
        self._lookup_path_dir = lookup_path_dir
        self._lookup_path_type = lookup_path_type

    @property
    def lookup_path_dir(self) -> str:
        return self._lookup_path_dir

    @lookup_path_dir.setter
    def lookup_path_dir(self, lookup_path_dir: str) -> None:
        self._lookup_path_dir = lookup_path_dir

    @property
    def lookup_path_type(self) -> LookupPathType:
        return self._lookup_path_type

    @lookup_path_type.setter
    def lookup_path_type(self, lookup_path_type: LookupPathType) -> None:
        self._lookup_path_type = lookup_path_type


class ProjectFindRule:
    @abc.abstractmethod
    @property
    def file_rules(self) -> List[str]:
        """
        a list of regex to filter the file names or suffixes
        """

    @abc.abstractmethod
    @property
    def content_rules(self) -> Dict[str, str]:
        """
        regex to filter the file context. Key is the regex of filename
        Value is file content filter with regex.
        """


class PluginContext:
    def __init__(self, context: Dict[str, Any]):
        self._context = context

    @property
    def context_map(self):
        """
        the context retrieved from command line, its key is the command line option
        name, value is corresponding input
        """
        return self._context


class IaCPluginInterface(metaclass=abc.ABCMeta):
    """
    Interface for an IaC Plugin
    We only require two methods here - get_project and write_project
    """

    def __init__(self, context: PluginContext):
        self._context = context

    @abc.abstractmethod
    def read_project(self, lookup_paths: List[str]) -> SamCliProject:
        """
        Read and parse template of that IaC Platform
        """
        raise NotImplementedError

    @abc.abstractmethod
    def write_project(self, project: SamCliProject, build_dir: str) -> bool:
        """
        Write project to a template (or a set of templates),
        move the template(s) to build_path
        return true if it's successful
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update_packaged_locations(self, stack: Stack) -> bool:
        """
        update the locations of assets inside a stack after sam packaging
        return true if it's successful
        """
        raise NotImplementedError


class IaCPluginDefinition:
    def __init__(
        self,
        plugin_name: str,
        plugin_creator: Callable[IaCPluginInterface],
        plugin_detector: ProjectFindRule,
        additional_options: List[click.option],
    ):
        self._plugin_name = plugin_name
        self._plugin_creator = plugin_creator
        self._project_detector = plugin_detector
        self._additional_options = additional_options

    def create_plugin(self, context: PluginContext) -> IaCPluginInterface:
        """
        factory method to use plugin_creator function to instantiate an IaCPluginInterface object.
        """
        return self._plugin_creator(context)

    @abc.abstractmethod
    def project_detected(self, path: str) -> bool:
        """
        use the defined project_detector function to detect the type of a project
        return true if a valid project is detected
        """
        raise NotImplementedError

    @abc.abstractmethod
    def valid_context(self, options: List[click.option]) -> bool:
        """
        validate the options from command line
        return true if the command line options are valid for the given project type
        """
        raise NotImplementedError


# pylint: disable=R0801
def _make_dict(obj):
    if not isinstance(obj, MutableMapping):
        return obj
    to_return = dict()
    for key, val in obj.items():
        to_return[key] = _make_dict(val)
    return to_return
