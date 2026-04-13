# envault

> A CLI tool for securely managing and syncing .env files across projects using encrypted local storage.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended for CLI tools):

```bash
pipx install envault
```

---

## Usage

**Initialize a vault for your project:**

```bash
envault init
```

**Store your current `.env` file:**

```bash
envault push --project myapp
```

**Pull and restore a stored `.env` file:**

```bash
envault pull --project myapp
```

**List all stored projects:**

```bash
envault list
```

All secrets are encrypted at rest using AES-256 encryption. A master password is required on first use and cached securely in your system keychain.

---

## How It Works

1. `envault` encrypts your `.env` file using a master password derived key.
2. The encrypted file is stored in a local vault (`~/.envault/`).
3. You can sync the vault directory across machines using any file sync tool (e.g., Dropbox, iCloud, rsync).

---

## Requirements

- Python 3.8+
- `cryptography`
- `click`
- `keyring`

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*Contributions and issues are welcome. Please open a GitHub issue or submit a pull request.*