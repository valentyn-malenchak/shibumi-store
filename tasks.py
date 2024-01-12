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
def outdated_packages(ctx: Context) -> None:
    """Shows a list of outdated packages.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke outdated-packages   # Shows outdated packages.

    """
    ctx.run("poetry show --outdated")


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
    ctx.run(f"mongodb-migrate-create --description {description}")


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
            "mongo_url": (
                f"mongodb://{SETTINGS.MONGODB_HOST}:{SETTINGS.MONGODB_PORT}/"
                f"{SETTINGS.MONGODB_NAME}?authSource={SETTINGS.MONGO_AUTH_SOURCE}",
            ),
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
            "mongo_url": (
                f"mongodb://{SETTINGS.MONGODB_HOST}:{SETTINGS.MONGODB_PORT}/"
                f"{SETTINGS.MONGODB_NAME}?authSource={SETTINGS.MONGO_AUTH_SOURCE}",
            ),
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

    ctx.run("python -m app.app")


@task(pre=[upgrade_migrations])
def test(ctx: Context) -> None:
    """Runs unit tests.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke test  # Runs unit tests.

    """
    ctx.run(
        "pytest -v --cov-report term-missing --cov-report xml "
        "--cov-report html --cov-branch --cov=app app/"
    )


@task
def lint(ctx: Context, fix: bool = False) -> None:
    """Runs Ruff linter.

    Args:
        fix (bool): If True, enables automatically fix behaviour.
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke lint        # Runs linter.
        invoke lint --fix  # Runs linter with automatically error fix.

    """
    command = "ruff check ."
    if fix:
        command += " --fix"
    ctx.run(command)


@task
def format(ctx: Context, fix: bool = False) -> None:
    """Runs formatter.

    Args:
        fix (bool): If True, enables automatically fix behaviour.
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke format        # Runs formatter and only shows the list of errors.
        invoke format --fix  # Runs formatter and automatically fixes errors.

    """
    command = "ruff format ."
    if fix is False:
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

    ctx.run("mypy .")


@task
def check(ctx: Context) -> None:
    """Runs unit tests, linter, mypy and formatter together.

    Args:
        ctx (invoke.Context): The context object representing the current invocation.

    Example:
        invoke check  # Runs linter, formatter, static type checker and unit tests.

    """
    lint(ctx)
    format(ctx)
    mypy(ctx)
    test(ctx)


@task
def fixture(_: Context) -> None:
    """Loads test data from fixture files into MongoDB collections.

    Args:
        _ (invoke.Context): The context object representing the current invocation.

    Example:
        invoke fixture  # Loads data from fixtures into Mongo collections.

    """

    file_fixture_manager = FileFixtureManager()

    asyncio.run(file_fixture_manager.load())


@task
def build(ctx: Context) -> None:
    """Builds a new docker image for application.

    Args:
        ctx: The context object representing the current invocation.

    Example:
        invoke build  # Builds new application image

    """
    ctx.run("docker build -t fastapi-shop:latest .")


@task
def compose(ctx: Context) -> None:
    """Runs a docker-compose.

    Args:
        ctx: The context object representing the current invocation.

    Example:
        invoke compose  # Runs a docker-compose

    """
    ctx.run("docker-compose up -d")
