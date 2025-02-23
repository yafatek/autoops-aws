"""
Main CLI application module.
"""

import asyncio
import sys
import logging
from typing import Optional
import click
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from .interface import CLIInterface
from .command import CommandType

console = Console()
logger = logging.getLogger(__name__)

class CLIApp:
    """Main CLI application class."""
    
    def __init__(self):
        """Initialize the CLI application."""
        self.interface = CLIInterface()
        self.running = False
    
    def _display_welcome(self):
        """Display welcome message and instructions."""
        console.print("\n[bold blue]Welcome to AutoOps AWS CLI![/bold blue]")
        console.print("Type [green]help[/green] for available commands or [red]exit[/red] to quit.\n")
    
    def _display_help(self, help_info):
        """Display help information in a formatted table."""
        table = Table(title="Available Commands")
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="green")
        
        commands = {
            "list ec2 instances": "List all EC2 instances in the current region",
            "terminate ec2 instance <id>": "Terminate a specific EC2 instance",
            "create s3 bucket <name>": "Create a new S3 bucket",
            "list s3 buckets": "List all S3 buckets",
            "help": "Show this help message",
            "exit": "Exit the application"
        }
        
        for command in help_info["available_commands"]:
            table.add_row(command, commands.get(command, ""))
        
        console.print(table)
    
    def _display_aws_result(self, result):
        """Display AWS command results in a formatted way."""
        if not result:
            return
            
        if "Buckets" in result:
            table = Table(title="S3 Buckets")
            table.add_column("Bucket Name", style="cyan")
            table.add_column("Creation Date", style="green")
            
            for bucket in result["Buckets"]:
                table.add_row(
                    bucket["Name"],
                    str(bucket["CreationDate"])
                )
            console.print(table)
        elif "Instances" in result:
            table = Table(title="EC2 Instances")
            table.add_column("Instance ID", style="cyan")
            table.add_column("State", style="green")
            table.add_column("Type", style="blue")
            
            for instance in result["Instances"]:
                table.add_row(
                    instance["InstanceId"],
                    instance["State"]["Name"],
                    instance["InstanceType"]
                )
            console.print(table)
        else:
            console.print(result)
    
    async def _get_user_approval(self, command) -> bool:
        """Get user approval for a command."""
        console.print("\n[yellow]Command requires approval:[/yellow]")
        console.print(f"[bold]{str(command)}[/bold]")
        
        return Confirm.ask("Do you want to approve this command?")
    
    async def _process_command(self, user_input: str) -> bool:
        """
        Process a single command.
        
        Returns:
            Boolean indicating whether to continue running
        """
        try:
            # Parse the command
            command = await self.interface.process_input(user_input)
            
            # Handle exit command
            if command.type == CommandType.EXIT:
                return False
            
            # Handle help command
            if command.type == CommandType.HELP:
                result = await self.interface.execute_command(command)
                self._display_help(result)
                return True
            
            # Get approval if needed
            if command.requires_approval:
                if not await self._get_user_approval(command):
                    console.print("[yellow]Command cancelled by user[/yellow]")
                    return True
                await self.interface.approve_command(command)
            
            # Execute the command
            result = await self.interface.execute_command(command)
            self._display_aws_result(result)
            
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            logger.exception("Error processing command")
        
        return True
    
    async def run(self):
        """Run the main application loop."""
        self.running = True
        self._display_welcome()
        
        while self.running:
            try:
                user_input = console.input("[bold green]>>> [/bold green]")
                self.running = await self._process_command(user_input)
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except Exception as e:
                console.print(f"[red]Unexpected error:[/red] {str(e)}")
                logger.exception("Unexpected error in main loop")
        
        console.print("\n[blue]Goodbye![/blue]")

@click.command()
def main():
    """Main entry point for the CLI application."""
    try:
        app = CLIApp()
        asyncio.run(app.run())
    except Exception as e:
        console.print(f"[red]Fatal error:[/red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 