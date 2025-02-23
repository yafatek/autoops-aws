"""
AWS Cost Optimization Agent.

This module provides basic AWS cost analysis and optimization recommendations.
"""

import logging
from typing import Dict, Any, List
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class CostOptimizer:
    """Handles AWS cost analysis and optimization."""
    
    def __init__(self):
        """Initialize the cost optimizer."""
        self.cost_explorer = boto3.client('ce')
        self.ec2 = boto3.client('ec2')
        self.rds = boto3.client('rds')
    
    async def analyze_current_costs(self, time_period: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze current AWS costs.
        
        Args:
            time_period: Dict with 'Start' and 'End' dates
            
        Returns:
            Dict containing cost analysis
        """
        try:
            # Get cost and usage data
            response = self.cost_explorer.get_cost_and_usage(
                TimePeriod=time_period,
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
                ]
            )
            
            return {
                "costs": response['ResultsByTime'],
                "total": sum(float(group['Metrics']['UnblendedCost']['Amount'])
                           for result in response['ResultsByTime']
                           for group in result['Groups'])
            }
            
        except ClientError as e:
            logger.error(f"Error analyzing costs: {e}")
            raise
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get cost optimization recommendations.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        try:
            # Check for unused EC2 instances
            ec2_instances = self.ec2.describe_instances()
            for reservation in ec2_instances['Reservations']:
                for instance in reservation['Instances']:
                    if instance['State']['Name'] == 'running':
                        # Check CPU utilization (you'd typically want to check CloudWatch metrics)
                        recommendations.append({
                            "type": "EC2",
                            "resource_id": instance['InstanceId'],
                            "recommendation": "Review if this instance is needed",
                            "potential_savings": "Varies based on instance type"
                        })
            
            # Check for unattached EBS volumes
            volumes = self.ec2.describe_volumes()
            for volume in volumes['Volumes']:
                if not volume['Attachments']:
                    recommendations.append({
                        "type": "EBS",
                        "resource_id": volume['VolumeId'],
                        "recommendation": "Delete unused EBS volume",
                        "potential_savings": f"${float(volume['Size']) * 0.10}/month"  # Example rate
                    })
            
            # Add RDS optimization recommendations
            rds_instances = self.rds.describe_db_instances()
            for instance in rds_instances['DBInstances']:
                recommendations.append({
                    "type": "RDS",
                    "resource_id": instance['DBInstanceIdentifier'],
                    "recommendation": "Consider scaling down during non-peak hours",
                    "potential_savings": "20-50% of instance cost"
                })
                
        except ClientError as e:
            logger.error(f"Error getting recommendations: {e}")
            raise
        
        return recommendations
    
    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """Format recommendations for display."""
        if not recommendations:
            return "No optimization recommendations found."
        
        formatted = "Cost Optimization Recommendations:\n\n"
        for i, rec in enumerate(recommendations, 1):
            formatted += f"{i}. {rec['type']} - {rec['resource_id']}\n"
            formatted += f"   Recommendation: {rec['recommendation']}\n"
            formatted += f"   Potential Savings: {rec['potential_savings']}\n\n"
        
        return formatted 