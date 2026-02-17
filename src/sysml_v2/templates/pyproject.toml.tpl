[project]
name = "${project_name}"
version = "0.1.0"
description = "SysML v2 model project"
requires-python = ">=3.12"
dependencies = [
    "sysml-v2",
]

[project.optional-dependencies]
jupyter = ["jupyterlab>=4.0", "ipykernel>=6.29"]
syside = ["syside>=0.8"]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
]
