"""
CLI Interface module for handling user interactions.
"""

import re
import asyncio
import logging
from typing import List, Dict, Any, Optional
import boto3

from .command import Command, CommandType
from ..config import DEFAULT_AWS_CONFIG

logger = logging.getLogger(__name__)

class CLIInterface:
    """Main class for CLI interaction."""
    
    def __init__(self):
        """Initialize the CLI interface."""
        self.command_history: List[Command] = []
        self.aws_config = DEFAULT_AWS_CONFIG
        self._command_patterns = self._compile_command_patterns()
    
    def _compile_command_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for command parsing."""
        return {
            "list_instances": re.compile(r"list\s+ec2\s+instances"),
            "terminate_instance": re.compile(r"terminate\s+ec2\s+instance\s+(i-[a-z0-9]+)"),
            "create_bucket": re.compile(r"create\s+s3\s+bucket\s+([a-z0-9-]+)"),
            "list_buckets": re.compile(r"list\s+s3\s+buckets"),
        }
    
    async def process_input(self, user_input: str) -> Command:
        """
        Process user input and convert it to a Command object.
        
        Args:
            user_input: Raw input string from user
            
        Returns:
            Command object representing the parsed command
        """
        user_input = user_input.strip().lower()
        
        # Check for built-in commands
        if user_input in ["help", "?"]:
            return Command(
                type=CommandType.HELP,
                service="cli",
                action="help",
                parameters={},
                requires_approval=False
            )
        elif user_input in ["exit", "quit"]:
            return Command(
                type=CommandType.EXIT,
                service="cli",
                action="exit",
                parameters={},
                requires_approval=False
            )
        
        # Try to match AWS commands
        for pattern_name, pattern in self._command_patterns.items():
            if match := pattern.match(user_input):
                command_config = self._get_command_config(pattern_name, match)
                return Command(
                    type=CommandType.AWS,
                    **command_config
                )
        
        raise ValueError(f"Unknown command: {user_input}")
    
    def _get_command_config(self, pattern_name: str, match: re.Match) -> Dict[str, Any]:
        """Get command configuration based on the matched pattern."""
        if pattern_name == "list_instances":
            return {
                "service": "ec2",
                "action": "list-instances",
                "parameters": {}
            }
        elif pattern_name == "terminate_instance":
            return {
                "service": "ec2",
                "action": "terminate-instances",
                "parameters": {"InstanceIds": [match.group(1)]}
            }
        elif pattern_name == "create_bucket":
            return {
                "service": "s3",
                "action": "create-bucket",
                "parameters": {"Bucket": match.group(1)}
            }
        elif pattern_name == "list_buckets":
            return {
                "service": "s3",
                "action": "list-buckets",
                "parameters": {}
            }
        else:
            raise ValueError(f"Unknown pattern: {pattern_name}")
    
    async def approve_command(self, command: Command) -> None:
        """
        Approve a command for execution.
        
        Args:
            command: Command to approve
        """
        if not command.requires_approval:
            return
            
        command.approve("cli-user")  # TODO: Get actual user ID
        self.command_history.append(command)
    
    async def execute_command(self, command: Command) -> Optional[Dict[str, Any]]:
        """
        Execute an approved command.
        
        Args:
            command: Command to execute
            
        Returns:
            Optional dict containing command results
        """
        if command.requires_approval and not command.is_approved:
            raise ValueError("Command must be approved before execution")
        
        if command.type == CommandType.AWS:
            return await self._execute_aws_command(command)
        elif command.type == CommandType.HELP:
            return self._show_help()
        elif command.type == CommandType.EXIT:
            return None
            
        raise ValueError(f"Unknown command type: {command.type}")
    
    async def _execute_aws_command(self, command: Command) -> Dict[str, Any]:
        """Execute an AWS command using boto3."""
        aws_command = command.to_aws_command()
        client = boto3.client(aws_command["service"])
        
        # Convert action from kebab-case to snake_case for boto3
        action = aws_command["action"].replace("-", "_")
        
        try:
            method = getattr(client, action)
            return method(**aws_command["parameters"])
        except Exception as e:
            logger.error(f"Error executing AWS command: {e}")
            raise
    
    def _show_help(self) -> Dict[str, Any]:
        """Show help information."""
        return {
            "available_commands": [
                "list ec2 instances",
                "terminate ec2 instance <instance-id>",
                "create s3 bucket <bucket-name>",
                "list s3 buckets",
                "help",
                "exit"
            ]
        } 