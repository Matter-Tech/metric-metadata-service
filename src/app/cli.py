# cli.py
import click
from colorama import Fore, init
from matter_task_queue import async_to_sync

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


if __name__ == "__main__":
    cli()
