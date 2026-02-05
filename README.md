# SysML v2 Workspace

A reproducible development environment for model-based systems engineering with [SysML v2](https://www.omg.org/spec/SysML/2.0/).

Provides: textual model editing in VSCode, Python interoperability, Jupyter notebooks, and a local API server.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| **uv** | >= 0.9 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Docker** | >= 24 | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| **VSCode** | latest | [code.visualstudio.com](https://code.visualstudio.com/) |
| **git** | any | pre-installed on macOS/Linux |

## Quick Start

```bash
git clone <this-repo-url> && cd sysml-v2
make setup
```

This runs `setup.sh`, which:

1. Checks that `uv`, `docker`, and `git` are installed
2. Installs recommended VSCode extensions (Syside Editor, Python, Jupyter, Docker)
3. Creates a Python 3.12+ virtual environment and installs dependencies
4. Clones the [SysML v2 standard library](https://github.com/Systems-Modeling/SysML-v2-Release) into `lib/`
5. Clones the [API Cookbook](https://github.com/Systems-Modeling/SysML-v2-API-Cookbook) notebooks into `notebooks/api-cookbook/`
6. Pulls Docker images for the local API server

Then open the workspace in VSCode:

```bash
code .
```

## Project Structure

```
.
├── models/                    SysML v2 model files (.sysml)
│   └── examples/              Starter models (vehicle, requirements)
├── notebooks/                 Jupyter notebooks
│   ├── getting-started.ipynb  Intro notebook — sysml2py + API usage
│   └── api-cookbook/           OMG API Cookbook (cloned by setup.sh)
├── scripts/                   Python automation scripts
├── lib/
│   └── SysML-v2-Release/      Standard library (cloned by setup.sh)
├── docker/
│   └── docker-compose.yml     Local API server stack
├── .vscode/                   Workspace settings + extension recommendations
├── pyproject.toml             Python dependencies (managed by uv)
├── setup.sh                   Bootstrap script
└── Makefile                   Convenience commands
```

## Common Commands

| Command | Description |
|---------|-------------|
| `make setup` | Full bootstrap (first time) |
| `make install` | Install core Python dependencies |
| `make install-all` | Install all dependencies including optional extras |
| `make server-up` | Start the SysML v2 API server (port 9000) |
| `make server-down` | Stop the API server |
| `make server-logs` | Tail the API server logs |
| `make lab` | Launch JupyterLab |
| `make test` | Run Python tests |
| `make lint` | Lint Python files with ruff |
| `make clean` | Remove venv, caches, Docker volumes |
| `make help` | Show all commands |

## Editing SysML v2 Models

The [Syside Editor](https://marketplace.visualstudio.com/items?itemName=sensmetry.syside-editor) extension provides:

- Real-time validation and diagnostics
- Semantic highlighting and auto-completion
- Go-to-definition and find-all-references
- Documentation on hover
- Auto-formatting on save

Open any `.sysml` file in `models/` to get started. See `models/examples/vehicle.sysml` for a part decomposition example and `models/examples/requirements.sysml` for requirements modeling.

## Python Integration

### Core (installed by default)

- **[sysml2py](https://pypi.org/project/sysml2py/)** — Open-source library for constructing SysML v2 elements in Python
- **[httpx](https://www.python-httpx.org/)** — HTTP client for direct API calls
- **[JupyterLab](https://jupyter.org/)** — Notebook environment

### Optional Extras

```bash
# Sensmetry Syside Automator (requires license key)
export SYSIDE_LICENSE_KEY="your-key-here"
uv sync --extra syside

# Official OMG API client (from GitHub)
uv sync --extra api-client

# Everything
uv sync --all-extras
```

**Syside Automator** ([docs](https://docs.sensmetry.com/automator/)) is the most capable Python library for SysML v2. It operates directly on `.sysml` files without a model server, supports model traversal, expression evaluation, and automation workflows. Requires a [Sensmetry license](https://sensmetry.com/pricing/) (30-day free trial available).

## Local API Server

The Docker Compose stack runs PostgreSQL + the SysML v2 REST API server:

```bash
make server-up          # Start (detached)
make server-logs        # Watch logs
open http://localhost:9000/docs/   # Swagger UI
make server-down        # Stop
```

The API Cookbook notebooks in `notebooks/api-cookbook/` are designed to run against this server.

### Alternative: Full Stack with JupyterLab

For a more complete local environment including a pre-configured JupyterLab instance:

```bash
git clone https://github.com/gorenje/sysmlv2-jupyter-docker.git docker/sysmlv2-server
cd docker/sysmlv2-server && make spin-up
```

This runs PostgreSQL + API server (port 9000) + JupyterLab (port 8888).

## Resources

- [SysML v2 Specification (OMG)](https://www.omg.org/spec/SysML/2.0/)
- [SysML v2 Release Repository](https://github.com/Systems-Modeling/SysML-v2-Release) — spec docs, standard library, example models
- [SysML v2 Pilot Implementation](https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation) — Eclipse-based reference implementation
- [Syside Editor](https://marketplace.visualstudio.com/items?itemName=sensmetry.syside-editor) — VSCode extension
- [Syside Automator Docs](https://docs.sensmetry.com/automator/) — Python library documentation
- [Sysand](https://github.com/sensmetry/sysand) — SysML v2 package manager
- [sysml2py](https://pypi.org/project/sysml2py/) — Open-source Python library
- [API Cookbook](https://github.com/Systems-Modeling/SysML-v2-API-Cookbook) — Jupyter notebook recipes
