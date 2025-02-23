"""
Command module for representing CLI commands.
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

class CommandType(Enum):
    """Types of commands that can be executed."""
    AWS = "aws"
    SYSTEM = "system"
    HELP = "help"
    EXIT = "exit"

@dataclass
class Command:
    """Represents a command to be executed."""
    
    type: CommandType
    service: str
    action: str
    parameters: Dict[str, Any]
    requires_approval: bool = True
    is_approved: bool = False
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    
    def __post_init__(self):
        """Validate command after initialization."""
        if self.type == CommandType.AWS:
            self.requires_approval = True
        elif self.type == CommandType.HELP:
            self.requires_approval = False
    
    def approve(self, approver: str):
        """
        Approve the command for execution.
        
        Args:
            approver: Name/ID of the person approving the command
        """
        self.is_approved = True
        self.approved_at = datetime.now()
        self.approved_by = approver
    
    def to_aws_command(self) -> Dict[str, Any]:
        """
        Convert the command to AWS SDK format.
        
        Returns:
            Dict containing the AWS SDK command parameters
        """
        if self.type != CommandType.AWS:
            raise ValueError("Can only convert AWS commands")
            
        return {
            "service": self.service,
            "action": self.action,
            "parameters": self.parameters
        }
    
    def __str__(self) -> str:
        """Return string representation of the command."""
        base = f"{self.type.value} command: {self.service} {self.action}"
        if self.parameters:
            params = " ".join(f"{k}={v}" for k, v in self.parameters.items())
            base += f" with parameters: {params}"
        return base 