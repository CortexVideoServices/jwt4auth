from uuid import uuid4
from datetime import datetime, timedelta
from typing import Optional, Callable, Tuple
import jwt
from aiohttp import web
from . import abc
from .handlers import routes
from .middleware import AuthMiddleware
from .utils import bearer_token_getter, with_prefix

ACCESS_TOKEN_TTL = 5 * 60


class AuthManager(abc.AuthManager):
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
    def algorithms(self) -> str:
        """ See: `abc.AuthManager.algorithms` """
        return self.__kwargs.get('algorithms', 'HS256')

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
            token_data['exp'] = datetime.now() + timedelta(seconds=ACCESS_TOKEN_TTL)
        access_token = jwt.encode(token_data, self.secret, self.algorithms).decode('utf8')
        refresh_token = str(uuid4())
        return access_token, refresh_token

    async def create_token_pair(self, app: web.Application, username: str) -> Tuple[str, str]:
        """
        Creates access and refresh tokens for a given username. Starts user session.

        Raises:
            ValueError: if disabled or wrong username
        """
        token_data = await self.create_token_data(app, username)
        access_token, refresh_token = self._make_token_pair(token_data)
        await self.save_refresh_token(app, token_data, refresh_token)
        return access_token, refresh_token

    async def refresh_token_pair(self, app: web.Application, refresh_token: str) -> Tuple[str, str]:
        """
        Refreshes access and refresh tokens for a given refresh token.

        Raises:
            ValueError: if outdated or wrong refresh token
        """
        token_data = await self.check_refresh_token(app, refresh_token)
        access_token, refresh_token = self._make_token_pair(token_data)
        await self.save_refresh_token(app, token_data, refresh_token)
        return access_token, refresh_token
