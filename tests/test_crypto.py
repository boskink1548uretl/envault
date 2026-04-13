"""Unit tests for envault.crypto module."""

import pytest
from envault.crypto import encrypt, decrypt


def test_encrypt_returns_string():
    token = encrypt("SECRET=abc", "password123")
    assert isinstance(token, str)
    assert len(token) > 0


def test_decrypt_roundtrip():
    plaintext = "API_KEY=supersecret\nDB_PASS=hunter2"
    password = "my-secure-passphrase"
    token = encrypt(plaintext, password)
    result = decrypt(token, password)
    assert result == plaintext


def test_decrypt_wrong_password_raises():
    token = encrypt("SECRET=value", "correct-password")
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, "wrong-password")


def test_decrypt_invalid_token_raises():
    with pytest.raises(ValueError):
        decrypt("not-a-valid-token!!", "password")


def test_encrypt_produces_unique_tokens():
    """Each encryption call should produce a different ciphertext (random nonce/salt)."""
    plaintext = "KEY=value"
    password = "pass"
    token1 = encrypt(plaintext, password)
    token2 = encrypt(plaintext, password)
    assert token1 != token2


def test_empty_string_roundtrip():
    token = encrypt("", "passphrase")
    assert decrypt(token, "passphrase") == ""
