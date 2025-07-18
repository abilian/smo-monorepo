# Copyright (c) 2023-2025, Abilian SAS
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import nox

# Minimal version is 3.10
PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]

SUB_REPOS = [
    "smo-core",
    "smo-cli",
]

nox.options.default_venv_backend = "uv|virtualenv"


nox.options.sessions = [
    "lint",
    "pytest",
]


@nox.session
def lint(session: nox.Session):
    """Run linters."""
    session.run("uv", "run", "--active", "ruff", "check")


@nox.session(python=PYTHON_VERSIONS)
def pytest(session: nox.Session) -> None:
    session.run("uv", "run", "--active", "pytest")


@nox.session(python=PYTHON_VERSIONS)
@nox.parametrize("sub_repo", SUB_REPOS)
def pytest_packages(session: nox.Session, sub_repo: str) -> None:
    run_subsession(session, sub_repo)


def run_subsession(session, sub_repo) -> None:
    name = session.name.split("(")[0]
    print(f"\nRunning session: {session.name} in subrepo: {sub_repo}\n")
    with session.chdir(sub_repo):
        session.run("nox", "-e", name, external=True)
    print()
