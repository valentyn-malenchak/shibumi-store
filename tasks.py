"""
Module to manage shell-oriented subprocesses and organizing executable
Python code into CLI-invokable tasks.
"""

from invoke import Context, task


@task(default=True)
def run(ctx: Context, debug: bool = False) -> None:
    """Runs a FastAPI application.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.
        debug (bool): If True, run the application in debug mode with auto-reloading.

    Example:
        invoke run          # Run the application.
        invoke run --debug  # Run the application in debug mode with auto-reloading.

    """
    command = "poetry run python -m app.app"
    if debug:
        command += " --reload"

    ctx.run(command)


@task
def test(ctx: Context) -> None:
    """Runs unittests.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    """
    ctx.run("poetry run pytest")


@task
def lint(ctx: Context, fix: bool = False) -> None:
    """Runs Ruff linter.

    Args:
        fix (bool): If True, enables autofix behaviour.
        ctx (invoke.Context): The context object representing the current invocation.

    """
    command = "poetry run ruff check ."
    if fix:
        command += " --fix"
    ctx.run(command)


@task
def format(ctx: Context, check_only: bool = False) -> None:
    """Runs Black formatter.

    Args:
        check_only (bool): If True, only prints out diffs.
        ctx (invoke.Context): The context object representing the current invocation.

    """
    command = "poetry run black ."
    if check_only:
        command += " --diff"

    ctx.run(command)


@task
def mypy(ctx: Context) -> None:
    """Runs mypy checker.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    """

    ctx.run("poetry run mypy .")


@task
def check(ctx: Context) -> None:
    """Runs unittests, linter, mypy and formatter together.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    """
    lint(ctx)
    format(ctx, check_only=True)
    mypy(ctx)
    test(ctx)
