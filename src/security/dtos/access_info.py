from pydantic import BaseModel

from src.security.enums import Permissions


class AccessInfo(BaseModel):
    user_id: int
    permissions: list[Permissions]

    def has_permission(self, permission: Permissions) -> bool:
        return permission in self.permissions
