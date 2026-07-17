"""Mihomo (Clash Meta) HTTP API client."""

import os
from typing import Any

import httpx


class MihomoError(Exception):
    """Raised when the Mihomo API returns an error."""
    pass


class MihomoClient:
    """Async HTTP client for Mihomo external controller API.

    API docs: https://clash.wiki/configuration.html#external-controller
    """

    def __init__(
        self,
        base_url: str | None = None,
        secret: str | None = None,
    ):
        self.base_url = (base_url or os.getenv("MIHOMO_API_URL", "http://127.0.0.1:9090")).rstrip("/")
        self.secret = secret or os.getenv("MIHOMO_API_SECRET", "")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._headers(),
            timeout=httpx.Timeout(10.0),
        )

    def _headers(self) -> dict[str, str]:
        h = {}
        if self.secret:
            h["Authorization"] = f"Bearer {self.secret}"
        return h

    async def close(self):
        await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        resp = await self._client.request(method, path, **kwargs)
        if resp.status_code >= 400:
            raise MihomoError(f"{method} {path} → {resp.status_code}: {resp.text[:200]}")
        return resp.json()

    # ── proxies ──────────────────────────────────────────────

    async def get_proxies(self) -> dict[str, Any]:
        """Return all proxies and proxy groups with their metadata."""
        return await self._request("GET", "/proxies")

    async def switch_proxy(self, group: str, node: str) -> dict[str, Any]:
        """Switch a proxy group to the specified node."""
        return await self._request("PUT", f"/proxies/{group}", json={"name": node})

    async def test_delay(
        self, name: str, url: str = "https://www.gstatic.com/generate_204", timeout: int = 3000
    ) -> dict[str, Any]:
        """Test delay of a specific proxy node."""
        return await self._request(
            "GET", f"/proxies/{name}/delay", params={"url": url, "timeout": timeout}
        )

    # ── configs ──────────────────────────────────────────────

    async def get_configs(self) -> dict[str, Any]:
        """Return current Mihomo configuration."""
        return await self._request("GET", "/configs")

    async def patch_configs(self, updates: dict[str, Any]) -> None:
        """Patch Mihomo config (e.g. mode, sniffer, etc.). PATCH /configs."""
        await self._client.request("PATCH", "/configs", json=updates)

    async def reload_config(self) -> None:
        """Force reload configuration from disk."""
        await self._request("PUT", "/configs", params={"force": "true"})

    # ── rules ────────────────────────────────────────────────

    async def get_rules(self) -> dict[str, Any]:
        """Return routing rules."""
        return await self._request("GET", "/rules")
