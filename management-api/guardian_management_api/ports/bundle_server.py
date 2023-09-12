from abc import abstractmethod
from enum import StrEnum
from pathlib import Path

from guardian_lib.ports import BasePort

from guardian_management_api.ports.condition import ConditionPersistencePort


class BundleType(StrEnum):
    data = "DATA"
    policies = "POLICIES"


class BundleServerPort(BasePort):
    @abstractmethod
    def get_check_interval(self) -> float:
        """
        Specifies the time in seconds to wait, before starting another loop.
        """

    @abstractmethod
    async def generate_templates(self):
        """
        Generates the template bundle at the specified location.

        :raises BundleGenerationIOError: If there are any io problems during the template creation
        """

    @abstractmethod
    async def prepare_directories(self) -> Path:
        """
        Creates all necessary directories that are required.

        Returns the path, where the generated bundles will be stored.

        :raises BundleGenerationIOError: If there are any io problems during the directory creation
        """

    @abstractmethod
    async def generate_bundles(self, cond_persistence_port: ConditionPersistencePort):
        """
        Builds the bundles if any were scheduled for creation.
        This method is called repeatedly by the application loop.

        If the Bundle Server does not get replaced by some external service:
        - Decouple from ConditionPersistencePort

        :raises BundleGenerationIOError: If there are any io problems during the bundle creation
        :raises BundleBuildError: If the subprocess to build the bundles fails
        """

    @abstractmethod
    async def schedule_bundle_build(self, bundle_type: BundleType):
        """
        Schedules a bundle of the given type to be built.
        """
