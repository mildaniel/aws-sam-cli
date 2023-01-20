"""
Interface for MapperConsumerFactory, Producer, Mapper, ListInfoPullerConsumer
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Dict, Any
from enum import Enum

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")


class DataFilter(ABC):
    @abstractmethod
    def filter_data(self, data: Dict[Any, Any], filter_string: str) -> Dict[Any, Any]:
        """

        :param data:
        :param filter_string:
        :return:
        """


class ListInfoPullerConsumer(ABC, Generic[InputType]):
    """
    Interface definition to consume and display data
    """

    @abstractmethod
    def consume(self, data: InputType):
        """
        Parameters
        ----------
        data: TypeVar
            Data for the consumer to print
        """


class Mapper(ABC, Generic[InputType, OutputType]):
    """
    Interface definition to map data to json or table
    """

    @abstractmethod
    def map(self, data: InputType, data_filter: Optional[DataFilter], filter_string: Optional[str]) -> OutputType:
        """
        Parameters
        ----------
        data: TypeVar
            Data for the mapper to map

        data_filter: Optional[DataFilter]

        filter_string: Optional[str]
            Filter the JSON output with a given filter string

        Returns
        -------
        Any
            Mapped output given the data
        """


class Producer(ABC):
    """
    Interface definition to produce data for the mappers and consumers
    """

    mapper: Mapper
    consumer: ListInfoPullerConsumer

    @abstractmethod
    def produce(self):
        """
        Produces the data for the mappers and consumers
        """


class MapperConsumerFactoryInterface(ABC):
    """
    Interface definition to create mapper-consumer factories
    """

    @abstractmethod
    def create(self, producer, output):
        """
        Parameters
        ----------
        producer: str
            A string indicating which producer is calling the function
        output: str
            A string indicating the output type

        Returns
        -------
        MapperConsumerContainer
            A container that contains a mapper and a consumer
        """


class ProducersEnum(Enum):
    STACK_OUTPUTS_PRODUCER = 1
    RESOURCES_PRODUCER = 2
    ENDPOINTS_PRODUCER = 3
