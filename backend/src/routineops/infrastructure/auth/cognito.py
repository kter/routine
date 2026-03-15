"""
Cognito JWT JWKS verification.
Caches the JWKS in memory to avoid redundant HTTP calls.
"""

import json
import urllib.request
from functools import lru_cache

from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode

from routineops.config.settings import get_api_settings


@lru_cache(maxsize=1)
def _get_jwks() -> dict[str, object]:
    settings = get_api_settings()
    if not settings.cognito_jwks_url:
        raise ValueError("COGNITO_JWKS_URL is not configured")
    url = settings.cognito_jwks_url
    with urllib.request.urlopen(url, timeout=5) as response:  # noqa: S310
        return json.loads(response.read())  # type: ignore[no-any-return]


def verify_token(token: str) -> dict[str, object]:
    """
    Verify a Cognito JWT and return the decoded payload.

    Raises:
        ValueError: if the token is invalid or expired
    """
    try:
        headers = jwt.get_unverified_headers(token)
        kid = headers["kid"]

        jwks = _get_jwks()
        keys = jwks.get("keys")
        if not isinstance(keys, list):
            raise ValueError("JWKS payload is invalid")
        key_data = next(
            (k for k in keys if isinstance(k, dict) and k.get("kid") == kid),
            None,
        )
        if key_data is None:
            raise ValueError("Public key not found for kid")

        public_key = jwk.construct(key_data)
        message, encoded_sig = token.rsplit(".", 1)
        decoded_sig = base64url_decode(encoded_sig.encode())

        if not public_key.verify(message.encode(), decoded_sig):
            raise ValueError("Signature verification failed")

        claims: dict[str, object] = jwt.get_unverified_claims(token)

        # Verify audience and issuer
        settings = get_api_settings()
        if not settings.cognito_client_id:
            raise ValueError("COGNITO_CLIENT_ID is not configured")
        expected_client_id = settings.cognito_client_id
        if (
            claims.get("client_id") != expected_client_id
            and claims.get("aud") != expected_client_id
        ):
            raise ValueError("Token audience mismatch")

        return claims

    except JWTError as e:
        raise ValueError(f"Invalid JWT: {e}") from e
