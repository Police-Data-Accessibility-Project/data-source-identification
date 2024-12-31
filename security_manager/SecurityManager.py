import os
from enum import Enum
from typing import Annotated

import dotenv
import jwt
from fastapi import HTTPException, Security
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import BaseModel
from starlette import status

ALGORITHM = "HS256"

def get_secret_key():
    dotenv.load_dotenv()
    secret_key = os.getenv("SECRET_KEY")
    return secret_key

class Permissions(Enum):
    SOURCE_COLLECTOR = "source_collector"

class AccessInfo(BaseModel):
    user_id: int
    permissions: list[Permissions]

    def has_permission(self, permission: Permissions) -> bool:
        return permission in self.permissions

class SecurityManager:


    def __init__(
            self
    ):
        self.secret_key = get_secret_key()

    def validate_token(self, token: str) -> AccessInfo:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[ALGORITHM])
            return self.payload_to_access_info(payload)
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def payload_to_access_info(payload: dict) -> AccessInfo:
        user_id = payload.get("user_id")
        permissions = payload.get("permissions")
        return AccessInfo(user_id=user_id, permissions=permissions)

    @staticmethod
    def get_relevant_permissions(raw_permissions: list[str]) -> list[Permissions]:
        relevant_permissions = []
        for permission in raw_permissions:
            if permission in Permissions.__members__:
                relevant_permissions.append(Permissions[permission])
        return relevant_permissions

    def check_access(self, token: str):
        access_info = self.validate_token(token)
        if not access_info.has_permission(Permissions.SOURCE_COLLECTOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden",
            )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_access_info(
        token: Annotated[str, Depends(oauth2_scheme)]
) -> AccessInfo:
    return SecurityManager().validate_token(token)