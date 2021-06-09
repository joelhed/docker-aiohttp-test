from aiohttp import web
import json

from .db import create_connection
from . import data_access


async def index(request):
    """Get the status of the application."""
    async with create_connection(request.app) as conn:
        question_count = await data_access.get_question_count(conn)

    return web.json_response({
        "status": "online",
        "question_count": question_count,
    })


# POLLS

async def get_polls(request):
    """Get all polls."""
    async with create_connection(request.app) as conn:
        polls = await data_access.get_all_questions(conn)

    return web.json_response(polls)


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
        question_id = await data_access.create_question(conn, question_text, choices)

    return web.json_response({"question_id": question_id})


async def get_poll(request):
    """Get info about a particular poll."""
    poll_id = int(request.match_info["poll_id"])

    async with create_connection(request.app) as conn:
        poll = await data_access.get_question_with_choices(conn, poll_id)
        if poll is None:
            raise web.HTTPNotFound()

    vote_count = sum(choice["votes"] for choice in poll["choices"])
    poll["vote_count"] = vote_count

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
            await data_access.vote_on_choice(conn, poll_id, choice_id)

            choice = await data_access.get_choice(conn, poll_id, choice_id)
            if choice is None:
                raise web.HTTPNotFound()

        return web.json_response(choice)

    return web.json_response({"resource": "put_poll_choice"})
