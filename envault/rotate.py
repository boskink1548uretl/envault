"""Password rotation for the envault vault."""

from envault.crypto import decrypt, encrypt, derive_key
from envault.storage import load_vault, save_vault, get_vault_path


class RotationError(Exception):
    """Raised when vault password rotation fails."""


def rotate_password(old_password: str, new_password: str, home_dir=None) -> int:
    """
    Re-encrypt the entire vault with a new password.

    Decrypts every project's env block using the old password, then
    re-encrypts each one with the new password and persists the vault.

    Returns the number of projects that were re-encrypted.

    Raises RotationError if the old password is wrong or decryption fails.
    """
    vault_path = get_vault_path(home_dir=home_dir)
    data = load_vault(vault_path)

    projects = data.get("projects", {})
    updated: dict = {}

    for project_name, encrypted_blob in projects.items():
        try:
            plaintext = decrypt(encrypted_blob, old_password)
        except Exception as exc:
            raise RotationError(
                f"Failed to decrypt project '{project_name}' with the provided "
                f"old password. Rotation aborted — no changes were saved."
            ) from exc

        updated[project_name] = encrypt(plaintext, new_password)

    data["projects"] = updated
    save_vault(vault_path, data)
    return len(updated)
