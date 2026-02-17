"""Tests for SysMLClient."""

import httpx

from sysml_v2.api.client import SysMLClient


class MockTransport(httpx.BaseTransport):
    """Fake transport that returns canned responses based on path."""

    def __init__(self, routes: dict):
        self._routes = routes

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path
        for route, response_data in self._routes.items():
            if path == route:
                return httpx.Response(200, json=response_data)
        return httpx.Response(404, json={"error": "not found"})


def _make_client(routes: dict) -> SysMLClient:
    """Create a SysMLClient with a mock transport."""
    client = SysMLClient.__new__(SysMLClient)
    client._client = httpx.Client(
        base_url="http://test",
        transport=MockTransport(routes),
    )
    return client


def test_list_projects():
    projects = [{"@id": "p1", "name": "Test"}]
    client = _make_client({"/projects": projects})

    result = client.list_projects()

    assert result == projects
    client.close()


def test_get_project():
    project = {"@id": "p1", "name": "Test"}
    client = _make_client({"/projects/p1": project})

    result = client.get_project("p1")

    assert result == project
    client.close()


def test_healthy_returns_true():
    client = _make_client({"/": {"status": "ok"}})

    assert client.healthy() is True
    client.close()


def test_context_manager():
    client = _make_client({"/": {}})
    with client as c:
        assert c.healthy()


def test_get_elements():
    elements = [{"@id": "e1", "@type": "PartUsage"}]
    client = _make_client({"/projects/p1/commits/c1/elements": elements})

    result = client.get_elements("p1", "c1")

    assert result == elements
    client.close()
