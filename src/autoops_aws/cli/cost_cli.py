"""
Cost Optimization CLI.

A simple command-line interface for AWS cost optimization.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

from ..agent.cost_optimizer import CostOptimizer

console = Console()

class CostOptimizationCLI:
    """CLI for AWS cost optimization."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.optimizer = CostOptimizer()
    
    def _display_welcome(self):
        """Display welcome message."""
        console.print("\n[bold blue]AWS Cost Optimization Assistant[/bold blue]")
        console.print("""
This tool helps you analyze and optimize your AWS costs. Available commands:
- [green]analyze[/green]: Show current cost analysis
- [green]optimize[/green]: Get cost optimization recommendations
- [green]help[/green]: Show this help message
- [green]exit[/green]: Exit the application
""")
    
    def _display_costs(self, cost_data: Dict[str, Any]):
        """Display cost analysis in a table."""
        table = Table(title="AWS Costs by Service")
        table.add_column("Service", style="cyan")
        table.add_column("Usage Type", style="magenta")
        table.add_column("Cost (USD)", style="green", justify="right")
        
        for time_period in cost_data['costs']:
            for group in time_period['Groups']:
                service, usage_type = group['Keys']
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                table.add_row(service, usage_type, f"${cost:,.2f}")
        
        console.print(table)
        console.print(f"\n[bold green]Total Cost: ${cost_data['total']:,.2f}[/bold green]")
    
    async def analyze_costs(self):
        """Analyze current AWS costs."""
        try:
            # Get costs for the last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            time_period = {
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            }
            
            console.print("\n[yellow]Analyzing costs for the last 30 days...[/yellow]")
            cost_data = await self.optimizer.analyze_current_costs(time_period)
            self._display_costs(cost_data)
            
        except Exception as e:
            console.print(f"\n[red]Error analyzing costs:[/red] {str(e)}")
    
    async def get_recommendations(self):
        """Get and display optimization recommendations."""
        try:
            console.print("\n[yellow]Analyzing your AWS resources for optimization opportunities...[/yellow]")
            recommendations = await self.optimizer.get_optimization_recommendations()
            
            console.print("\n" + self.optimizer.format_recommendations(recommendations))
            
            if recommendations and Confirm.ask("\nWould you like detailed information about any of these recommendations?"):
                # TODO: Implement detailed recommendation viewing
                console.print("[yellow]Detailed viewing coming soon![/yellow]")
            
        except Exception as e:
            console.print(f"\n[red]Error getting recommendations:[/red] {str(e)}")
    
    async def run(self):
        """Run the CLI interface."""
        self._display_welcome()
        
        while True:
            try:
                command = console.input("\n[bold green]>>> [/bold green]").lower().strip()
                
                if command == "exit":
                    break
                elif command == "help":
                    self._display_welcome()
                elif command == "analyze":
                    await self.analyze_costs()
                elif command == "optimize":
                    await self.get_recommendations()
                else:
                    console.print("[yellow]Unknown command. Type 'help' for available commands.[/yellow]")
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except Exception as e:
                console.print(f"[red]An error occurred:[/red] {str(e)}")
        
        console.print("\n[blue]Goodbye![/blue]")

@click.command()
def main():
    """Main entry point for the CLI."""
    try:
        cli = CostOptimizationCLI()
        asyncio.run(cli.run())
    except Exception as e:
        console.print(f"[red]Fatal error:[/red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 