"""
Tests for the CLI interface module.
"""

import pytest
from unittest.mock import Mock, patch
from autoops_aws.cli.interface import CLIInterface
from autoops_aws.cli.command import Command, CommandType

@pytest.fixture
def cli_interface():
    """Create a CLIInterface instance for testing."""
    return CLIInterface()

def test_cli_interface_initialization(cli_interface):
    """Test that CLIInterface initializes correctly."""
    assert isinstance(cli_interface, CLIInterface)
    assert hasattr(cli_interface, "command_history")
    assert isinstance(cli_interface.command_history, list)

@pytest.mark.asyncio
async def test_process_user_input():
    """Test processing of user input into a command."""
    cli = CLIInterface()
    command = await cli.process_input("list ec2 instances")
    
    assert isinstance(command, Command)
    assert command.type == CommandType.AWS
    assert command.service == "ec2"
    assert command.action == "list-instances"
    assert not command.is_approved

@pytest.mark.asyncio
async def test_command_requires_approval():
    """Test that AWS commands require approval before execution."""
    cli = CLIInterface()
    command = await cli.process_input("terminate ec2 instance i-1234567890abcdef0")
    
    assert not command.is_approved
    assert command.requires_approval
    assert command.type == CommandType.AWS
    assert command.service == "ec2"
    assert command.action == "terminate-instances"

@pytest.mark.asyncio
async def test_command_approval_flow():
    """Test the command approval flow."""
    cli = CLIInterface()
    command = await cli.process_input("create s3 bucket my-test-bucket")
    
    # Command should start unapproved
    assert not command.is_approved
    
    # Approve the command
    await cli.approve_command(command)
    assert command.is_approved
    
    # Should be in command history
    assert command in cli.command_history

@pytest.mark.asyncio
async def test_safe_command_execution():
    """Test that only approved commands can be executed."""
    cli = CLIInterface()
    command = await cli.process_input("list s3 buckets")
    
    # Try to execute without approval
    with pytest.raises(ValueError, match="Command must be approved before execution"):
        await cli.execute_command(command)
    
    # Approve and execute
    await cli.approve_command(command)
    with patch("autoops_aws.cli.interface.boto3") as mock_boto3:
        mock_s3 = Mock()
        mock_boto3.client.return_value = mock_s3
        mock_s3.list_buckets.return_value = {"Buckets": []}
        
        result = await cli.execute_command(command)
        assert result is not None
        mock_s3.list_buckets.assert_called_once() 