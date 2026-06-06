# Contributing to woninet

Thank you for considering contributing to *woninet!*
This project welcomes improvements, bug fixes, documentation updates, and new features.

To help us maintain code quality, stability, and a predictable release process, please review and follow the guidelines below.

## 1. How to Contribute

You can contribute in several ways:

- Report bugs or request features via GitHub issues
- Improve documentation
- Fix bugs
- Add new monitoring features or collectors
- Optimize performance, interval handling, or concurrency logic

All contributions small or large are appreciated.

## 2. Development Environment Setup

### 1. Clone the repository:

```shell
git clone https://github.com/teymuri-alireza/woninet
cd woninet
```

### 2. Create and activate a virtual environment:

**Note:** Create the virtual environment outside the project directory to avoid
`Multiple top-level packages discovered in a flat-layout` errors.

**Unix/Linux note:** The `--copies` flag forces Python to copy the interpreter instead of using a symbolic link.
This is required because you will apply Linux capabilities directly to the Python binary in the virtual environment.

#### Linux/macOS

```shell
python3 -m venv --copies ../venv
source ../venv/bin/activate
```

#### Windows (PowerShell)

```shell
py -m venv ..\venv
..\venv\Scripts\Activate.ps1
```

### 3. Install *woninet* locally in editable mode:

```shell
pip install -e .
```

### 4. Configure permissions for ICMP (one-time)

Grant the cap_net_raw capability to the Python interpreter inside the virtual environment so you can run woninet without sudo:

```shell
sudo setcap cap_net_raw=eip ../venv/bin/python3
```

### 5. Run the package

```shell
python3 -m woninet
```

**Alternative (not recommended):** You can run woninet with sudo instead of using setcap, but this is discouraged for security reasons:

```shell
sudo ../venv/bin/python3 -m woninet
```

## 3. Project Structure Overview

```text
woninet/
├── core/ # Monitoring engine, ARP + ICMP logic, Models
├── database/ # Database engine, ORM operation handlers, Tables + Repositories
├── server/ # FastAPI application and routes
├── utilities/ # Argument handler, Logging
└── main.py # The woninet entry point
```

## 4. Code Style

- Write type‑annotated code:

```python
def start(self) -> None:
```

- Keep imports absolute, not relative:

```python
from woninet.core.monitor import NetworkMonitorCore # Correct

from .core.monitor import NetworkMonitorCore # Incorrect
```

- Use **Ruff** for linting and formatting:

```shell
ruff check .
ruff format .
```

## 5. Commit Message Guidelines

Use Conventional Commits:

- `feat:` – new feature
- `fix:` – bug fix
- `docs:` – documentation changes
- `refactor:` – code improvements without behavior change
- `perf:` – performance optimizations
- `chore:` – maintenance, version bumps, CI tweaks

## 6. Branching Model

Use a lightwaight workflow:

- **main** – Stable releases. This branch should always contain production‑ready code
- **dev** – Active development and integration branch

Contributors should create branches from dev using the following naming conventions:

- **feature/*** – New features (e.g., `feature/add-search`)
- **fix/*** – Bug fixes (e.g., `fix/login-error`)
- **perf/*** – Performance improvements (e.g., `perf/cache-optimization`)

When your work is complete, open a Pull Request targeting the dev branch.

Changes are reviewed and tested before being merged.

## 7. Pull Request Guidelines

When opening a PR:

1. Describe what the PR does and why the change is needed
2. Link related issues (e.g., `Closes #42`)
3. Keep PRs small and focused
4. Ensure your branch is up‑to‑date with the latest dev branch before submitting

---

Thank you for making *woninet* better!
Maintainers and contributors appreciate your work.

**Update: 2026-04-30**
