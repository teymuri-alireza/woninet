# Contributing to woninet

Thank you for considering contributing to **woninet**!

Whether you're fixing a bug, improving the documentation, or implementing a new feature, your contributions are appreciated.

## Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/teymuri-alireza/woninet
cd woninet
```

### 2. Create a virtual environment

#### Linux/macOS

```bash
python3 -m venv --copies ../venv
source ../venv/bin/activate
```

#### Windows (PowerShell)

```powershell
py -m venv ..\venv
..\venv\Scripts\Activate.ps1
```

> **Linux:** `--copies` is recommended because Linux capabilities are applied directly to the Python executable.

### 3. Install woninet for development

```bash
pip install -e ".[test]"
```

This installs the project in editable mode together with the testing dependencies.

### 4. Configure ICMP permissions (Linux)

To allow raw ICMP without running as root:

```bash
sudo setcap cap_net_raw=eip ../venv/bin/python3
```

Alternatively, you may run the application with `sudo`, although this is not recommended.

### 5. Run woninet

```bash
woninet
```

## Running Tests

Run the complete test suite before opening a Pull Request.

```bash
pytest
```

You may also execute individual test files.

```bash
pytest tests/test_api.py
```

## Code Style

Please ensure that all changes pass formatting and linting.

```bash
ruff format .
ruff check .
```

General guidelines:

- Use type annotations.
- Prefer absolute imports.
- Keep functions focused and readable.
- Document public APIs when appropriate.

## Project Structure

```text
woninet/
├── core/
├── database/
├── server/
├── utilities/
└── main.py
```

## Branching Model

The project uses a lightweight Git workflow.

- **main** — stable releases
- **dev** — active development

Create feature branches from **dev**.

Pull Requests should target **dev**.

Releases are prepared using release branches and merged into **main**.

## Commit Messages

Write concise commit messages in the imperative mood.

Examples:

```
Add alert persistence
Fix ARP timeout handling
Refactor database session management
Update documentation
```

## Pull Requests

Before submitting a Pull Request:

- Ensure all tests pass.
- Run Ruff formatting and linting.
- Update documentation if necessary.
- Update the CHANGELOG when the change affects users.
- Keep Pull Requests focused on a single logical change.
- Link related GitHub issues when applicable.

---

Thank you for helping improve **woninet**.
