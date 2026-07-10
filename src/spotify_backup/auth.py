from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Event
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import requests

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    server: "OAuthCallbackServer"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        self.server.auth_code = params.get("code", [None])[0]
        self.server.auth_state = params.get("state", [None])[0]
        self.server.auth_error = params.get("error", [None])[0]
        self.server.done.set()

        self.send_response(200 if self.server.auth_code else 400)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        message = "Spotify authorization complete. You can close this tab.\n"
        if self.server.auth_error:
            message = f"Spotify authorization failed: {self.server.auth_error}\n"
        self.wfile.write(message.encode("utf-8"))

    def log_message(self, format: str, *args: object) -> None:
        return


class OAuthCallbackServer(HTTPServer):
    auth_code: str | None = None
    auth_state: str | None = None
    auth_error: str | None = None

    def __init__(self, server_address: tuple[str, int]) -> None:
        super().__init__(server_address, OAuthCallbackHandler)
        self.done = Event()


def code_verifier() -> str:
    return secrets.token_urlsafe(64)[:128]


def code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def build_authorize_url(
    *,
    client_id: str,
    redirect_uri: str,
    scopes: tuple[str, ...],
    verifier: str,
    state: str,
) -> str:
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "state": state,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge(verifier),
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code(
    *,
    client_id: str,
    redirect_uri: str,
    code: str,
    verifier: str,
) -> dict[str, Any]:
    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": client_id,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": verifier,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    response.raise_for_status()
    token = response.json()
    token["expires_at"] = int(time.time()) + int(token.get("expires_in", 3600)) - 60
    return token


def refresh_access_token(*, client_id: str, refresh_token: str) -> dict[str, Any]:
    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    response.raise_for_status()
    token = response.json()
    token["expires_at"] = int(time.time()) + int(token.get("expires_in", 3600)) - 60
    if "refresh_token" not in token:
        token["refresh_token"] = refresh_token
    return token


def save_token(path: Path, token: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(token, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)


def load_token(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def valid_access_token(*, client_id: str, token_file: Path) -> str:
    token = load_token(token_file)
    if int(token.get("expires_at", 0)) <= int(time.time()):
        token = refresh_access_token(client_id=client_id, refresh_token=token["refresh_token"])
        save_token(token_file, token)
    return token["access_token"]


def run_login(
    *,
    client_id: str,
    redirect_uri: str,
    scopes: tuple[str, ...],
    token_file: Path,
    open_browser: bool = True,
    timeout_seconds: int = 300,
) -> dict[str, Any]:
    parsed = urlparse(redirect_uri)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    verifier = code_verifier()
    state = secrets.token_urlsafe(24)
    authorize_url = build_authorize_url(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scopes=scopes,
        verifier=verifier,
        state=state,
    )

    server = OAuthCallbackServer((host, port))
    server.timeout = 1
    print("Open this URL to authorize Spotify:")
    print(authorize_url)
    if open_browser:
        webbrowser.open(authorize_url)

    started = time.time()
    while not server.done.is_set():
        server.handle_request()
        if time.time() - started > timeout_seconds:
            raise TimeoutError("Timed out waiting for Spotify OAuth callback.")

    if server.auth_error:
        raise RuntimeError(f"Spotify authorization failed: {server.auth_error}")
    if not server.auth_code:
        raise RuntimeError("Spotify authorization did not return a code.")
    if server.auth_state != state:
        raise RuntimeError("Spotify authorization state mismatch.")

    token = exchange_code(
        client_id=client_id,
        redirect_uri=redirect_uri,
        code=server.auth_code,
        verifier=verifier,
    )
    save_token(token_file, token)
    return token
