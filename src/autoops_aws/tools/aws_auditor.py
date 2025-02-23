"""
AWS Auditor Tool.

This tool performs security and compliance checks on AWS resources.
"""

import logging
from typing import Dict, Any, List
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class AWSAuditor:
    """Tool for auditing AWS resources."""
    
    def __init__(self):
        """Initialize the AWS auditor."""
        self.iam = boto3.client('iam')
        self.ec2 = boto3.client('ec2')
        self.s3 = boto3.client('s3')
        self.config = boto3.client('config')
        
    async def run_audit(self) -> Dict[str, Any]:
        """
        Run a comprehensive audit of AWS resources.
        
        Returns:
            Dict containing audit results and recommendations
        """
        try:
            results = {
                "iam": await self._audit_iam(),
                "security_groups": await self._audit_security_groups(),
                "s3": await self._audit_s3(),
                "compliance": await self._check_compliance(),
                "recommendations": []
            }
            
            # Generate recommendations based on findings
            results["recommendations"] = self._generate_recommendations(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error during audit: {e}")
            raise
    
    async def _audit_iam(self) -> Dict[str, Any]:
        """Audit IAM configurations."""
        try:
            findings = {
                "users": [],
                "roles": [],
                "policies": []
            }
            
            # Check IAM users
            users = self.iam.list_users()['Users']
            for user in users:
                user_findings = {
                    "username": user['UserName'],
                    "issues": []
                }
                
                # Check for access keys
                access_keys = self.iam.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']
                if len(access_keys) > 0:
                    for key in access_keys:
                        if key['Status'] == 'Active':
                            user_findings["issues"].append("Has active access keys")
                
                # Check for direct policy attachments
                attached_policies = self.iam.list_attached_user_policies(UserName=user['UserName'])
                if attached_policies['AttachedPolicies']:
                    user_findings["issues"].append("Has directly attached policies")
                
                if user_findings["issues"]:
                    findings["users"].append(user_findings)
            
            # Check roles
            roles = self.iam.list_roles()['Roles']
            for role in roles:
                role_findings = {
                    "rolename": role['RoleName'],
                    "issues": []
                }
                
                # Check for overly permissive trust relationships
                if '*' in str(role['AssumeRolePolicyDocument']):
                    role_findings["issues"].append("Overly permissive trust relationship")
                
                if role_findings["issues"]:
                    findings["roles"].append(role_findings)
            
            return findings
            
        except ClientError as e:
            logger.error(f"Error auditing IAM: {e}")
            raise
    
    async def _audit_security_groups(self) -> Dict[str, Any]:
        """Audit EC2 security groups."""
        try:
            findings = []
            
            security_groups = self.ec2.describe_security_groups()['SecurityGroups']
            for sg in security_groups:
                sg_findings = {
                    "group_id": sg['GroupId'],
                    "group_name": sg['GroupName'],
                    "issues": []
                }
                
                # Check for overly permissive rules
                for rule in sg['IpPermissions']:
                    if any(ip['CidrIp'] == '0.0.0.0/0' for ip in rule.get('IpRanges', [])):
                        sg_findings["issues"].append(f"Open to world on port(s): {rule.get('FromPort', 'ALL')}")
                
                if sg_findings["issues"]:
                    findings.append(sg_findings)
            
            return findings
            
        except ClientError as e:
            logger.error(f"Error auditing security groups: {e}")
            raise
    
    async def _audit_s3(self) -> Dict[str, Any]:
        """Audit S3 buckets."""
        try:
            findings = []
            
            buckets = self.s3.list_buckets()['Buckets']
            for bucket in buckets:
                bucket_findings = {
                    "bucket_name": bucket['Name'],
                    "issues": []
                }
                
                try:
                    # Check bucket policy
                    policy = self.s3.get_bucket_policy(Bucket=bucket['Name'])
                    if '*' in policy['Policy']:
                        bucket_findings["issues"].append("Public bucket policy")
                except ClientError as e:
                    if e.response['Error']['Code'] != 'NoSuchBucketPolicy':
                        raise
                
                # Check encryption
                try:
                    encryption = self.s3.get_bucket_encryption(Bucket=bucket['Name'])
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                        bucket_findings["issues"].append("No default encryption")
                    else:
                        raise
                
                if bucket_findings["issues"]:
                    findings.append(bucket_findings)
            
            return findings
            
        except ClientError as e:
            logger.error(f"Error auditing S3: {e}")
            raise
    
    async def _check_compliance(self) -> Dict[str, Any]:
        """Check AWS Config rules compliance."""
        try:
            compliance = {
                "compliant": [],
                "non_compliant": []
            }
            
            rules = self.config.describe_config_rules()['ConfigRules']
            for rule in rules:
                result = self.config.get_compliance_details_by_config_rule(
                    ConfigRuleName=rule['ConfigRuleName']
                )
                
                for evaluation in result['EvaluationResults']:
                    if evaluation['ComplianceType'] == 'NON_COMPLIANT':
                        compliance["non_compliant"].append({
                            "rule": rule['ConfigRuleName'],
                            "resource": evaluation['EvaluationResultIdentifier']['EvaluationResultQualifier']['ResourceId']
                        })
                    else:
                        compliance["compliant"].append(rule['ConfigRuleName'])
            
            return compliance
            
        except ClientError as e:
            logger.error(f"Error checking compliance: {e}")
            raise
    
    def _generate_recommendations(self, audit_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on audit findings."""
        recommendations = []
        
        # IAM recommendations
        if audit_results["iam"]["users"]:
            recommendations.append({
                "category": "Security",
                "service": "IAM",
                "priority": "High",
                "description": "Review IAM user permissions and access keys",
                "details": "Found users with direct policy attachments or active access keys"
            })
        
        # Security group recommendations
        if audit_results["security_groups"]:
            recommendations.append({
                "category": "Security",
                "service": "EC2",
                "priority": "High",
                "description": "Review security group rules",
                "details": "Found security groups with overly permissive rules"
            })
        
        # S3 recommendations
        if audit_results["s3"]:
            recommendations.append({
                "category": "Security",
                "service": "S3",
                "priority": "High",
                "description": "Review S3 bucket security",
                "details": "Found buckets with public access or missing encryption"
            })
        
        # Compliance recommendations
        if audit_results["compliance"]["non_compliant"]:
            recommendations.append({
                "category": "Compliance",
                "service": "AWS Config",
                "priority": "Medium",
                "description": "Address non-compliant resources",
                "details": f"Found {len(audit_results['compliance']['non_compliant'])} non-compliant resources"
            })
        
        return recommendations 