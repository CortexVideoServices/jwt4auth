from typing import Tuple, Callable, Dict
from aiohttp import web
from .abc import AuthManager

Rule = Callable[[web.Request], bool]

routes = web.RouteTableDef()


def authorized(*rules: Tuple[Rule, ...]):
    """ Decorator sets authorization rules """

    def wrapper(handler):
        async def wrapped_handler(request: web.Request):
            request['authorization_rules'] = rules
            return await handler(request)

        return wrapped_handler

    return wrapper


#: Decorator requires authentication
authenticated = authorized()


@authenticated
@routes.post('/login')
async def refresh(request: web.Request):
    auth_manager = request['auth_manager']  # type: AuthManager
    if request.content_type.startswith('application/json'):
        data = await request.json()
    else:
        data = await request.post()
    username = data.get('username', data.get('login', data.get('email')))
    password = data.get('password')
    if not username or not password:
        raise web.HTTPBadRequest(reason="Absent user credential")
    if not await auth_manager.check_credential(request.app, username, password):
        raise web.HTTPNotFound(reason="Username or password is not correct")
    try:
        access_token, refresh_token = await auth_manager.create_token_pair(request.app, username)
    except ValueError:
        raise web.HTTPUnauthorized(reason="Username has disabled")
    if auth_manager.use_cookie:
        response = web.json_response({'refresh_token': refresh_token})
        response.set_cookie(auth_manager.use_cookie, access_token, httponly=True)
    else:
        response = web.json_response({'refresh_token': refresh_token, 'access_token': access_token})
    return response


@authenticated
@routes.post('/refresh')
async def refresh(request: web.Request):
    auth_manager = request['auth_manager']  # type: AuthManager
    if request.content_type.startswith('application/json'):
        data = await request.json()
    else:
        data = await request.post()
    if refresh_token := data.get('refresh_token') is None:
        raise web.HTTPBadRequest(reason="Absent refresh token")
    try:
        access_token, refresh_token = await auth_manager.refresh_token_pair(request.app, refresh_token)
    except ValueError:
        raise web.HTTPUnauthorized(reason="Bad refresh token")
    if auth_manager.use_cookie:
        response = web.json_response({'refresh_token': refresh_token})
        response.set_cookie(auth_manager.use_cookie, access_token, httponly=True)
    else:
        response = web.json_response({'refresh_token': refresh_token, 'access_token': access_token})
    return response


@authenticated
@routes.get('/logoff')
async def logoff(request: web.Request):
    token_data = request['token_data']  # type: Dict
    auth_manager = request['auth_manager']  # type: AuthManager
    await auth_manager.reset_refresh_token(request.app, token_data)
    return web.HTTPOk()
