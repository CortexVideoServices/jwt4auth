from uuid import uuid4
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from typing import Optional, Union, Dict, Tuple
import jwt


class AuthManager(ABC):
    """ Auth manager for async web framework
    """

    def __init__(self, secret: str, *,
                 algorithm: str = 'HS256',
                 access_token_ttl: int = 300,
                 use_cookie: Optional[str] = 'jwt4auth'):
        self.__secret = secret
        self.__algorithm = algorithm
        self.__access_token_ttl = access_token_ttl
        self.__use_cookie = use_cookie

    @property
    def secret(self) -> str:
        """ JWT decode key """
        return self.__secret

    @property
    def algorithm(self) -> str:
        """ JWT secure algorithm """
        return self.__algorithm

    @property
    def access_token_ttl(self) -> int:
        """ Access token TTL, secs """
        return self.__access_token_ttl

    @property
    def use_cookie(self) -> Optional[str]:
        """
        Cookie name that be used to store the access token.
        If a value is None, cookies will not be used.
        """
        return self.__use_cookie

    async def create_token_pair(self, user_data: Dict) -> Tuple[str, str]:
        """ Creates access, token_data and refresh tokens for a given username. Starts user session. """
        token_data = {'user_data': user_data,
                      'exp': datetime.now(timezone.utc) + timedelta(seconds=self.access_token_ttl)}
        if token_data:
            access_token = jwt.encode(token_data, self.secret, self.algorithm).decode('utf8')
            refresh_token = str(uuid4())
            if not await self.save_refresh_token(user_data, refresh_token):
                raise RuntimeError('Cannot save refresh token')
            return access_token, refresh_token
        raise RuntimeError('Cannot create token pair')

    def check_access_token(self, access_token: str, *, verify_exp=True) -> Dict:
        """ Checks access token and returns user data. """
        token_data = jwt.decode(access_token, self.secret,
                                algorithms=self.algorithm, options={'verify_exp': verify_exp})
        return token_data['user_data']

    @abstractmethod
    async def check_credential(self, username: str, password: str) -> bool:
        """ Checks user credentials and return True or False. """

    @abstractmethod
    async def get_user_data(self, username: Union[int, str]) -> Optional[Dict]:
        """ Gets user data for a given username (userId). """

    @abstractmethod
    async def save_refresh_token(self, user_data: Dict, refresh_token: str) -> bool:
        """ Save refresh token related with a given user data. Starts user session. """

    @abstractmethod
    async def check_refresh_token(self, user_data: Dict, refresh_token: str) -> bool:
        """ Checks refresh token related with a given user data. Continue user session """

    @abstractmethod
    async def reset_refresh_token(self, user_data: Dict) -> bool:
        """ Reset refresh token related with a given user data. End of user session. """