from aiohttp import web
import json
from sqlite3 import Row

from .db import create_connection


async def index(request):
    """Get the status of the application."""
    async with create_connection(request.app) as conn:
        cur = await conn.execute("SELECT COUNT(*) FROM question;")
        question_count, = await cur.fetchone()
    return web.json_response({
        "status": "online",
        "question_count": question_count,
    })


# POLLS

async def get_polls(request):
    """Get all polls."""
    async with create_connection(request.app) as conn:
        conn.row_factory = Row
        cur = await conn.execute("SELECT * FROM question;")
        data = await cur.fetchall()
    return web.json_response([dict(row) for row in data])

async def post_polls(request):
    """Create a new poll.

    The endpoint takes a JSON object in the following format:
    {
      "question_text": "What question would you like to ask?",
      "choices": [
        "One choice",
        "Another choice"
      ]
    }
    """
    try:
        data = await request.json()
        question_text = str(data["question_text"])
        choices = [str(choice) for choice in data["choices"]]
    except (KeyError, json.decoder.JSONDecodeError):
        raise web.HTTPBadRequest()

    async with create_connection(request.app) as conn:
        #conn.row_factory = Row
        cur = await conn.execute(
            "INSERT INTO question (question_text) VALUES (?);",
            (question_text, )
        )
        question_id = cur.lastrowid

        await cur.executemany(
            "INSERT INTO choice (choice_text, question_id) VALUES (?, ?);",
            [(choice_text, question_id) for choice_text in choices],
        )
        await conn.commit()
    return web.json_response({"question_id": question_id})


async def get_poll(request):
    """Get info about a particular poll."""
    poll_id = int(request.match_info["poll_id"])
    async with create_connection(request.app) as conn:
        conn.row_factory = Row

        cur = await conn.execute("SELECT * FROM question WHERE id=?", (poll_id, ))
        res = await cur.fetchone()
        if res is None:
            raise web.HTTPNotFound()

        poll = dict(res)

        await cur.execute("SELECT id, choice_text, votes FROM choice WHERE question_id=?", (poll_id, ))
        res = await cur.fetchall()
        poll["choices"] = [dict(choice) for choice in res]

    return web.json_response(poll)


# CHOICES

async def post_poll_choices(request):
    return web.json_response({"resource": "post_poll_choices"})


async def put_poll_choice(request):
    """Vote on a poll choice.

    The endpoint takes a JSON object in the following format:
    {
      "vote": true
    }
    """
    poll_id = int(request.match_info["poll_id"])
    choice_id = int(request.match_info["choice_id"])
    try:
        data = await request.json()
        vote = bool(data["vote"])
    except (KeyError, TypeError, json.decoder.JSONDecodeError):
        raise web.HTTPBadRequest()

    if vote:
        async with create_connection(request.app) as conn:
            conn.row_factory = Row
            await conn.execute(
                "UPDATE choice SET votes = votes + 1 WHERE question_id=? AND id=?;",
                (poll_id, choice_id),
            )
            await conn.commit()

            cur = await conn.execute(
                "SELECT * FROM choice WHERE question_id=? AND id=?;",
                (poll_id, choice_id),
            )
            res = await cur.fetchone()
            if res is None:
                raise web.HTTPNotFound()

        choice = dict(res)
        return web.json_response(choice)

    return web.json_response({"resource": "put_poll_choice"})
