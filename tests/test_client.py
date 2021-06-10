import pytest
from docker_test.main import app
import init_db


@pytest.fixture
async def client(aiohttp_client, loop):
    init_db.init_db_with_sample_data()
    client = await aiohttp_client(app)
    return client


async def test_index(client):
    resp = await client.get('/')
    assert resp.status == 200
    data = await resp.json()
    assert data["status"] == "online"
    assert data["question_count"] == 1
