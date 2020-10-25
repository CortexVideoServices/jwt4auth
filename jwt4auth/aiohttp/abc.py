from abc import ABC, abstractmethod
from typing import Optional, Callable, Tuple, Dict
from aiohttp import web


class AuthManager(ABC):
    """
    Interface of auth manager for aiohttp
    """

    @property
    @abstractmethod
    def secret(self) -> str:
        """
        JWT decode key
        """

    @property
    @abstractmethod
    def algorithms(self) -> str:
        """
        JWT key algorithms
        """

    @property
    @abstractmethod
    def use_cookie(self) -> Optional[str]:
        """
        Cookie name that be used to store the access token.
        If a value is None, cookies will not be used.
        """

    @property
    @abstractmethod
    def token_getter(self) -> Optional[Callable[[web.Request, ], Optional[str]]]:
        """
        Second method of getting the access token is used if the cookie method not available.
        """

    @abstractmethod
    async def check_credential(self, app: web.Application, username: str, password: str) -> bool:
        """
        Checks user credentials and return True or False.
        """

    @abstractmethod
    async def create_token_pair(self, app: web.Application, username: str) -> Tuple[str, str]:
        """
        Creates access and refresh tokens for a given username.

        Raises:
            ValueError: if disabled or wrong username
        """

    @abstractmethod
    async def create_token_data(self, app: web.Application, username: str) -> Dict:
        """
        Creates token data for a given username.

        Raises:
            ValueError: if disabled or wrong username
        """

    @abstractmethod
    async def refresh_token_pair(self, app: web.Application, refresh_token: str) -> Tuple[str, str]:
        """
        Refreshes access and refresh tokens for a given refresh token.

        Raises:
            ValueError: if outdated or wrong refresh token
        """

    @abstractmethod
    async def save_refresh_token(self, app: web.Application, token_data: Dict, refresh_token: str):
        """
        Save refresh token and relates it with a given token data. Starts user session.
        """

    @abstractmethod
    async def check_refresh_token(self, app: web.Application, refresh_token: str) -> Dict:
        """
        Checks refresh a token and returns related token data if if valid.

        Raises:
            ValueError: if outdated or wrong refresh token
        """

    @abstractmethod
    async def reset_refresh_token(self, app: web.Application, token_data: Dict):
        """
        Reset refresh token related with  a given token data. End of user session.
        """
