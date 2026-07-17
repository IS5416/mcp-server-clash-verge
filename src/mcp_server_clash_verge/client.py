"""Mihomo (Clash Meta) HTTP API client."""

import os
import platform
from pathlib import Path
from typing import Any

import httpx


class MihomoError(Exception):
    """Raised when the Mihomo API returns an error."""
    pass


def _find_clash_config() -> Path | None:
    """Locate Clash Verge Rev config file on supported platforms."""
    app_id = "io.github.clash-verge-rev.clash-verge-rev"
    system = platform.system()
    if system == "Windows":
        base = Path(os.environ.get("APPDATA", ""))
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:  # Linux
        xdg = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        base = Path(xdg)

    config_path = base / app_id / "config.yaml"
    return config_path if config_path.exists() else None


def _parse_clash_config(path: Path) -> dict[str, str]:
    """Extract external-controller and secret from Clash Verge config."""
    result: dict[str, str] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("external-controller:"):
                val = stripped.split(":", 1)[1].strip()
                if val:
                    result["external_controller"] = val
            elif stripped.startswith("secret:"):
                val = stripped.split(":", 1)[1].strip()
                result["secret"] = val
    return result


class MihomoClient:
    """Async HTTP client for Mihomo external controller API.

    Configuration priority (highest to lowest):
    1. Explicit constructor arguments
    2. Environment variables (MIHOMO_API_URL, MIHOMO_API_SECRET)
    3. Auto-detected from Clash Verge Rev config file
    4. Built-in defaults (http://127.0.0.1:9090 / no secret)
    """

    def __init__(
        self,
        base_url: str | None = None,
        secret: str | None = None,
    ):
        # Resolve base_url: explicit → env → auto-detect → default
        self.base_url = (
            base_url
            or os.getenv("MIHOMO_API_URL")
            or self._auto_detect_url()
            or "http://127.0.0.1:9090"
        ).rstrip("/")

        # Resolve secret: explicit → env → auto-detect → default
        # Empty string from env or auto-detect means no secret
        self.secret = secret
        if self.secret is None:
            self.secret = os.getenv("MIHOMO_API_SECRET")
        if self.secret is None:
            self.secret = self._auto_detect_secret()

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._headers(),
            timeout=httpx.Timeout(10.0),
        )

    @staticmethod
    def _auto_detect_url() -> str | None:
        path = _find_clash_config()
        if path:
            cfg = _parse_clash_config(path)
            if "external_controller" in cfg:
                # Clash config stores "127.0.0.1:9097" — already a URL host:port
                addr = cfg["external_controller"]
                return f"http://{addr}"
        return None

    @staticmethod
    def _auto_detect_secret() -> str | None:
        path = _find_clash_config()
        if path:
            cfg = _parse_clash_config(path)
            return cfg.get("secret")
        return None

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
        # Some endpoints return 204 No Content
        return resp.json() if resp.content else {}

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
        resp = await self._client.put("/configs", json={}, params={"force": "true"})
        if resp.status_code >= 400:
            raise MihomoError(f"PUT /configs → {resp.status_code}: {resp.text[:200]}")

    # ── rules ────────────────────────────────────────────────

    async def get_rules(self) -> dict[str, Any]:
        """Return routing rules."""
        return await self._request("GET", "/rules")
