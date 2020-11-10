from typing import Callable, Union, Awaitable

import jwt
from aiohttp import web

import jwt4auth.general

routes = web.RouteTableDef()

Rule = Callable[[web.Request], Union[Awaitable[bool], bool]]


def authorized(*rules: Rule):
    """ The decorator sets the authorization rules and requires them to be checked
    """

    def wrapper(handler):
        handler.authorization_rules = rules
        return handler

    return wrapper


#: Decorator requires authentication check
authenticated = authorized()


async def _get_request_data(request: web.Request, *keys: str):
    if request.content_type.startswith('application/json'):
        data = await request.json()
    else:
        data = dict(await request.post())
    try:
        return [data[key] for key in keys]
    except KeyError as exc:
        raise web.HTTPBadRequest(reason=str(exc))


@routes.post('/auth/login')
async def login(request: web.Request):
    """ Login request handler """
    auth_manager = request['auth_manager']  # type: AuthManager
    username, password = await _get_request_data(request, 'username', 'password')
    if not await auth_manager.check_credential(username, password):
        raise web.HTTPNotFound(reason="Username or password is not correct")
    user_data = await auth_manager.get_user_data(username)
    access_token, refresh_token = await auth_manager.create_token_pair(user_data)
    request['access_token'] = access_token
    if auth_manager.use_cookie:
        return web.json_response({'refresh_token': refresh_token, 'user_data': user_data})
    else:
        return web.json_response({'access_token': access_token, 'refresh_token': refresh_token, 'user_data': user_data})


@authenticated
@routes.post('/auth/refresh')
async def refresh(request: web.Request):
    user_data = request['user_data']
    auth_manager = request['auth_manager']  # type: AuthManager
    refresh_token, = await _get_request_data(request, 'refresh_token')
    if not (await auth_manager.check_refresh_token(user_data, refresh_token)):
        raise web.HTTPUnauthorized(reason="Bad refresh token")
    access_token, refresh_token = await auth_manager.create_token_pair(user_data)
    request['access_token'] = access_token
    if auth_manager.use_cookie:
        return web.json_response({'refresh_token': refresh_token, 'user_data': user_data})
    else:
        return web.json_response({'access_token': access_token, 'refresh_token': refresh_token, 'user_data': user_data})


@authenticated
@routes.get('/auth/logoff')
async def logoff(request: web.Request):
    user_data = request['user_data']
    auth_manager = request['auth_manager']  # type: AuthManager
    if not await auth_manager.reset_refresh_token(user_data):
        request.app.logger.warning('Cannot reset refresh token')
    request.pop('access_token', None)
    return web.HTTPOk()


class AuthManager(jwt4auth.general.AuthManager):
    """ Auth manager for aiohttp
    """
    routes = routes

    async def check_authorization_rules(self, request: web.Request, *rules: Rule):
        for rule in rules:
            try:
                result = rule(request)
                if hasattr(result, '__await__'):
                    result = await result
            except Exception as exc:
                reason = "Cannot execute authorization rule"
                request.app.logger.exception(f"${reason}: ${exc}")
                raise web.HTTPInternalServerError(reason=reason)
            if not result:
                raise web.HTTPForbidden(reason="Insufficient access rights")

    async def middleware(auth_manager, application, handler):
        """ aiohttp middleware """

        async def middleware_handler(request: web.Request):
            access_token = None
            request['auth_manager'] = auth_manager
            authorization_rules = getattr(handler, 'authorization_rules', None)
            if authorization_rules is not None:
                if auth_manager.use_cookie in request.cookies:
                    access_token = request.cookies.get(auth_manager.use_cookie)
                else:
                    if 'Authorization' in request.headers:
                        scheme, remain = request.headers.get('Authorization').strip().split(' ')
                        if scheme.lower() == 'bearer':
                            access_token = remain
                if access_token is None:
                    raise web.HTTPUnauthorized(reason="Authentication required")
                request['access_token'] = access_token
                try:
                    request['user_data'] = auth_manager.check_access_token(access_token,
                                                                           verify_exp=handler not in (refresh, logoff))
                except (jwt.InvalidTokenError, KeyError, ValueError):
                    raise web.HTTPUnauthorized(reason="Invalid or outdated access token")
            if authorization_rules is not None:
                await auth_manager.check_authorization_rules(request, *authorization_rules)
            response = await handler(request)  # type: web.Response
            access_token = request.pop('access_token', access_token)
            if auth_manager.use_cookie and access_token is not None:
                response.set_cookie(auth_manager.use_cookie, access_token, httponly=True)
            return response

        return middleware_handler
