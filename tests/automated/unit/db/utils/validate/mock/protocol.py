from asyncio import Protocol


class MockProtocol(Protocol):

    def mock_method(self) -> None:
        pass