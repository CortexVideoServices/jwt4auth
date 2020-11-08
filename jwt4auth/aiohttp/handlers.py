from typing import Tuple, Callable, Dict
from aiohttp import web
from jwt4auth.general import AuthManager

Rule = Callable[[web.Request], bool]


def authorized(*rules: Tuple[Rule, ...]):
    """ Decorator sets authorization rules """

    def wrapper(handler):
        handler.authorization_rules = rules
        return handler

    return wrapper


#: Decorator requires authentication
authenticated = authorized()

routes = web.RouteTableDef()


@routes.post('/login')
async def login(request: web.Request):
    auth_manager = request['auth_manager']  # type: AuthManager
    if request.content_type.startswith('application/json'):
        data = await request.json()
    else:
        data = await request.post()
    username = data.get('username', data.get('login', data.get('email')))
    password = data.get('password')
    if not username or not password:
        raise web.HTTPBadRequest(reason="Absent user credential")
    if not await auth_manager.check_credential(username, password):
        raise web.HTTPNotFound(reason="Username or password is not correct")
    access_token, token_data, refresh_token = await auth_manager.create_tokens(username)
    if auth_manager.use_cookie:
        response = web.json_response({'refresh_token': refresh_token, 'token_data': token_data})
        response.set_cookie(auth_manager.use_cookie, access_token, httponly='HttpOnly')
    else:
        response = web.json_response({
            'refresh_token': refresh_token,
            'access_token': access_token,
            'token_data': token_data
        })
    return response


@authenticated
@routes.post('/refresh')
async def refresh(request: web.Request):
    auth_manager = request['auth_manager']  # type: AuthManager
    if request.content_type.startswith('application/json'):
        data = await request.json()
    else:
        data = await request.post()
    if (refresh_token := data.get('refresh_token')) is None:
        raise web.HTTPBadRequest(reason="Absent refresh token")
    username = await auth_manager.check_refresh_token(refresh_token)
    if not username:
        raise web.HTTPUnauthorized(reason="Bad refresh token")
    access_token, token_data, refresh_token = await auth_manager.create_tokens(username)
    if auth_manager.use_cookie:
        response = web.json_response({'refresh_token': refresh_token, 'token_data': token_data})
        response.set_cookie(auth_manager.use_cookie, access_token, httponly='HttpOnly')
    else:
        response = web.json_response({
            'refresh_token': refresh_token,
            'access_token': access_token,
            'token_data': token_data
        })
    request.pop('token_data', None)
    return response


@authenticated
@routes.get('/logoff')
async def logoff(request: web.Request):
    token_data = request['token_data']  # type: Dict
    auth_manager = request['auth_manager']  # type: AuthManager
    if not await auth_manager.reset_refresh_token(token_data['username']):
        request.app.logger.warning('Cannot reset refresh token')
    request.pop('token_data', None)
    return web.HTTPOk()
