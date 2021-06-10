import asyncio
#import aiohttp
from aiohttp import web

from .routes import setup_routes
from .settings import config


def make_app():
    app = web.Application()
    setup_routes(app)
    app["config"] = config
    return app


if __name__ == "__main__":
    app = make_app()
    web.run_app(app)
