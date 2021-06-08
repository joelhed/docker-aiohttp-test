from aiohttp import web
import json

from .db import create_connection


async def index(request):
    async with create_connection(request.app) as conn:
        cur = await conn.execute("""
        SELECT question.id, question.pub_date, question.question_text, choice.choice_text, choice.votes
        FROM choice
        LEFT JOIN question on choice.question_id=question.id;""")
        data = await cur.fetchall()
        await cur.close()
        conf = request.app["config"]
        return web.Response(text=json.dumps(data))
