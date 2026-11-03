import asyncio
import hashlib

import pytest
from fastapi import HTTPException

from app.database.queries.password_reset import _hash_reset_token
from app.routes.auth import exchange_google_oauth_token, proxy_profile_image


class StubRequest:
    def __init__(self, session: dict[str, str]) -> None:
        self.session = session


def test_reset_tokens_are_stored_as_sha256_digests() -> None:
    token = "one-time-reset-token"

    digest = _hash_reset_token(token)

    assert digest == hashlib.sha256(token.encode("utf-8")).hexdigest()
    assert digest != token


def test_oauth_exchange_consumes_the_pending_token_once() -> None:
    request = StubRequest({"oauth_access_token": "signed-jwt"})

    response = asyncio.run(exchange_google_oauth_token(request))  # type: ignore[arg-type]

    assert response.access_token == "signed-jwt"
    assert request.session == {}

    with pytest.raises(HTTPException) as error:
        asyncio.run(exchange_google_oauth_token(request))  # type: ignore[arg-type]
    assert error.value.status_code == 401


@pytest.mark.parametrize(
    "url",
    [
        "http://lh3.googleusercontent.com/avatar.png",
        "https://127.0.0.1/avatar.png",
        "https://example.com/avatar.png",
        "https://lh3.googleusercontent.com.evil.example/avatar.png",
    ],
)
def test_profile_image_proxy_rejects_untrusted_urls(url: str) -> None:
    with pytest.raises(HTTPException) as error:
        asyncio.run(proxy_profile_image(url))

    assert error.value.status_code == 400
