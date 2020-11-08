from abc import ABC, abstractmethod
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Union
import jwt

ACCESS_TOKEN_TTL = 5 * 60
JWT_SECURE_ALGORITHM = 'HS256'


class AuthManager(ABC):
    """ Auth manager for async web framework
    """

    def __init__(self, secret, **kwargs):
        self.__secret = secret
        self.__kwargs = kwargs

    @property
    def secret(self) -> str:
        """ JWT decode key """
        return self.__secret

    @property
    def algorithm(self) -> str:
        """ JWT secure algorithm """
        return self.__kwargs.get('algorithm', JWT_SECURE_ALGORITHM)

    @property
    def access_token_ttl(self) -> int:
        """ Access token TTL, secs """
        return self.__kwargs.get('access_token_ttl', ACCESS_TOKEN_TTL)

    @property
    def use_cookie(self) -> Optional[str]:
        """ Cookie name that be used to store the access token.
        If a value is None, cookies will not be used.
        """
        return self.__kwargs.get('use_cookie', 'jwt4auh')

    async def create_tokens(self, username: Union[int, str]) -> Tuple[str, Dict, str]:
        """
        Creates access, token_data and refresh tokens for a given username. Starts user session.
        """
        token_data = {'user_data': await self.create_user_data(username),
                      'username': username,
                      'exp': datetime.now(timezone.utc) + timedelta(seconds=self.access_token_ttl)}
        if token_data:
            access_token = jwt.encode(token_data, self.secret, self.algorithm)
            refresh_token = str(uuid4())
            if not await self.save_refresh_token(token_data['username'], refresh_token):
                raise RuntimeError('Cannot save refresh token')
            return access_token, token_data, refresh_token
        raise RuntimeError('Cannot create token data')

    @abstractmethod
    async def check_credential(self, username: str, password: str) -> bool:
        """
        Checks user credentials and return True or False.
        """

    @abstractmethod
    async def create_user_data(self, username: Union[int, str]) -> Optional[Dict]:
        """
        Creates and returns token data for a given username(userId).
        """

    @abstractmethod
    async def save_refresh_token(self, username: str, refresh_token: str) -> bool:
        """
        Save refresh token related with a given username. Starts user session.
        """

    @abstractmethod
    async def check_refresh_token(self, refresh_token: str) -> Optional[Union[int, str]]:
        """
        Checks refresh a token and returns related username(userId) if if valid.
        """

    @abstractmethod
    async def reset_refresh_token(self, username: str) -> bool:
        """
        Reset refresh token related with a given username. End of user session.
        """
