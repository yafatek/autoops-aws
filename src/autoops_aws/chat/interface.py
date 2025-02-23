"""
Chat interface module for interacting with the AWS Operations Agent.
"""

import asyncio
import uuid
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.panel import Panel

from ..agent.core import AWSOperationsAgent

console = Console()

class ChatInterface:
    """Interactive chat interface for the AWS Operations Agent."""
    
    def __init__(self):
        """Initialize the chat interface."""
        self.agent = AWSOperationsAgent()
        self.user_id = str(uuid.uuid4())
        self.conversation_id: Optional[str] = None
        
    def _display_welcome(self):
        """Display welcome message and instructions."""
        welcome_text = """
# AWS Operations Assistant

I'm your AI-powered DevOps and Cloud Engineering assistant. I can help you with:

## Infrastructure Management
- Creating and managing AWS infrastructure using Terraform
- Designing scalable and secure architectures
- Implementing best practices and patterns

## DevOps Operations
- Setting up CI/CD pipelines
- Implementing monitoring and logging
- Troubleshooting issues
- Managing deployments

## Cloud Engineering
- AWS service integration
- Security and compliance
- Cost optimization
- High availability setup

## How to interact
- Describe what you want to achieve in natural language
- I'll analyze your request and suggest appropriate actions
- You'll have the chance to review and approve any changes
- Ask for help or clarification at any time

Type 'help' for available commands or 'exit' to quit.
"""
        console.print(Markdown(welcome_text))
    
    def _display_code(self, code: str, language: str = "terraform"):
        """Display code with syntax highlighting."""
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=f"{language.capitalize()} Code"))
    
    def _display_architecture(self, architecture: Dict[str, Any]):
        """Display architecture diagram and details."""
        # TODO: Implement architecture visualization
        console.print(Panel(str(architecture), title="Architecture Design"))
    
    async def _get_user_approval(self, action: str, details: Dict[str, Any]) -> bool:
        """
        Get user approval for an action.
        
        Args:
            action: Description of the action
            details: Action details
            
        Returns:
            Boolean indicating approval
        """
        console.print(f"\n[yellow]Action requires approval:[/yellow] {action}")
        
        if "code" in details:
            self._display_code(details["code"])
        if "architecture" in details:
            self._display_architecture(details["architecture"])
        
        return Confirm.ask("Do you want to proceed with this action?")
    
    async def _process_help(self):
        """Display help information."""
        help_text = """
## Available Commands

### Infrastructure
- create infrastructure <description>
- update infrastructure <description>
- destroy infrastructure <name>

### Applications
- deploy application <details>
- rollback deployment <service>
- scale application <service>

### Monitoring
- setup monitoring <resources>
- investigate issue <description>
- optimize resources <targets>

### Security
- audit security <scope>
- update security <requirements>

### Cost Management
- analyze costs
- optimize costs <target>

### General
- help - Show this help message
- exit - Exit the application
"""
        console.print(Markdown(help_text))
    
    async def run(self):
        """Run the chat interface."""
        self._display_welcome()
        
        # Start conversation
        self.conversation_id = await self.agent.start_conversation(self.user_id)
        
        while True:
            try:
                # Get user input
                user_input = console.input("[bold green]>>> [/bold green]")
                
                # Handle built-in commands
                if user_input.lower() == "exit":
                    break
                elif user_input.lower() == "help":
                    await self._process_help()
                    continue
                
                # Process user input
                response = await self.agent.process_message(
                    self.conversation_id,
                    user_input
                )
                
                # Handle response
                if "error" in response:
                    console.print(f"[red]Error:[/red] {response['error']}")
                    continue
                
                # Display response
                if "message" in response:
                    console.print(response["message"])
                
                # Handle actions that need approval
                if "actions" in response:
                    for action in response["actions"]:
                        if await self._get_user_approval(action["description"], action["details"]):
                            # Execute approved action
                            result = await self.agent.execute_action(
                                self.conversation_id,
                                action["id"]
                            )
                            console.print(f"[green]Action completed:[/green] {result['message']}")
                        else:
                            console.print("[yellow]Action cancelled[/yellow]")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except Exception as e:
                console.print(f"[red]An error occurred:[/red] {str(e)}")
        
        console.print("\n[blue]Goodbye![/blue]")

def main():
    """Main entry point for the chat interface."""
    interface = ChatInterface()
    asyncio.run(interface.run()) 