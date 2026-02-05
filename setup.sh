#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# SysML v2 Workspace — Bootstrap Script
#
# Prerequisites:
#   - uv        (https://docs.astral.sh/uv/getting-started/installation/)
#   - docker    (https://docs.docker.com/get-docker/)
#   - VSCode    (https://code.visualstudio.com/)
#   - git
#
# Usage:
#   chmod +x setup.sh && ./setup.sh
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== SysML v2 Workspace Setup ==="
echo ""

# ---------------------------------------------------------------------------
# 1. Check prerequisites
# ---------------------------------------------------------------------------
check_command() {
    if ! command -v "$1" &>/dev/null; then
        echo "ERROR: '$1' is not installed. $2"
        exit 1
    fi
}

check_command uv    "Install from https://docs.astral.sh/uv/getting-started/installation/"
check_command docker "Install from https://docs.docker.com/get-docker/"
check_command git    "Install git for your platform."

echo "[1/6] Prerequisites OK (uv, docker, git)"

# ---------------------------------------------------------------------------
# 2. Install VSCode extensions
# ---------------------------------------------------------------------------
if command -v code &>/dev/null; then
    echo "[2/6] Installing recommended VSCode extensions..."
    code --install-extension sensmetry.syside-editor  --force 2>/dev/null || true
    code --install-extension ms-python.python         --force 2>/dev/null || true
    code --install-extension ms-toolsai.jupyter       --force 2>/dev/null || true
    code --install-extension ms-azuretools.vscode-docker --force 2>/dev/null || true
else
    echo "[2/6] SKIP: 'code' CLI not found — install VSCode extensions manually."
    echo "       Recommended: sensmetry.syside-editor, ms-python.python, ms-toolsai.jupyter"
fi

# ---------------------------------------------------------------------------
# 3. Set up Python environment
# ---------------------------------------------------------------------------
echo "[3/6] Setting up Python environment with uv..."
uv sync

echo "       To also install the Syside Automator (requires license key):"
echo "         uv sync --extra syside"
echo "       To install the OMG API client:"
echo "         uv sync --extra api-client"

# ---------------------------------------------------------------------------
# 4. Clone the SysML v2 standard library
# ---------------------------------------------------------------------------
if [ ! -d "lib/SysML-v2-Release" ]; then
    echo "[4/6] Cloning SysML v2 standard library (2025-12 release)..."
    git clone --depth 1 https://github.com/Systems-Modeling/SysML-v2-Release.git lib/SysML-v2-Release
else
    echo "[4/6] Standard library already present at lib/SysML-v2-Release"
fi

# ---------------------------------------------------------------------------
# 5. Clone the API Cookbook notebooks
# ---------------------------------------------------------------------------
if [ ! -d "notebooks/api-cookbook" ]; then
    echo "[5/6] Cloning SysML v2 API Cookbook notebooks..."
    git clone --depth 1 https://github.com/Systems-Modeling/SysML-v2-API-Cookbook.git notebooks/api-cookbook
else
    echo "[5/6] API Cookbook already present at notebooks/api-cookbook"
fi

# ---------------------------------------------------------------------------
# 6. Pull Docker images for the API server
# ---------------------------------------------------------------------------
echo "[6/6] Pulling Docker images for the local API server..."
docker compose -f docker/docker-compose.yml pull 2>/dev/null || {
    echo "       WARNING: Could not pull Docker images. Docker may not be running."
    echo "       You can pull them later with: make server-pull"
}

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "=== Setup complete ==="
echo ""
echo "Quick start:"
echo "  make server-up     Start the SysML v2 API server (http://localhost:9000)"
echo "  make lab           Launch JupyterLab"
echo "  make help          Show all available commands"
echo ""
echo "Open this folder in VSCode to start editing .sysml files:"
echo "  code ."
