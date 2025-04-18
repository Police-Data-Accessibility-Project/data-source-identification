import os
from enum import Enum
from typing import Annotated

import dotenv
import jwt
from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import BaseModel
from starlette import status

ALGORITHM = "HS256"

def get_secret_key():
    dotenv.load_dotenv()
    secret_key = os.getenv("DS_APP_SECRET_KEY")
    return secret_key

class Permissions(Enum):
    SOURCE_COLLECTOR = "source_collector"
    SOURCE_COLLECTOR_FINAL_REVIEW = "source_collector_final_review"

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
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def payload_to_access_info(self, payload: dict) -> AccessInfo:
        user_id = int(payload.get("sub"))
        raw_permissions = payload.get("permissions")
        permissions = self.get_relevant_permissions(raw_permissions)
        return AccessInfo(user_id=user_id, permissions=permissions)

    @staticmethod
    def get_relevant_permissions(raw_permissions: list[str]) -> list[Permissions]:
        relevant_permissions = []
        for raw_permission in raw_permissions:
            try:
                permission = Permissions(raw_permission)
                relevant_permissions.append(permission)
            except ValueError:
                continue
        return relevant_permissions

    def check_access(
            self,
            token: str,
            permission: Permissions
    ) -> AccessInfo:
        access_info = self.validate_token(token)
        if not access_info.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden",
            )
        return access_info


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_access_info(
        token: Annotated[str, Depends(oauth2_scheme)]
) -> AccessInfo:
    return SecurityManager().check_access(token, Permissions.SOURCE_COLLECTOR)

def require_permission(permission: Permissions):
    def dependency(token: Annotated[str, Depends(oauth2_scheme)]) -> AccessInfo:
        return SecurityManager().check_access(token, permission=permission)
    return dependency