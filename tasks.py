"""
Module to manage shell-oriented subprocesses and organizing executable
Python code into CLI-invokable tasks.
"""

import asyncio

from invoke import Context, task
from mongodb_migrations.cli import MigrationManager
from mongodb_migrations.config import Configuration, Execution

from app.settings import SETTINGS
from app.tests.fixtures.manager import FileFixtureManager


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


@task
def create_migration(ctx: Context, description: str) -> None:
    """Creates a MongoDB migration script.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.
        description (str): Migration script description.

    Example:
        # Creates an empty migration script.
        invoke create-migration --description add_index

    """
    ctx.run(f"poetry run mongodb-migrate-create --description {description}")


@task
def upgrade_migrations(_: Context, to_datetime: str | None = None) -> None:
    """Upgrades MongoDB migrations.

    Args:
        _ (invoke.Context): The context object representing the current invocation.
        to_datetime (str): Defines a prefix of migration upgrade/downgrade
        operations will reach.

    Example:
        # Upgrades MongoDB migrations.
        invoke upgrade-migrations

        # Upgrades MongoDB migrations till '20231231132337'.
        invoke upgrade-migrations --to-datetime 20231231132337

    """

    config = Configuration(
        {
            "mongo_host": SETTINGS.MONGODB_HOST,
            "mongo_port": SETTINGS.MONGODB_PORT,
            "mongo_database": SETTINGS.MONGODB_NAME,
            "mongo_username": SETTINGS.MONGODB_USER,
            "mongo_password": SETTINGS.MONGODB_PASSWORD,
            "execution": Execution.MIGRATE,
            "to_datetime": to_datetime,
        }
    )

    manager = MigrationManager(config)

    manager.run()


@task
def downgrade_migrations(_: Context, to_datetime: str | None = None) -> None:
    """Downgrades MongoDB migration.

    Args:
        _ (invoke.Context): The context object representing the current invocation.
        to_datetime (str): Defines a prefix of migration upgrade/downgrade
        operations will reach.

    Example:
        # Downgrades MongoDB migrations.
        invoke downgrade_migrations

        # Downgrades MongoDB migrations till '20231231132337'.
        invoke downgrade-migrations --to-datetime 20231231132337


    """

    config = Configuration(
        {
            "mongo_host": SETTINGS.MONGODB_HOST,
            "mongo_port": SETTINGS.MONGODB_PORT,
            "mongo_database": SETTINGS.MONGODB_NAME,
            "mongo_username": SETTINGS.MONGODB_USER,
            "mongo_password": SETTINGS.MONGODB_PASSWORD,
            "execution": Execution.DOWNGRADE,
            "to_datetime": to_datetime,
        }
    )

    manager = MigrationManager(config)

    manager.run()


@task(default=True, pre=[upgrade_migrations])
def run(ctx: Context) -> None:
    """Runs a FastAPI application.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke run  # Runs the application.

    """

    ctx.run("poetry run python -m app.app")


@task(pre=[upgrade_migrations])
def test(ctx: Context) -> None:
    """Runs unit tests.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke test  # Runs unit tests.

    """
    ctx.run("poetry run pytest -v --cov=app app/")


@task
def coverage_report(ctx: Context) -> None:
    """Shows unit tests coverage report.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke coverage-report  # Shows coverage report.

    """
    ctx.run("poetry run coverage report -m")


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
    """Runs unit tests, linter, mypy and formatter together.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke check  # Runs linter, formatter, static type checker and unit tests.

    """
    lint(ctx)
    format(ctx, check_only=True)
    mypy(ctx)
    test(ctx)


@task
def load_fixtures(_: Context) -> None:
    """Loads test data from fixture files into MongoDB collections.

    Args:
        _ (invoke.Context): The context object representing the current invocation.

    Example:
        invoke load-fixtures  # Loads data from fixtures into Mongo collections.

    """

    file_fixture_manager = FileFixtureManager()

    asyncio.run(file_fixture_manager.load())
