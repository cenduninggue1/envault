"""Tests for envault.crypto module."""

import pytest
from envault.crypto import encrypt, decrypt


def test_encrypt_returns_bytes():
    result = encrypt("hello", "password")
    assert isinstance(result, bytes)


def test_encrypt_decrypt_roundtrip():
    plaintext = "SECRET_KEY=abc123"
    password = "strongpassword"
    data = encrypt(plaintext, password)
    recovered = decrypt(data, password)
    assert recovered == plaintext


def test_different_encryptions_differ():
    """Each encryption call should produce different ciphertext (random salt)."""
    data1 = encrypt("same", "pass")
    data2 = encrypt("same", "pass")
    assert data1 != data2


def test_decrypt_wrong_password_raises():
    data = encrypt("secret", "correct")
    with pytest.raises(ValueError, match="Invalid password"):
        decrypt(data, "wrong")


def test_decrypt_tampered_data_raises():
    data = bytearray(encrypt("secret", "pass"))
    data[20] ^= 0xFF  # flip some bits
    with pytest.raises(ValueError):
        decrypt(bytes(data), "pass")
