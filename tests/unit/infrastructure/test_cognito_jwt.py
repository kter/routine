"""Unit tests for Cognito JWT verification (verify_token)."""

import os
from collections.abc import Generator
from unittest.mock import patch

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwk as jose_jwk
from jose import jwt

from routineops.config.settings import clear_settings_caches
from routineops.infrastructure.auth import cognito

CLIENT_ID = "unit-test-client-id"
KID = "unit-test-kid"


def _generate_private_pem() -> str:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


PRIVATE_PEM = _generate_private_pem()
OTHER_PRIVATE_PEM = _generate_private_pem()


def _public_jwk(private_pem: str, kid: str) -> dict[str, object]:
    key = jose_jwk.construct(private_pem, algorithm="RS256")
    public = key.public_key().to_dict()
    public["kid"] = kid
    return public


JWKS = {"keys": [_public_jwk(PRIVATE_PEM, KID)]}


def _encode_token(
    claims: dict[str, object],
    *,
    private_pem: str = PRIVATE_PEM,
    kid: str = KID,
) -> str:
    return jwt.encode(claims, private_pem, algorithm="RS256", headers={"kid": kid})


@pytest.fixture(autouse=True)
def _configured_settings() -> Generator[None, None, None]:
    with patch.dict(
        os.environ,
        {
            "COGNITO_CLIENT_ID": CLIENT_ID,
            "COGNITO_JWKS_URL": "https://cognito.example.com/jwks.json",
            "TEST_MODE": "false",
        },
        clear=False,
    ):
        clear_settings_caches()
        yield
    clear_settings_caches()


@pytest.fixture
def _stubbed_jwks() -> Generator[None, None, None]:
    with patch.object(cognito, "_get_jwks", return_value=JWKS):
        yield


@pytest.mark.usefixtures("_stubbed_jwks")
class TestVerifyTokenSuccess:
    def test_accepts_token_with_matching_aud_claim(self) -> None:
        token = _encode_token({"sub": "user-1", "aud": CLIENT_ID})

        claims = cognito.verify_token(token)

        assert claims["sub"] == "user-1"
        assert claims["aud"] == CLIENT_ID

    def test_accepts_token_with_matching_client_id_claim(self) -> None:
        token = _encode_token({"sub": "user-2", "client_id": CLIENT_ID})

        claims = cognito.verify_token(token)

        assert claims["sub"] == "user-2"

    def test_returns_custom_claims(self) -> None:
        token = _encode_token(
            {
                "sub": "user-3",
                "aud": CLIENT_ID,
                "custom:tenant_id": "00000000-0000-0000-0000-000000000042",
            }
        )

        claims = cognito.verify_token(token)

        assert claims["custom:tenant_id"] == "00000000-0000-0000-0000-000000000042"


@pytest.mark.usefixtures("_stubbed_jwks")
class TestVerifyTokenFailure:
    def test_rejects_token_with_unknown_kid(self) -> None:
        token = _encode_token({"sub": "user-1", "aud": CLIENT_ID}, kid="unknown-kid")

        with pytest.raises(ValueError, match="Public key not found for kid"):
            cognito.verify_token(token)

    def test_rejects_token_signed_by_another_key(self) -> None:
        token = _encode_token(
            {"sub": "user-1", "aud": CLIENT_ID},
            private_pem=OTHER_PRIVATE_PEM,
        )

        with pytest.raises(ValueError, match="Signature verification failed"):
            cognito.verify_token(token)

    def test_rejects_token_with_tampered_payload(self) -> None:
        token = _encode_token({"sub": "user-1", "aud": CLIENT_ID})
        forged_payload = jwt.encode(
            {"sub": "attacker", "aud": CLIENT_ID},
            PRIVATE_PEM,
            algorithm="RS256",
            headers={"kid": KID},
        ).split(".")[1]
        header, _payload, signature = token.split(".")
        tampered = ".".join([header, forged_payload, signature])

        with pytest.raises(ValueError, match="Signature verification failed"):
            cognito.verify_token(tampered)

    def test_rejects_token_with_audience_mismatch(self) -> None:
        token = _encode_token({"sub": "user-1", "aud": "someone-else"})

        with pytest.raises(ValueError, match="Token audience mismatch"):
            cognito.verify_token(token)

    def test_rejects_malformed_token(self) -> None:
        with pytest.raises(ValueError, match="Invalid JWT"):
            cognito.verify_token("not-a-jwt")

    def test_rejects_when_jwks_payload_is_invalid(self) -> None:
        token = _encode_token({"sub": "user-1", "aud": CLIENT_ID})

        with patch.object(cognito, "_get_jwks", return_value={"keys": "broken"}):
            with pytest.raises(ValueError, match="JWKS payload is invalid"):
                cognito.verify_token(token)

    def test_rejects_when_client_id_is_not_configured(self) -> None:
        token = _encode_token({"sub": "user-1", "aud": CLIENT_ID})

        env = {k: v for k, v in os.environ.items() if k != "COGNITO_CLIENT_ID"}
        with patch.dict(os.environ, env, clear=True):
            clear_settings_caches()
            with pytest.raises(ValueError, match="COGNITO_CLIENT_ID is not configured"):
                cognito.verify_token(token)
        clear_settings_caches()


class TestGetJwks:
    def test_raises_when_jwks_url_is_not_configured(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "COGNITO_JWKS_URL"}
        with patch.dict(os.environ, env, clear=True):
            clear_settings_caches()
            cognito._get_jwks.cache_clear()
            with pytest.raises(ValueError, match="COGNITO_JWKS_URL is not configured"):
                cognito._get_jwks()
        clear_settings_caches()
        cognito._get_jwks.cache_clear()
