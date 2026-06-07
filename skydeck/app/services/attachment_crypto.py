"""Encryption helpers for message attachments."""

from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings
from app.core.errors import StorageError

_MESSAGE_AAD = b"skydeck-message-attachment-v1"
_PROFILE_PICTURE_AAD = b"skydeck-user-profile-picture-v1"
_ALG = "AES-256-GCM"


@dataclass(frozen=True)
class EncryptedAttachmentBytes:
    """Encrypted attachment payload plus the metadata required to decrypt it."""

    ciphertext: bytes
    encrypted_key: str
    key_nonce: str
    content_nonce: str
    key_id: str
    alg: str = _ALG


def encrypt_attachment(plaintext: bytes) -> EncryptedAttachmentBytes:
    """Encrypt one attachment with a random data key and protected key metadata."""
    return _encrypt_bytes(plaintext, aad=_MESSAGE_AAD)


def encrypt_profile_picture(plaintext: bytes) -> EncryptedAttachmentBytes:
    """Encrypt one profile picture with a random data key."""
    return _encrypt_bytes(plaintext, aad=_PROFILE_PICTURE_AAD)


def _encrypt_bytes(plaintext: bytes, *, aad: bytes) -> EncryptedAttachmentBytes:
    """Encrypt bytes with a random data key and protected key metadata."""
    data_key = os.urandom(32)
    content_nonce = os.urandom(12)
    key_nonce = os.urandom(12)

    ciphertext = AESGCM(data_key).encrypt(content_nonce, plaintext, aad)
    encrypted_key = AESGCM(_master_key()).encrypt(key_nonce, data_key, aad)

    return EncryptedAttachmentBytes(
        ciphertext=ciphertext,
        encrypted_key=_b64(encrypted_key),
        key_nonce=_b64(key_nonce),
        content_nonce=_b64(content_nonce),
        key_id=_key_id(),
    )


def decrypt_attachment(
    *,
    ciphertext: bytes,
    encrypted_key: str,
    key_nonce: str,
    content_nonce: str,
) -> bytes:
    """Decrypt one stored message attachment in memory."""
    return _decrypt_bytes(
        ciphertext=ciphertext,
        encrypted_key=encrypted_key,
        key_nonce=key_nonce,
        content_nonce=content_nonce,
        aad=_MESSAGE_AAD,
    )


def decrypt_profile_picture(
    *,
    ciphertext: bytes,
    encrypted_key: str,
    key_nonce: str,
    content_nonce: str,
) -> bytes:
    """Decrypt one stored profile picture in memory."""
    return _decrypt_bytes(
        ciphertext=ciphertext,
        encrypted_key=encrypted_key,
        key_nonce=key_nonce,
        content_nonce=content_nonce,
        aad=_PROFILE_PICTURE_AAD,
    )


def _decrypt_bytes(
    *,
    ciphertext: bytes,
    encrypted_key: str,
    key_nonce: str,
    content_nonce: str,
    aad: bytes,
) -> bytes:
    """Decrypt encrypted bytes in memory."""
    try:
        data_key = AESGCM(_master_key()).decrypt(_unb64(key_nonce), _unb64(encrypted_key), aad)
        return AESGCM(data_key).decrypt(_unb64(content_nonce), ciphertext, aad)
    except (InvalidTag, ValueError) as exc:
        raise StorageError("Attachment decryption failed") from exc


def _master_secret() -> str:
    """Return the configured attachment master secret."""
    return (
        settings.FILE_ENCRYPTION_MASTER_KEY
        or settings.MESSAGE_ATTACHMENT_MASTER_KEY
        or settings.SECRET_KEY
    )


def _master_key() -> bytes:
    """Derive a stable 256-bit AES key from the configured secret."""
    return hashlib.sha256(_master_secret().encode("utf-8")).digest()


def _key_id() -> str:
    """Return a non-secret identifier for the current master key."""
    return hashlib.sha256(_master_secret().encode("utf-8")).hexdigest()[:16]


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value.encode("ascii"))
