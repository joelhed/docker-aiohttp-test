import pytest
from docker_test.main import make_app
import init_db


@pytest.fixture
async def client(aiohttp_client, loop):
    init_db.init_db_with_sample_data()
    app = make_app()
    client = await aiohttp_client(app)
    return client


async def test_index(client):
    resp = await client.get('/')
    assert resp.status == 200
    
    data = await resp.json()
    assert data["status"] == "online"
    assert data["question_count"] == 1


async def test_get_polls(client):
    resp = await client.get('/polls')
    assert resp.status == 200

    data = await resp.json()
    assert len(data) == 1

    poll = data[0]
    assert poll["id"] == 1
    assert poll["question_text"] == "What's new?"
    assert poll["pub_date"] == "2015-12-15 17:17:49"


async def test_get_poll(client):
    resp = await client.get('/polls/1')
    assert resp.status == 200

    poll = await resp.json()
    assert poll["question_text"] == "What's new?"
    assert poll["pub_date"] == "2015-12-15 17:17:49"
    assert poll["vote_count"] == 0
    assert len(poll["choices"]) == 3

    choice = next(
        (choice for choice in poll["choices"] if choice["choice_text"] == "The sky"),
        None
    )
    assert choice is not None
    assert choice["id"] == 2
    assert choice["votes"] == 0


# Create new poll

async def test_post_polls(client):
    new_poll = {
        "question_text": "A test question",
        "choices": [
            "Choice 1",
            "Choice 2",
        ],
    }
    resp = await client.post('/polls', json=new_poll)
    assert resp.status == 200

    poll_id = (await resp.json())["question_id"]
    assert poll_id == 2

    # Check that it got posted
    resp = await client.get(f'/polls/{poll_id}')
    assert resp.status == 200

    poll = await resp.json()
    assert poll["question_text"] == "A test question"
    assert poll["vote_count"] == 0

    choice = next(
        (choice for choice in poll["choices"] if choice["choice_text"] == "Choice 1"),
        None
    )
    assert choice is not None
    assert type(choice["id"]) == int
    assert choice["votes"] == 0


async def test_post_polls_without_question_text(client):
    new_poll = {
        #"question_text": "A test question",
        "choices": [
            "Choice 1",
            "Choice 2",
        ],
    }
    resp = await client.post('/polls', json=new_poll)
    assert resp.status == 400


async def test_post_polls_with_empty_question_text(client):
    new_poll = {
        "question_text": " ",
        "choices": [
            "Choice 1",
            "Choice 2",
        ],
    }
    resp = await client.post('/polls', json=new_poll)
    assert resp.status == 400


async def test_post_polls_without_choices(client):
    new_poll = {
        "question_text": "A test question",
        #"choices": [
        #    "Choice 1",
        #    "Choice 2",
        #],
    }
    resp = await client.post('/polls', json=new_poll)
    assert resp.status == 400


async def test_post_polls_with_empty_choices_list(client):
    new_poll = {
        "question_text": "A test question",
        "choices": [
            #"Choice 1",
            #"Choice 2",
        ],
    }
    resp = await client.post('/polls', json=new_poll)
    assert resp.status == 400


async def test_post_polls_with_only_empty_choices(client):
    new_poll = {
        "question_text": "A test question",
        "choices": [
            "",
            "",
        ],
    }
    resp = await client.post('/polls', json=new_poll)
    assert resp.status == 400


async def test_post_polls_with_some_empty_choices(client):
    new_poll = {
        "question_text": "A test question",
        "choices": [
            "Choice 1",
            "Choice 2",
            " ",
            "",
        ],
    }
    resp = await client.post('/polls', json=new_poll)
    assert resp.status == 200

    poll_id = (await resp.json())["question_id"]

    resp = await client.get(f'/polls/{poll_id}')
    assert resp.status == 200

    poll = await resp.json()
    assert poll["question_text"] == "A test question"

    choices = [choice["choice_text"] for choice in poll["choices"]]
    assert choices == ["Choice 1", "Choice 2"]


# Choice

async def test_get_choice(client):
    resp = await client.get('/polls/1/choices/2')
    assert resp.status == 200

    choice = await resp.json()
    assert choice["id"] == 2
    assert choice["question_id"] == 1
    assert choice["choice_text"] == "The sky"
    assert choice["votes"] == 0


async def test_vote_on_choice(client):
    body = {
        "vote": True
    }
    resp = await client.put('/polls/1/choices/2', json=body)
    assert resp.status == 200

    choice = await resp.json()
    assert choice["id"] == 2
    assert choice["question_id"] == 1
    assert choice["choice_text"] == "The sky"
    assert choice["votes"] == 1

    # Check that it actually updated
    resp = await client.get('/polls/1')
    assert resp.status == 200

    poll = await resp.json()
    assert poll["vote_count"] == 1

    choice = next(
        (choice for choice in poll["choices"] if choice["id"] == 2),
        None
    )
    assert choice is not None
    assert choice["choice_text"] == "The sky"
    assert choice["votes"] == 1


async def test_put_choice_without_content(client):
    body = {
        #"vote": True
    }
    resp = await client.put('/polls/1/choices/2', json=body)
    assert resp.status == 200

    choice = await resp.json()
    choice["votes"] == 0


async def test_put_choice_where_vote_is_false(client):
    body = {
        "vote": False
    }
    resp = await client.put('/polls/1/choices/2', json=body)
    assert resp.status == 200

    choice = await resp.json()
    choice["votes"] == 0


async def test_put_choice_where_vote_isnt_bool(client):
    body = {
        "vote": "Something weird"
    }
    resp = await client.put('/polls/1/choices/2', json=body)
    assert resp.status == 400
