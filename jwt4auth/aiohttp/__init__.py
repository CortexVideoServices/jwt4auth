from abc import ABC
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from typing import Optional, Callable, Tuple, Dict
import jwt
from aiohttp import web
from . import abc
from .handlers import routes
from .middleware import AuthMiddleware
from .utils import bearer_token_getter, with_prefix

ACCESS_TOKEN_TTL = 5 * 60
JWT_SECURE_ALGORITHM = 'HS256'


class AuthManager(abc.AuthManager, ABC):
    """ Auth manager for aiohttp
    """

    routes = routes

    def __init__(self, secret, **kwargs):
        self.__secret = secret
        self.__kwargs = kwargs

    @property
    def secret(self) -> str:
        """ See: `abc.AuthManager.secret` """
        return self.__secret

    @property
    def algorithm(self) -> str:
        """ See: `abc.AuthManager.algorithm` """
        return self.__kwargs.get('algorithm', JWT_SECURE_ALGORITHM)

    @property
    def access_token_ttl(self) -> int:
        """ See: `abc.AuthManager.access_token_ttl` """
        return self.__kwargs.get('access_token_ttl', ACCESS_TOKEN_TTL)

    @property
    def use_cookie(self) -> Optional[str]:
        """ See: `abc.AuthManager.use_cookie` """
        return self.__kwargs.get('use_cookie')

    @property
    def token_getter(self) -> Optional[Callable[[web.Request, ], Optional[str]]]:
        """ See: `abc.AuthManager.token_getter` """
        return self.__kwargs.get('token_getter', bearer_token_getter)

    async def middleware(self, _, handler):
        """ aiohttp middleware """
        return AuthMiddleware(self, handler)

    def _make_token_pair(self, token_data):
        if 'exp' not in token_data:
            token_data['exp'] = datetime.now(timezone.utc) + timedelta(seconds=self.access_token_ttl)
        access_token = jwt.encode(token_data, self.secret, self.algorithm).decode('utf8')
        refresh_token = str(uuid4())
        return access_token, refresh_token

    async def create_token_pair(self, app: web.Application, token_data: Dict) -> Tuple[str, str]:
        """
        Creates access and refresh tokens for a given token_data. Starts user session.

        Raises:
            ValueError: if disabled or wrong username
        """
        access_token, refresh_token = self._make_token_pair(token_data)
        await self.save_refresh_token(app, token_data, refresh_token)
        return access_token, refresh_token
