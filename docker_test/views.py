from aiohttp import web
import json
from sqlite3 import Row

from .db import create_connection


async def index(request):
    async with create_connection(request.app) as conn:
        cur = await conn.execute("""
        SELECT question.id, question.pub_date, question.question_text, choice.choice_text, choice.votes
        FROM choice
        LEFT JOIN question on choice.question_id=question.id;""")
        data = await cur.fetchall()
        await cur.close()
        #conf = request.app["config"]
        return web.json_response(data)


# Resources

# Poll
# /polls
# get all
async def get_polls(request):
    async with create_connection(request.app) as conn:
        conn.row_factory = Row
        cur = await conn.execute("SELECT * FROM question;")
        data = await cur.fetchall()
        return web.json_response([dict(row) for row in data])

# post new
async def post_polls(request):
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

# get one
# /polls/{id}
async def get_poll(request):
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
# put?

# Choice
# /polls/{id}/choices
# post new choice
async def post_poll_choices(request):
    return web.json_response({"resource": "post_poll_choices"})

# /polls/{id}/choices/{id}
# put to vote
async def put_poll_choice(request):
    return web.json_response({"resource": "put_poll_choice"})
