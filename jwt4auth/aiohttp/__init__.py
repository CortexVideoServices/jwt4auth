import jwt4auth.general
from .handlers import routes
from .middleware import AuthMiddleware


class AuthManager(jwt4auth.general.AuthManager):
    """ Auth manager for aiohttp
    """
    routes = routes

    async def middleware(self, _, handler):
        """ aiohttp middleware """
        return AuthMiddleware(self, handler)

