# cli.py
from datetime import UTC, datetime

import click
from colorama import Fore, init
from matter_persistence.sql.exceptions import DatabaseIntegrityError
from matter_task_queue import async_to_sync

from app.components.organizations.models.organization import OrganizationModel
from app.dependencies import Dependencies

init(autoreset=True)


@click.group()
def cli():
    Dependencies.start()


@cli.command()
@click.option("--parameter", prompt="Additional optional parameter", required=False)
def my_command(parameter):
    """Your custom command."""
    click.echo("My command!")
    if parameter:
        click.echo(f"A parameter has been passed: {Fore.GREEN}{parameter}")


@cli.command()
@click.option("--deep", prompt="Additional optional parameter", required=False)
def check_health(deep):
    """Checks the system's health and returns an analysis."""
    health_service = Dependencies.health_service()
    health_status_model = async_to_sync(health_service.get_health_status)
    click.echo(f"{Fore.GREEN}Health status retrieved.")
    click.echo(health_status_model.dict())


@cli.command()
@click.option("--organization_name", prompt="The organization's name", required=True)
@click.option("--organization_email", prompt="The organization's email", required=True)
@click.option("--first_name", prompt="The point of contact's first name", required=True)
@click.option("--last_name", prompt="The point of contact's last name", required=True)
def create_organization(organization_name, organization_email, first_name, last_name):
    """Creates a new organization and adds it to the database"""
    organization_service = Dependencies.organization_service()

    click.echo("Creating organization...")
    organization = OrganizationModel(
        organization_name=organization_name,
        organization_email=organization_email,
        first_name=first_name,
        last_name=last_name,
        created=datetime.now(tz=UTC),
    )

    click.echo("Saving in database...")
    try:
        new_organization = async_to_sync(organization_service.create_organization, organization)
    except DatabaseIntegrityError as exc:
        click.echo(f"{Fore.RED}Unable to create organization: ({str(exc.description)})")
        click.echo(f"Details: ({str(exc.detail)})")
        return

    click.echo(f"{Fore.GREEN}Organization Created:")
    click.echo(new_organization.__dict__)
    click.echo(f"{Fore.GREEN}Done!")


if __name__ == "__main__":
    cli()
