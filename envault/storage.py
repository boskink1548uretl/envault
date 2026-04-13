"""Local encrypted storage management for envault."""

import json
import os
from pathlib import Path

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_DIR = Path.home() / ".envault"
VAULT_FILE = "vault.enc"


def get_vault_path(vault_dir: Path = DEFAULT_VAULT_DIR) -> Path:
    """Return the path to the encrypted vault file."""
    return vault_dir / VAULT_FILE


def load_vault(password: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> dict:
    """Load and decrypt the vault. Returns an empty dict if vault doesn't exist."""
    vault_path = get_vault_path(vault_dir)
    if not vault_path.exists():
        return {}
    token = vault_path.read_text(encoding="utf-8").strip()
    if not token:
        return {}
    plaintext = decrypt(token, password)
    return json.loads(plaintext)


def save_vault(data: dict, password: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> None:
    """Encrypt and save the vault data to disk."""
    vault_dir.mkdir(parents=True, exist_ok=True)
    vault_path = get_vault_path(vault_dir)
    plaintext = json.dumps(data)
    token = encrypt(plaintext, password)
    vault_path.write_text(token, encoding="utf-8")
    os.chmod(vault_path, 0o600)


def vault_exists(vault_dir: Path = DEFAULT_VAULT_DIR) -> bool:
    """Check whether a vault file exists."""
    return get_vault_path(vault_dir).exists()
