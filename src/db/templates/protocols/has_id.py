from typing import Protocol, runtime_checkable


@runtime_checkable
class HasIDProtocol(Protocol):
    id: int