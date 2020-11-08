import re
import os.path
from datetime import datetime, timezone
from typing import Optional, Union, Dict

from aiohttp import web
import jwt4auth.aiohttp
from jwt4auth.aiohttp.handlers import authenticated

routes = web.RouteTableDef()
static_path = os.path.join(os.path.dirname(__file__), 'dist')


@authenticated
@routes.get('/api/message')
async def secured(request: web.Request):
    return web.json_response(
        {'message': f'This is very, very protected data. Current time: {datetime.now(timezone.utc).isoformat()}'})


@routes.get('/')
@routes.get(r'/{file:[\.\-\w]+\.(html|js|css)$}')
async def static(request: web.Request):
    filepath = request.match_info.get('file', 'index.html')
    filepath = os.path.join(static_path, filepath)
    if (os.path.exists(filepath)):
        content_type = 'text/html'
        if filepath.endswith('.js'):
            content_type = 'application/javascript'
        elif filepath.endswith('.css'):
            content_type = 'text/css'
        with open(filepath) as file:
            return web.Response(status=200, content_type=content_type, body=file.read())
    return web.HTTPNotFound()


class AuthManager(jwt4auth.aiohttp.AuthManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sessions = dict()

    async def check_credential(self, username: str, password: str) -> bool:
        return password == '123456'

    async def create_user_data(self, username: Union[int, str]) -> Optional[Dict]:
        return {'username': username,
                'display_name': ' '.join(map(lambda s: s.capitalize(), re.split(r'\W|_', username.split('@')[0])))}

    async def save_refresh_token(self, username: str, refresh_token: str) -> bool:
        self.sessions[username] = refresh_token
        return True

    async def check_refresh_token(self, refresh_token: str) -> Optional[Union[int, str]]:
        for username, refresh_token_ in self.sessions.items():
            if refresh_token == refresh_token_:
                return username

    async def reset_refresh_token(self, username: str) -> bool:
        return self.sessions.pop(username, None) is not None


if __name__ == '__main__':
    import os.path
    import logging

    logging.basicConfig(level=logging.INFO)
    auth_manager = AuthManager(secret='VeryVerySecretPhrase', access_token_ttl=120)
    auth_routes = [web.RouteDef(route.method, '/auth' + route.path, route.handler, route.kwargs)
                   for route in auth_manager.routes]
    app = web.Application(middlewares=[auth_manager.middleware], logger=logging.root)
    app['auth_manager'] = auth_manager
    app.router.add_routes(auth_routes)
    app.router.add_routes(routes)
    web.run_app(app, port=5000)
