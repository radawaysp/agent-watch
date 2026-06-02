# Security Policy

Agent Watch reads public web sources and writes local Markdown files. Treat configuration files as public by default, and keep secrets in environment variables.

Please do not include API keys, generated state databases, private vault paths, or private report contents in issues or pull requests. The repository ignores `.env`, `data/`, `notes/`, and SQLite files by default.

If you find a security issue, open a private report through GitHub security advisories when available. If this repository is mirrored elsewhere, contact the maintainer listed in that mirror.

