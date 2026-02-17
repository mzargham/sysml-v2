"""SysML v2 REST API client wrapping httpx."""

from __future__ import annotations

from typing import Any

import httpx

from sysml_v2.config import load_config

_DEFAULT_TIMEOUT = 30


class SysMLClient:
    """Lightweight client for the SysML v2 Systems Modeling API.

    Works with any server that implements the SysML v2 REST API
    (gorenje/sysmlv2-api, Gearshift, or the reference implementation).

    Usage::

        client = SysMLClient()              # reads url from sysml.toml or default
        client = SysMLClient("http://localhost:9000")
        projects = client.list_projects()
    """

    def __init__(self, base_url: str | None = None, timeout: float = _DEFAULT_TIMEOUT) -> None:
        if base_url is None:
            cfg = load_config()
            base_url = cfg.server.url
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def close(self) -> None:
        """Close the underlying HTTP connection."""
        self._client.close()

    def __enter__(self) -> SysMLClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- Health ---------------------------------------------------------------

    def healthy(self) -> bool:
        """Return True if the API server is reachable."""
        try:
            resp = self._client.get("/")
            return resp.status_code < 500
        except httpx.HTTPError:
            return False

    # -- Projects -------------------------------------------------------------

    def list_projects(self) -> list[dict[str, Any]]:
        """List all projects on the server."""
        resp = self._client.get("/projects")
        resp.raise_for_status()
        return resp.json()

    def get_project(self, project_id: str) -> dict[str, Any]:
        """Get a single project by ID."""
        resp = self._client.get(f"/projects/{project_id}")
        resp.raise_for_status()
        return resp.json()

    def create_project(self, name: str, description: str = "") -> dict[str, Any]:
        """Create a new project."""
        body: dict[str, Any] = {"name": name}
        if description:
            body["description"] = description
        resp = self._client.post("/projects", json=body)
        resp.raise_for_status()
        return resp.json()

    # -- Commits --------------------------------------------------------------

    def list_commits(self, project_id: str) -> list[dict[str, Any]]:
        """List commits for a project."""
        resp = self._client.get(f"/projects/{project_id}/commits")
        resp.raise_for_status()
        return resp.json()

    def get_commit(self, project_id: str, commit_id: str) -> dict[str, Any]:
        """Get a single commit."""
        resp = self._client.get(f"/projects/{project_id}/commits/{commit_id}")
        resp.raise_for_status()
        return resp.json()

    # -- Elements -------------------------------------------------------------

    def get_elements(self, project_id: str, commit_id: str) -> list[dict[str, Any]]:
        """List all elements in a commit."""
        resp = self._client.get(
            f"/projects/{project_id}/commits/{commit_id}/elements"
        )
        resp.raise_for_status()
        return resp.json()

    def get_element(
        self, project_id: str, commit_id: str, element_id: str
    ) -> dict[str, Any]:
        """Get a single element by ID."""
        resp = self._client.get(
            f"/projects/{project_id}/commits/{commit_id}/elements/{element_id}"
        )
        resp.raise_for_status()
        return resp.json()

    # -- Queries --------------------------------------------------------------

    def query(
        self, project_id: str, commit_id: str, body: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Execute a query against a commit.

        *body* should be a dict conforming to the SysML v2 Query schema,
        e.g. ``{"@type": "Query", "select": [...], "where": {...}}``.
        """
        resp = self._client.post(
            f"/projects/{project_id}/commits/{commit_id}/query",
            json=body,
        )
        resp.raise_for_status()
        return resp.json()
