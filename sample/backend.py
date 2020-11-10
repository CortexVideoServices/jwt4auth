import re
import os.path
import mimetypes
from datetime import datetime, timezone
from typing import Dict, Union, Optional
from urllib.parse import urljoin

from aiohttp import web, ClientSession

import jwt4auth.aiohttp
from jwt4auth.aiohttp import authenticated

routes = web.RouteTableDef()


@authenticated
@routes.get('/api/message')
async def secured(request: web.Request):
    return web.json_response(
        {'message': f'This is very, very protected data. Current time: {datetime.now(timezone.utc).isoformat()}'})


@web.middleware
async def error_middleware(request: web.Request, handler):
    try:
        response = await handler(request)
        if response.status != 404 or request.method not in ('HEAD', 'GET'):
            return response
    except web.HTTPException as ex:
        if ex.status != 404 or request.method not in ('HEAD', 'GET'):
            raise
        response = ex
    if static_serve := request.app.get('static_serve'):
        return await static_serve(request)
    if proxy_pass := request.app.get('proxy_pass'):
        return await proxy_pass(request)
    return response


class AuthManager(jwt4auth.aiohttp.AuthManager):
    sessions = dict()

    async def check_credential(self, username: str, password: str) -> bool:
        return password == '123456'

    async def get_user_data(self, username: Union[int, str]) -> Optional[Dict]:
        return {'username': username,
                'display_name': ' '.join(map(lambda s: s.capitalize(), re.split(r'\W|_', username.split('@')[0])))}

    async def save_refresh_token(self, user_data: Dict, refresh_token: str) -> bool:
        self.sessions[user_data['username']] = refresh_token
        return True

    async def check_refresh_token(self, user_data: Dict, refresh_token: str) -> bool:
        username = user_data['username']
        return username in self.sessions and self.sessions[username] == refresh_token

    async def reset_refresh_token(self, user_data: Dict) -> bool:
        return self.sessions.pop(user_data['username'], None) is not None


class Application(web.Application):
    def __init__(self, **kwargs):
        auth_manager = AuthManager('SECRET', access_token_ttl=20)
        kwargs['middlewares'] = (error_middleware, auth_manager.middleware)
        proxy_url = kwargs.pop('proxy_url', None)
        static_path = kwargs.pop('static_path', None)
        super().__init__(**kwargs)
        self.add_routes(auth_manager.routes)
        self.add_routes(routes)

        async def static_serve(static_path, request: web.Request):
            filename = os.path.join(os.path.abspath(static_path), 'index.html')
            if request.path != '/':
                filename = os.path.join(static_path, *request.path.split('/')[1:])
            if not os.path.exists(filename):
                raise web.HTTPNotFound()
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            response = web.StreamResponse(status=200, headers={'Content-Type': content_type})
            await response.prepare(request)
            with open(filename, 'rb') as file:
                while True:
                    chunk = file.read(1024 * 16)
                    if not chunk:
                        break
                    await response.write(chunk)
            return response

        async def proxy_pass(proxy_url, request: web.Request):
            async with ClientSession() as session:
                async with session.request(request.method, urljoin(proxy_url, request.path_qs)) as proxy:
                    response = web.StreamResponse(status=proxy.status, reason=proxy.reason,
                                                  headers={'Content-Type': proxy.content_type})
                    await response.prepare(request)
                    while True:
                        chunk = await proxy.content.read()
                        if not chunk:
                            break
                        await response.write(chunk)
                    return response

        if static_path:
            self['static_serve'] = lambda *args: static_serve(static_path, *args)
            self.logger.info(f'Enabled serving static files from path {static_path}')
        elif proxy_url:
            self['proxy_pass'] = lambda *args: proxy_pass(proxy_url, *args)
            self.logger.info(f'Enabled proxy pass to {proxy_url}')


if __name__ == '__main__':
    import argparse
    import logging

    parser = argparse.ArgumentParser("Backend")
    parser.add_argument('--proxy-url', help='Proxy URL')
    parser.add_argument('--static-path', help='Static file path')
    parser.add_argument('--debug', default=False, action='store_true', help='debug mode')
    options, _ = parser.parse_known_args()

    logging.basicConfig(level=(logging.DEBUG if options.debug else logging.INFO))
    app = Application(logger=logging.root, static_path=options.static_path, proxy_url=options.proxy_url)
    web.run_app(app, port=5000)
