import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.store import store

"""Basic pytest tests for core FastAPI endpoints and application behavior."""

@pytest.fixture(autouse=True)
def clear_store():
    store._items.clear()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_live_return_200(client):
    response = await client.get("/health/live")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "live ok"


@pytest.mark.asyncio
async def test_post_items_creates_item(client):
    payload = {
        "name": "Book",
        "description": "Test item",
        "status": "ACTIVE",
    }

    response = await client.post("/items", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == payload["name"]
    assert body["description"] == payload["description"]
    assert body["status"] == payload["status"]
    assert "id" in body
    assert "created_at" in body


@pytest.mark.asyncio
async def test_get_item_by_id_returns_created_item(client):
    payload = {
        "name": "Pen",
        "description": "Blue pen",
        "status": "ACTIVE",
    }

    create_response = await client.post("/items", json=payload)
    created_item = create_response.json()
    item_id = created_item["id"]

    get_response = await client.get(f"/items/{item_id}")
    assert get_response.status_code == 200

    body = get_response.json()
    assert body["id"] == item_id
    assert body["name"] == payload["name"]


@pytest.mark.asyncio
async def test_get_item_by_id_return_404_for_missing_item(client):
    response = await client.get("/items/non-existent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


@pytest.mark.asyncio
async def test_get_items_lists_items(client):
    payload_1 = {
        "name": "Item 1",
        "description": "First item",
        "status": "ACTIVE",
    }
    payload_2 = {
        "name": "Item 2",
        "description": "Second item",
        "status": "INACTIVE",
    }

    await client.post("/items", json=payload_1)
    await client.post("/items", json=payload_2)

    response = await client.get("/items")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2


@pytest.mark.asyncio
async def test_delete_item_removes_item(client):
    payload = {
        "name": "Notebook",
        "description": "To be deleted",
        "status": "ARCHIVED",
    }

    create_response = await client.post("/items", json=payload)
    item_id = create_response.json()["id"]

    delete_response = await client.delete(f"/items/{item_id}")
    assert delete_response.status_code == 200
    assert "deleted successfully" in delete_response.json()["message"]

    get_response = await client.get(f"/items/{item_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_metrics_endpoint_returns_200(client):
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "request_count" in response.text or "error_count" in response.text