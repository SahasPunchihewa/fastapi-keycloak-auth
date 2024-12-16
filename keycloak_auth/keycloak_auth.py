import os
import traceback
from functools import wraps
from logging import Logger, getLogger
from threading import Lock
from typing import Callable, TypeVar, List

from fastapi import HTTPException, Depends, Header
from jose import ExpiredSignatureError
from keycloak import KeycloakOpenID

T = TypeVar('T', bound=Callable)
log: Logger = getLogger(__name__)


class KeycloakAuth:
    _instance = None
    _instance_lock = Lock()
    _init_lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KeycloakAuth, cls).__new__(cls)
        return cls._instance

    def __init__(self,
                 server_url: str = os.getenv('KEYCLOAK_URL', ''),
                 client_id: str = os.getenv('KEYCLOAK_CLIENT_ID', ''),
                 realm_name: str = os.getenv('KEYCLOAK_REALM_NAME', ''),
                 client_secret_key: str = os.getenv('KEYCLOAK_CLIENT_SECRET', ''),
                 use_resource_access: bool = False):
        with self._init_lock:
            if not hasattr(self, 'initialized'):
                self.server_url = server_url
                self.client_id = client_id
                self.realm_name = realm_name
                self.client_secret_key = client_secret_key
                self.use_resource_access = use_resource_access
                self.keycloak_client: KeycloakOpenID = KeycloakOpenID(server_url=server_url,
                                                                      client_id=client_id,
                                                                      realm_name=realm_name,
                                                                      client_secret_key=client_secret_key)
                self.current_token: str = ''

    @classmethod
    def get_instance(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super(KeycloakAuth, cls).__new__(cls)
                cls._instance.__init__()
            return cls._instance

    @staticmethod
    def get_authorization_header(authorization: str | None = Header(default=None)):
        return authorization

    def get_client_token(self) -> str | None:
        try:
            token: dict = self.keycloak_client.token(grant_type='client_credentials')
            return token['access_token']
        except Exception as ex:
            log.error(f'An error occurred while getting auth token: {ex}')
            return None

    def get_user_info(self) -> dict | None:
        try:
            if self.current_token == '' or self.current_token is None:
                return None
            user: dict = self.keycloak_client.userinfo(self.current_token)
            return user
        except Exception as ex:
            log.error(f'An error occurred while getting user info: {ex}')
            return None

    def RolesAllowed(self, allowed_roles: List[str]):
        def decorator(func: T) -> T:
            @wraps(func)
            async def wrapper(*args, authorization: str = Depends(self.get_authorization_header), **kwargs):
                self.current_token = authorization.split(' ')[1] if authorization else None
                if not self.current_token:
                    raise HTTPException(status_code=401, detail='Authorization token missing')

                try:
                    decoded_token: dict = self.keycloak_client.decode_token(self.current_token)
                    user_roles = decoded_token['resource_access' if self.use_resource_access else 'realm_access'][self.client_id]['roles']
                    matching_roles = set(user_roles) & set(allowed_roles)

                    if not len(matching_roles) > 0:
                        raise HTTPException(status_code=403, detail='Insufficient permissions')
                except ExpiredSignatureError:
                    raise HTTPException(status_code=401, detail='Authorization token expired')
                except HTTPException as ex:
                    raise ex
                except Exception as ex:
                    traceback.print_exc()
                    log.error(f'An error occurred while decoding token: {ex}')
                    raise HTTPException(status_code=500, detail='Internal Server Error')

                return await func(*args, **kwargs)

            return wrapper

        return decorator
