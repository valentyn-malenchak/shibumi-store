"""
Module to manage shell-oriented subprocesses and organizing executable
Python code into CLI-invokable tasks.
"""

from invoke import task


@task(default=True)
def run(ctx, debug=False):
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
def test(ctx):
    """Runs unittests.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    """
    ctx.run("poetry run pytest")


@task
def lint(ctx, fix=False):
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
def format(ctx, check_only=False):
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
def check(ctx):
    """Runs unittests and linter together.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    """
    lint(ctx)
    format(ctx, check_only=True)
    test(ctx)
