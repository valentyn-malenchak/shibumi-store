"""
Module to manage shell-oriented subprocesses and organizing executable
Python code into CLI-invokable tasks.
"""

from invoke import Context, task


@task
def install(ctx: Context, group: str | None = None) -> None:
    """Installs project's dependencies.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.
        group (str): Name of poetry group. Defaults to None.

    Example:
        invoke install              # Installs dependencies for default group.
        invoke install --group dev  # Installs dependencies for dev group.

    """
    command = "poetry install"

    if group is not None:
        command += f" --with {group}"

    ctx.run(command)


@task(default=True)
def run(ctx: Context) -> None:
    """Runs a FastAPI application.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke run  # Runs the application.

    """

    ctx.run("poetry run python -m app.app")


@task
def test(ctx: Context) -> None:
    """Runs unit tests.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke test  # Runs unit tests.

    """
    ctx.run("poetry run pytest")


@task
def lint(ctx: Context, fix: bool = False) -> None:
    """Runs Ruff linter.

    Args:
        fix (bool): If True, enables autofix behaviour.
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke lint        # Runs linter.
        invoke lint --fix  # Runs linter with automatically error fix.

    """
    command = "poetry run ruff check ."
    if fix:
        command += " --fix"
    ctx.run(command)


@task
def format(ctx: Context, check_only: bool = False) -> None:
    """Runs formatter.

    Args:
        check_only (bool): If True, only prints out diffs.
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke format               # Runs formatter and automatically fixes errors.
        invoke format --check_only  # Runs formatter and only shows the list of errors.

    """
    command = "poetry run ruff format ."
    if check_only:
        command += " --diff --check"

    ctx.run(command)


@task
def mypy(ctx: Context) -> None:
    """Runs mypy checker.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke mypy  # Runs static type checker.

    """

    ctx.run("poetry run mypy .")


@task
def check(ctx: Context) -> None:
    """Runs unittests, linter, mypy and formatter together.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke check  # Runs linter, formatter, static type checker and unit tests.

    """
    lint(ctx)
    format(ctx, check_only=True)
    mypy(ctx)
    test(ctx)
