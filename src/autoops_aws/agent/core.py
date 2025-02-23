"""
Core AI Agent module.

This module implements the main AI agent that combines DevOps and Cloud Engineering
capabilities to provide an intelligent assistant for AWS operations.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from ..roles.devops import DevOpsCapabilities
from ..roles.cloud_engineer import CloudEngineerCapabilities

logger = logging.getLogger(__name__)

@dataclass
class Conversation:
    """Represents a conversation with the AI agent."""
    id: str
    start_time: datetime
    context: Dict[str, Any]
    history: List[Dict[str, Any]]

class AWSOperationsAgent:
    """Main AI agent class combining DevOps and Cloud Engineering capabilities."""
    
    def __init__(self):
        """Initialize the AI agent with all capabilities."""
        self.devops = DevOpsCapabilities()
        self.cloud = CloudEngineerCapabilities()
        self.conversations: Dict[str, Conversation] = {}
        
        # Define common tasks and their handlers
        self.task_handlers = {
            # Infrastructure tasks
            "create_infrastructure": self._handle_infrastructure_creation,
            "update_infrastructure": self._handle_infrastructure_update,
            "destroy_infrastructure": self._handle_infrastructure_destruction,
            
            # Application deployment tasks
            "deploy_application": self._handle_application_deployment,
            "rollback_deployment": self._handle_deployment_rollback,
            "scale_application": self._handle_application_scaling,
            
            # Monitoring and maintenance tasks
            "setup_monitoring": self._handle_monitoring_setup,
            "investigate_issue": self._handle_issue_investigation,
            "optimize_resources": self._handle_resource_optimization,
            
            # Security tasks
            "security_audit": self._handle_security_audit,
            "update_security": self._handle_security_update,
            
            # Cost management tasks
            "analyze_costs": self._handle_cost_analysis,
            "optimize_costs": self._handle_cost_optimization
        }
    
    async def start_conversation(self, user_id: str) -> str:
        """
        Start a new conversation with the user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Conversation ID
        """
        conversation = Conversation(
            id=f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}",
            start_time=datetime.now(),
            context={},
            history=[]
        )
        self.conversations[conversation.id] = conversation
        return conversation.id
    
    async def process_message(
        self,
        conversation_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return appropriate response.
        
        Args:
            conversation_id: ID of the conversation
            message: User's message
            context: Optional additional context
            
        Returns:
            Dict containing the agent's response and any actions
        """
        # Update conversation context
        conversation = self.conversations[conversation_id]
        if context:
            conversation.context.update(context)
        
        # Add message to history
        conversation.history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now()
        })
        
        try:
            # Analyze the message and determine required actions
            task_type, parameters = await self._analyze_message(message, conversation.context)
            
            # Execute the appropriate task handler
            if task_type in self.task_handlers:
                response = await self.task_handlers[task_type](parameters, conversation.context)
            else:
                response = {
                    "message": "I'm not sure how to help with that specific task. Could you please rephrase or provide more details?",
                    "error": "Unknown task type"
                }
            
            # Add response to history
            conversation.history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now()
            })
            
            return response
            
        except Exception as e:
            logger.exception("Error processing message")
            return {
                "message": f"An error occurred while processing your request: {str(e)}",
                "error": str(e)
            }
    
    async def _analyze_message(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """
        Analyze user message to determine required actions.
        
        Args:
            message: User's message
            context: Current conversation context
            
        Returns:
            Tuple of (task_type, parameters)
        """
        # TODO: Implement message analysis using NLP
        raise NotImplementedError()
    
    async def _handle_infrastructure_creation(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle infrastructure creation requests."""
        # Generate Terraform code
        terraform_code = await self.devops.generate_terraform_code(parameters)
        
        # Design architecture
        architecture = await self.cloud.design_architecture(parameters)
        
        # Combine results
        return {
            "terraform_code": terraform_code,
            "architecture": architecture,
            "next_steps": [
                "Review the generated Terraform code",
                "Verify the architecture design",
                "Apply the infrastructure changes"
            ]
        }
    
    async def _handle_application_deployment(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle application deployment requests."""
        # Create CI/CD pipeline
        pipeline = await self.devops.create_cicd_pipeline(
            parameters.get("project_type"),
            parameters.get("pipeline_requirements")
        )
        
        # Set up monitoring
        monitoring = await self.devops.setup_monitoring(
            parameters.get("resources", []),
            parameters.get("metrics", [])
        )
        
        return {
            "pipeline_config": pipeline,
            "monitoring_config": monitoring,
            "next_steps": [
                "Review the CI/CD pipeline configuration",
                "Verify monitoring setup",
                "Trigger initial deployment"
            ]
        }
    
    async def _handle_issue_investigation(
        self,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle issue investigation requests."""
        # Get troubleshooting steps
        troubleshooting = await self.devops.troubleshoot_issue(
            parameters.get("description"),
            parameters.get("logs", {}),
            parameters.get("metrics", {})
        )
        
        # Audit security if needed
        if parameters.get("security_concern"):
            security_audit = await self.cloud.audit_security(
                parameters.get("resources", [])
            )
            troubleshooting["security_findings"] = security_audit
        
        return troubleshooting
    
    # Implement other task handlers similarly
    
    def _format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format the response for user consumption."""
        return {
            "message": response.get("message", "Task completed successfully."),
            "details": response,
            "timestamp": datetime.now().isoformat()
        } 