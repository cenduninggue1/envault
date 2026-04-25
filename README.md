# envault

> A CLI tool to securely manage and sync environment variables across projects using encrypted local vaults.

---

## Installation

```bash
pip install envault
```

Or install from source:

```bash
git clone https://github.com/yourname/envault.git && cd envault && pip install .
```

---

## Usage

Initialize a new vault in your project:

```bash
envault init
```

Add and retrieve environment variables:

```bash
envault set DATABASE_URL "postgres://localhost:5432/mydb"
envault get DATABASE_URL
```

Load all vault variables into your shell session:

```bash
eval $(envault load)
```

Sync your vault across projects:

```bash
envault sync --target ../other-project
```

List all stored keys:

```bash
envault list
```

---

## How It Works

envault stores your environment variables in an AES-encrypted local vault file (`.envault`). Each vault is protected by a master password and can be shared or synced across projects without exposing sensitive values.

> **Note:** Never commit your `.envault` file or master password to version control. Add `.envault` to your `.gitignore`.

---

## License

This project is licensed under the [MIT License](LICENSE).