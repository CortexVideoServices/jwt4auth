from urllib.parse import urljoin
from datetime import datetime, timezone
from aiohttp import web, ClientSession

routes = web.RouteTableDef()


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
    proxy_pass = request.app.get('proxy_pass')
    if proxy_pass:
        return await proxy_pass(request)
    return response


class Application(web.Application):
    def __init__(self, **kwargs):
        kwargs['middlewares'] = (error_middleware,)
        proxy_url = kwargs.pop('proxy_url', None)
        super().__init__(**kwargs)
        self.add_routes(routes)

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

        if proxy_url:
            self['proxy_pass'] = lambda *args: proxy_pass(proxy_url, *args)
            self.logger.info(f'Enabled proxy pass to {proxy_url}')


if __name__ == '__main__':
    import argparse
    import logging

    parser = argparse.ArgumentParser("Backend")
    parser.add_argument('--proxy-url', help='Proxy URL')
    parser.add_argument('--debug', default=False, action='store_true', help='debug mode')
    options, _ = parser.parse_known_args()

    logging.basicConfig(level=(logging.DEBUG if options.debug else logging.INFO))
    app = Application(logger=logging.root, proxy_url=options.proxy_url)
    web.run_app(app, port=5000)
