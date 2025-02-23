"""
AI-powered CLI for AWS operations.
"""

import asyncio
import sys
import os
from typing import Optional
import click
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel
from dotenv import load_dotenv

from ..agent.ai_agent import AWSAIAgent

console = Console()

class AICLI:
    """AI-powered CLI for AWS operations."""
    
    def __init__(self):
        """Initialize the CLI."""
        # Load environment variables
        load_dotenv()
        
        # Get Google API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Initialize AI agent
        self.agent = AWSAIAgent(api_key)
    
    def _display_welcome(self):
        """Display welcome message."""
        welcome_text = """
# AWS Operations AI Assistant

I'm your AI-powered AWS operations assistant. I can help you with:

## Available Capabilities
- Audit AWS resources for security and compliance
- Analyze and optimize costs
- Generate Terraform infrastructure code
- Provide best practices and recommendations

## How to interact
- Simply describe what you want to do in natural language
- I'll understand your request and suggest appropriate actions
- You'll have the chance to review and approve any changes

Type 'help' to see example commands or 'exit' to quit.
"""
        console.print(Markdown(welcome_text))
    
    def _display_code(self, code: str, language: str = "terraform"):
        """Display code with syntax highlighting."""
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"{language.capitalize()} Code"))
    
    def _display_audit_results(self, results: dict):
        """Display audit results in a formatted way."""
        # Display IAM findings
        if results.get("iam", {}).get("users"):
            console.print("\n[bold red]IAM Issues Found:[/bold red]")
            for user in results["iam"]["users"]:
                console.print(f"User: {user['username']}")
                for issue in user["issues"]:
                    console.print(f"  - {issue}")
        
        # Display security group findings
        if results.get("security_groups"):
            console.print("\n[bold red]Security Group Issues Found:[/bold red]")
            for sg in results["security_groups"]:
                console.print(f"Group: {sg['group_name']} ({sg['group_id']})")
                for issue in sg["issues"]:
                    console.print(f"  - {issue}")
        
        # Display S3 findings
        if results.get("s3"):
            console.print("\n[bold red]S3 Issues Found:[/bold red]")
            for bucket in results["s3"]:
                console.print(f"Bucket: {bucket['bucket_name']}")
                for issue in bucket["issues"]:
                    console.print(f"  - {issue}")
        
        # Display recommendations
        if results.get("recommendations"):
            console.print("\n[bold yellow]Recommendations:[/bold yellow]")
            for rec in results["recommendations"]:
                console.print(f"\n[bold]{rec['category']} - {rec['service']} (Priority: {rec['priority']})[/bold]")
                console.print(f"Description: {rec['description']}")
                console.print(f"Details: {rec['details']}")
    
    async def run(self):
        """Run the CLI interface."""
        self._display_welcome()
        
        while True:
            try:
                # Get user input
                user_input = console.input("\n[bold green]>>> [/bold green]")
                
                # Handle built-in commands
                if user_input.lower() == "exit":
                    break
                elif user_input.lower() == "help":
                    console.print(self.agent.get_available_commands())
                    continue
                
                # Process user input through AI agent
                console.print("\n[yellow]Thinking...[/yellow]")
                response = await self.agent.process_message(user_input)
                
                # Handle errors
                if "error" in response:
                    console.print(f"\n[red]Error:[/red] {response['error']}")
                    continue
                
                # Display AI's understanding
                console.print("\n[bold]I understand you want to:[/bold]")
                console.print(response["understanding"])
                
                # Display results based on action type
                if response["action"] == "audit":
                    self._display_audit_results(response["result"])
                elif response["action"] == "generate_terraform":
                    self._display_code(response["result"]["code"])
                else:
                    console.print("\n[bold]Results:[/bold]")
                    console.print(response["result"])
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except Exception as e:
                console.print(f"[red]An error occurred:[/red] {str(e)}")
        
        console.print("\n[blue]Goodbye![/blue]")

@click.command()
def main():
    """Main entry point for the CLI."""
    try:
        cli = AICLI()
        asyncio.run(cli.run())
    except Exception as e:
        console.print(f"[red]Fatal error:[/red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 