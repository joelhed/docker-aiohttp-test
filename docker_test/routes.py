from aiohttp import web
from . import views 


def setup_routes(app):
    app.add_routes([
        web.get("/", views.index),
        web.get("/polls", views.get_polls),
        web.post("/polls", views.post_polls),
        web.get(r"/polls/{poll_id:\d+}", views.get_poll),
        web.post(r"/polls/{poll_id:\d+}/choices", views.post_poll_choices),
        web.put(r"/polls/{poll_id:\d+}/choices/{choice_id:\d+}", views.put_poll_choice),
    ])
