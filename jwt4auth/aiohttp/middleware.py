from typing import Optional
import jwt
from aiohttp import web
from .abc import AuthManager
from .handlers import refresh, logoff


class AuthMiddleware(object):
    """ aiohttp middleware that works with auth manager
    """

    def __init__(self, auth_manager: AuthManager, handler):
        self.auth_manager = auth_manager
        self.handler = handler

    async def __call__(self, request: web.Request):
        if 'authorization_rules' not in request:
            return await self.handler(request)  # type: web.Response
        access_token = await self._get_token(request)
        try:
            token_data = None if not access_token else jwt.decode(
                access_token,
                self.auth_manager.secret,
                algorithms=self.auth_manager.algorithms,
                options={'verify_exp': self.handler != refresh}
            )
        except jwt.InvalidTokenError:
            raise web.HTTPUnauthorized(reason="Invalid or outdated access token")
        if token_data is None:
            raise web.HTTPUnauthorized(reason="Authentication required")
        await self._check_authorization_rules(request)
        request['token_data'] = token_data
        request['auth_manager'] = self.auth_manager
        response = await self.handler(request)  # type: web.Response
        if self.auth_manager.use_cookie and self.handler != logoff:
            response.set_cookie(self.auth_manager.use_cookie, access_token, httponly=True)
        return response

    async def _get_token(self, request) -> Optional[str]:
        try:
            if self.auth_manager.use_cookie in request.cookies:
                access_token = request.cookies.get(self.auth_manager.use_cookie)
            else:
                access_token = self.auth_manager.token_getter(request)
            if hasattr(access_token, '__await__'):
                access_token = await access_token
            if isinstance(access_token, bytes):
                access_token = access_token.decode('utf8')
            return access_token
        except Exception as exc:
            reason = "Cannot decode JWT token"
            request.app.logger.exception(f"${reason}: ${exc}")
            raise web.HTTPInternalServerError(reason=reason)

    async def _check_authorization_rules(self, request):
        for rule in request['authorization_rules']:
            try:
                result = await rule(request)
                if hasattr(result, '__await__'):
                    result = await result
            except Exception as exc:
                reason = "Cannot execute authorization rule"
                request.app.logger.exception(f"${reason}: ${exc}")
                raise web.HTTPInternalServerError(reason=reason)
            if not result:
                raise web.HTTPForbidden(reason="Insufficient access rights")
