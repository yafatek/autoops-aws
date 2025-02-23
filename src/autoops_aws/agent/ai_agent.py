"""
Core AI Agent using Google's Gemini model.
"""

import logging
from typing import Dict, Any, List, Optional
from google import genai
from ..tools.cost_analyzer import CostAnalyzer
from ..tools.terraform_generator import TerraformGenerator
from ..tools.aws_auditor import AWSAuditor

logger = logging.getLogger(__name__)

class AWSAIAgent:
    """Main AI agent class that coordinates all AWS operations."""
    
    def __init__(self, api_key: str):
        """
        Initialize the AI agent.
        
        Args:
            api_key: Google API key for Gemini
        """
        # Initialize Gemini
        genai.configure(api_key=api_key)
        self.client = genai.Client()
        self.model = 'gemini-pro'
        
        # Initialize tools
        self.cost_analyzer = CostAnalyzer()
        self.terraform_generator = TerraformGenerator()
        self.aws_auditor = AWSAuditor()
        
        # Create chat session
        self.chat = self.client.chats.create(model=self.model)
        
        # Define available commands and their descriptions
        self.commands = {
            "audit": "Audit AWS resources for security and cost optimization",
            "analyze_costs": "Analyze current AWS costs and usage",
            "generate_terraform": "Generate Terraform code for AWS infrastructure",
            "optimize": "Get cost optimization recommendations",
            "help": "Show available commands"
        }
    
    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and determine the appropriate action.
        
        Args:
            message: User's input message
            
        Returns:
            Dict containing the response and any actions to take
        """
        try:
            # Add system context for better understanding
            system_prompt = """
            You are an AWS DevOps AI assistant. Your role is to:
            1. Understand user requests about AWS infrastructure
            2. Determine which tools to use (audit, cost analysis, Terraform generation)
            3. Provide clear, actionable responses
            4. Always ask for confirmation before making changes
            
            Available tools:
            - AWS Auditor: Security and compliance checks
            - Cost Analyzer: Usage and cost optimization
            - Terraform Generator: Infrastructure as Code
            
            Respond with:
            1. Your understanding of the request
            2. The tool(s) you'll use
            3. Any additional information needed
            """
            
            # Send message to Gemini
            response = self.chat.send_message(
                f"{system_prompt}\n\nUser request: {message}"
            )
            
            # Parse the response to determine the action
            action_type, parameters = self._parse_ai_response(response.text)
            
            # Execute the appropriate action
            result = await self._execute_action(action_type, parameters)
            
            return {
                "understanding": response.text,
                "action": action_type,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "error": str(e),
                "message": "Failed to process your request"
            }
    
    def _parse_ai_response(self, response: str) -> tuple[str, Dict[str, Any]]:
        """
        Parse the AI's response to determine the action to take.
        
        Args:
            response: AI's response text
            
        Returns:
            Tuple of (action_type, parameters)
        """
        # TODO: Implement more sophisticated parsing
        # For now, use simple keyword matching
        response_lower = response.lower()
        
        if "audit" in response_lower:
            return "audit", {}
        elif "cost" in response_lower or "analyze" in response_lower:
            return "analyze_costs", {}
        elif "terraform" in response_lower or "infrastructure" in response_lower:
            return "generate_terraform", {"description": response}
        elif "optimize" in response_lower:
            return "optimize", {}
        else:
            return "unknown", {"response": response}
    
    async def _execute_action(
        self,
        action_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the determined action using the appropriate tool.
        
        Args:
            action_type: Type of action to perform
            parameters: Parameters for the action
            
        Returns:
            Dict containing the results
        """
        try:
            if action_type == "audit":
                return await self.aws_auditor.run_audit()
            elif action_type == "analyze_costs":
                return await self.cost_analyzer.analyze_costs()
            elif action_type == "generate_terraform":
                return await self.terraform_generator.generate(parameters.get("description", ""))
            elif action_type == "optimize":
                return await self.cost_analyzer.get_recommendations()
            else:
                return {
                    "message": "I'm not sure how to help with that. Could you rephrase your request?"
                }
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {e}")
            raise
    
    def get_available_commands(self) -> str:
        """Get formatted string of available commands."""
        return "\n".join(f"- {cmd}: {desc}" for cmd, desc in self.commands.items()) 