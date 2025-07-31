from abc import ABC, abstractmethod

from src.db.client.async_ import AsyncDatabaseClient
from src.db.client.sync import DatabaseClient
from tests.helpers.data_creator.models.clients import DBDataCreatorClientContainer


class DBDataCreatorCommandBase(ABC):

    def __init__(self,):
        self._clients: DBDataCreatorClientContainer | None = None

    def load_clients(self, clients: DBDataCreatorClientContainer):
        self._clients = clients

    @property
    def clients(self) -> DBDataCreatorClientContainer:
        if self._clients is None:
            raise Exception("Clients not loaded")
        return self._clients

    @property
    def db_client(self) -> DatabaseClient:
        return self.clients.db

    @property
    def adb_client(self) -> AsyncDatabaseClient:
        return self.clients.adb

    def run_command_sync(self, command: "DBDataCreatorCommandBase"):
        command.load_clients(self._clients)
        return command.run_sync()

    async def run_command(self, command: "DBDataCreatorCommandBase"):
        command.load_clients(self._clients)
        return await command.run()

    @abstractmethod
    async def run(self):
        raise NotImplementedError

    async def run_sync(self):
        raise NotImplementedError