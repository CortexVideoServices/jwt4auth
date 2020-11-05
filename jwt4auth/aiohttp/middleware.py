from typing import Optional
import jwt
from aiohttp import web
from jwt4auth.general import AuthManager
from .handlers import refresh, logoff


class AuthMiddleware(object):
    """ aiohttp middleware that works with auth manager
    """

    def __init__(self, auth_manager: AuthManager, handler):
        self.auth_manager = auth_manager
        self.handler = handler

    async def __call__(self, request: web.Request):
        request['auth_manager'] = self.auth_manager
        authorization_rules = getattr(self.handler, 'authorization_rules', None)
        token_data = None
        access_token = await self._get_token(request)
        try:
            try:
                if access_token is not None:
                    token_data = jwt.decode(
                        access_token,
                        self.auth_manager.secret,
                        algorithms=self.auth_manager.algorithm,
                        options={'verify_exp': self.handler not in (refresh, logoff)}
                    )
            except jwt.InvalidTokenError:
                raise web.HTTPUnauthorized(reason="Invalid or outdated access token")
            if token_data is None:
                raise web.HTTPUnauthorized(reason="Authentication required")
            else:
                request['token_data'] = token_data
        except web.HTTPUnauthorized as exc:
            if authorization_rules is not None:
                raise exc
        if authorization_rules is not None:
            await self._check_authorization_rules(request, self.handler.authorization_rules)
        response = await self.handler(request)  # type: web.Response
        if 'token_data' in request and self.auth_manager.use_cookie:
            response.set_cookie(self.auth_manager.use_cookie, access_token, httponly='HttpOnly')
        return response

    async def _get_token(self, request) -> Optional[str]:
        try:
            if self.auth_manager.use_cookie in request.cookies:
                access_token = request.cookies.get(self.auth_manager.use_cookie)
            else:
                access_token = self.bearer_token_getter(request)
            if hasattr(access_token, '__await__'):
                access_token = await access_token
            if isinstance(access_token, bytes):
                access_token = access_token.decode('utf8')
            return access_token
        except Exception as exc:
            reason = "Cannot decode JWT token"
            request.app.logger.exception(f"${reason}: ${exc}")
            raise web.HTTPInternalServerError(reason=reason)

    async def _check_authorization_rules(self, request, authorization_rules):
        for rule in authorization_rules:
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

    @staticmethod
    def bearer_token_getter(request: web.Request) -> Optional[str]:
        """ JWT token getter from bearer authentication header """
        if 'Authorization' in request.headers:
            scheme, access_token = request.headers.get('Authorization').strip().split(' ')
            if scheme.lower() == 'bearer':
                return access_token