from typing import Sequence, Optional
from aiohttp import web


def bearer_token_getter(request: web.Request) -> Optional[str]:
    """ JWT token getter from bearer authentication header """
    if 'Authorization' in request.headers:
        scheme, access_token = request.headers.get('Authorization').strip().split(' ')
        if scheme.lower() == 'bearer':
            return access_token


def with_prefix(prefix: str, routes: Sequence[web.RouteDef]) -> Sequence[web.RouteDef]:
    """ Adds prefix to routes """
    return [web.RouteDef(route.method, prefix + route.path, route.handler, route.kwargs) for route in routes]
