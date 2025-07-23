#######################################################
# @Project: Telemetry
# @Module: handler.py
# @Description: This module provides the base class for handling telemetry data.
# @Author: AbigailWilliams1692
# @CreationDate: 2025-07-23
#######################################################

#######################################################
# Import Libraries
#######################################################
# Standard Libraries
from abc import ABC, abstractmethod


# Third-Party Libraries

# Local Libraries

#######################################################
# Class: Handler Base
#######################################################
class Handler(ABC):
    """
    Base class for handling telemetry data.
    """

    ######################################################
    # Default Methods
    ######################################################
    def __init__(self) -> None:
        """
        Constructor for the Handler class.
        """
        super().__init__()

    def __str__(self) -> str:
        """
        Returns a string representation of the Handler instance.
        """
        return f"Handler<{id(self)}>"

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the Handler instance.
        """
        return self.__str__()

    ######################################################
    # Abstract Methods
    ######################################################
    @abstractmethod
    def export(self, records: list[dict]) -> None:
        """
        Abstract method to export telemetry records.

        :param records: List of telemetry records to export.
        :raises NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement this method.")
