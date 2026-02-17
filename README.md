# sysml-v2

CLI toolchain and Python library for SysML v2 model development and analysis.

Install once, use across all your MBSE projects. Provides project scaffolding, model validation, API server management, and a Python client for the SysML v2 REST API.

## Prerequisites

| Tool | Install |
|------|---------|
| **Python** >= 3.12 | [python.org](https://www.python.org/) |
| **Docker** | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| **VSCode** | [code.visualstudio.com](https://code.visualstudio.com/) |
| **git** | pre-installed on macOS/Linux |

## Install

```bash
# From GitHub (recommended)
uv tool install git+https://github.com/YOUR_USER/sysml-v2.git

# From a local clone
git clone https://github.com/YOUR_USER/sysml-v2.git
uv tool install ./sysml-v2

# Or install into an existing project's venv
uv pip install git+https://github.com/YOUR_USER/sysml-v2.git
```

## Quick Start

```bash
# Create a new project
mkdir my-satellite && cd my-satellite
sysml init

# Open in VS Code (installs Syside Editor extension for .sysml support)
code .

# Start the local API server
sysml serve up

# Validate your models
sysml validate models/

# Stop the server
sysml serve down
```

## CLI Commands

### `sysml init [PATH]`

Scaffold a new SysML v2 project with models, notebooks, VS Code config, Docker setup, and the standard library.

```bash
sysml init                          # current directory
sysml init my-project               # new directory
sysml init --backend gearshift      # use Gearshift backend instead of Flexo
sysml init -y                       # skip prompts
```

### `sysml serve <up|down|logs|pull|status>`

Manage the local Docker-based API server.

```bash
sysml serve up                      # start (Flexo MMS on port 8083)
sysml serve status                  # check if running
sysml serve logs                    # tail logs
sysml serve down                    # stop
sysml serve --backend gearshift up  # use Gearshift backend
```

### `sysml validate [PATH]`

Validate `.sysml` files.

```bash
sysml validate models/              # validate a directory (recursive)
sysml validate models/vehicle.sysml # validate a single file
sysml validate --server models/     # use Gearshift server for deeper analysis
```

## Python Library

```python
from sysml_v2 import SysMLClient, load, loads, find_models

# API client
with SysMLClient() as client:       # reads server URL from sysml.toml
    projects = client.list_projects()
    elements = client.get_elements(project_id, commit_id)

# Parse .sysml files
model = load("models/vehicle.sysml")
files = find_models("models/")
```

## Project Configuration

`sysml init` creates a `sysml.toml` in your project root:

```toml
[server]
backend = "flexo"                   # or "gearshift"
url = "http://localhost:8083"

[library]
path = "lib/SysML-v2-Release"

[validate]
mode = "local"                      # or "server"
```

## Server Backends

| Backend | Description | Status |
|---------|-------------|--------|
| **flexo** (default) | [Flexo MMS](https://github.com/Open-MBEE/flexo-mms-deployment) — OpenMBEE SysML v2 API, port 8083 | Stable |
| **gearshift** | [Gearshift KerML Service](https://github.com/open-mbee/gearshift-kerml-service) — KerML parser, Z3 solver, port 9000 | Pre-release |

## Optional Extras

```bash
# Jupyter notebooks
pip install sysml-v2[jupyter]

# Sensmetry Syside Automator (commercial, requires license)
pip install sysml-v2[syside]
```

## Resources

- [SysML v2 Specification (OMG)](https://www.omg.org/spec/SysML/2.0/)
- [SysML v2 Standard Library](https://github.com/Systems-Modeling/SysML-v2-Release)
- [Syside Editor (VS Code)](https://marketplace.visualstudio.com/items?itemName=sensmetry.syside-editor)
- [Gearshift KerML Service](https://github.com/open-mbee/gearshift-kerml-service)
- [sysml2py](https://pypi.org/project/sysml2py/)
- [SysML v2 API Cookbook](https://github.com/Systems-Modeling/SysML-v2-API-Cookbook)
