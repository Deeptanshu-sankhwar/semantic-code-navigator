"""Security Audit Agent for automated security analysis and vulnerability assessment."""

import re
from typing import Dict, List, Optional, Any, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .agent_manager import AgentManager
from ..config import config

console = Console()


class SecurityAuditAgent:
    """Specialized agent for security auditing and vulnerability assessment.
    
    This agent provides comprehensive security analysis including:
    - OWASP Top 10 vulnerability detection
    - Authentication and authorization review
    - Input validation and injection attack prevention
    - Data protection and encryption analysis
    - Configuration security assessment
    - Compliance and security best practices
    """
    
    def __init__(self, agent_name: str = "security_auditor"):
        self.agent_name = agent_name
        self.agent_manager = None
        
        self.security_categories = [
            "injection", "authentication", "authorization", "data_exposure",
            "xml_external_entities", "broken_access_control", "security_misconfiguration",
            "xss", "insecure_deserialization", "vulnerable_components", "logging_monitoring"
        ]
        
    def __enter__(self):
        """Context manager entry."""
        self.agent_manager = AgentManager()
        self.agent_manager.__enter__()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.agent_manager:
            self.agent_manager.__exit__(exc_type, exc_val, exc_tb)
    
    def ensure_agent_exists(self) -> bool:
        """Ensure the security audit agent exists, create if not."""
        try:
            agent_info = self.agent_manager.get_agent_info(self.agent_name)
            if agent_info:
                return True
            
            console.print(f"Creating security audit agent: {self.agent_name}", style="blue")
            success = self.agent_manager.create_agent(self.agent_name, "security-auditor")
            
            if success:
                console.print(f"Security audit agent created successfully", style="green")
                return True
            else:
                console.print(f"Failed to create security audit agent", style="red")
                return False
                
        except Exception as e:
            console.print(f"Error ensuring agent exists: {e}", style="red")
            return False
    
    def perform_comprehensive_security_audit(self) -> Optional[Dict[str, Any]]:
        """Perform comprehensive security audit of the entire codebase."""
        try:
            if not self.ensure_agent_exists():
                return None
            
            query = """Perform a comprehensive security audit of this codebase.
            
            Please analyze for OWASP Top 10 vulnerabilities and other security issues:
            
            1. **Injection Attacks** (SQL, NoSQL, OS, LDAP injection)
            2. **Broken Authentication** (session management, password policies)
            3. **Sensitive Data Exposure** (encryption, data handling)
            4. **XML External Entities (XXE)** (XML processing vulnerabilities)
            5. **Broken Access Control** (authorization flaws)
            6. **Security Misconfiguration** (default configs, error handling)
            7. **Cross-Site Scripting (XSS)** (input validation, output encoding)
            8. **Insecure Deserialization** (object deserialization risks)
            9. **Using Components with Known Vulnerabilities** (dependency analysis)
            10. **Insufficient Logging & Monitoring** (security event tracking)
            
            For each vulnerability found:
            - Describe the specific issue and location
            - Assess the risk level (Critical, High, Medium, Low)
            - Provide concrete remediation steps
            - Show secure code examples where applicable
            
            Focus on practical, actionable security improvements."""
            
            response = self.agent_manager.query_agent(self.agent_name, query)
            
            if response:
                audit_result = self._parse_security_audit(response)
                return audit_result
            
            return None
            
        except Exception as e:
            console.print(f"Security audit failed: {e}", style="red")
            return None
    
    def audit_authentication_system(self) -> Optional[Dict[str, Any]]:
        """Audit authentication and authorization mechanisms."""
        try:
            if not self.ensure_agent_exists():
                return None
            
            query = """Audit the authentication and authorization systems in this codebase.
            
            Please analyze:
            1. **Authentication Mechanisms**:
               - Password handling and hashing
               - Multi-factor authentication implementation
               - Session management and token handling
               - Login/logout functionality
            
            2. **Authorization Controls**:
               - Role-based access control (RBAC)
               - Permission checks and enforcement
               - Privilege escalation prevention
               - API endpoint protection
            
            3. **Session Security**:
               - Session token generation and validation
               - Session timeout and invalidation
               - CSRF protection
               - Secure cookie configuration
            
            4. **Common Authentication Vulnerabilities**:
               - Brute force attack protection
               - Account lockout mechanisms
               - Password reset security
               - Credential storage security
            
            Provide specific findings with risk assessments and remediation guidance."""
            
            response = self.agent_manager.query_agent(self.agent_name, query)
            
            if response:
                auth_result = self._parse_authentication_audit(response)
                return auth_result
            
            return None
            
        except Exception as e:
            console.print(f"Authentication audit failed: {e}", style="red")
            return None
    
    def audit_input_validation(self) -> Optional[Dict[str, Any]]:
        """Audit input validation and injection attack prevention."""
        try:
            if not self.ensure_agent_exists():
                return None
            
            query = """Audit input validation and injection attack prevention in this codebase.
            
            Please analyze:
            1. **SQL Injection Prevention**:
               - Parameterized queries usage
               - ORM security practices
               - Database access patterns
            
            2. **Cross-Site Scripting (XSS) Prevention**:
               - Input sanitization
               - Output encoding
               - Content Security Policy (CSP)
            
            3. **Command Injection Prevention**:
               - System command execution
               - File path validation
               - Shell command sanitization
            
            4. **Other Injection Types**:
               - LDAP injection
               - XML injection
               - Template injection
               - NoSQL injection
            
            5. **Input Validation Patterns**:
               - Data type validation
               - Length and format checks
               - Whitelist vs blacklist approaches
               - Server-side validation enforcement
            
            Identify specific vulnerabilities and provide secure coding examples."""
            
            response = self.agent_manager.query_agent(self.agent_name, query)
            
            if response:
                validation_result = self._parse_input_validation_audit(response)
                return validation_result
            
            return None
            
        except Exception as e:
            console.print(f"Input validation audit failed: {e}", style="red")
            return None
    
    def audit_data_protection(self) -> Optional[Dict[str, Any]]:
        """Audit data protection and encryption practices."""
        try:
            if not self.ensure_agent_exists():
                return None
            
            query = """Audit data protection and encryption practices in this codebase.
            
            Please analyze:
            1. **Data Encryption**:
               - Encryption at rest
               - Encryption in transit (TLS/SSL)
               - Encryption key management
               - Algorithm strength and implementation
            
            2. **Sensitive Data Handling**:
               - PII (Personally Identifiable Information) protection
               - Credit card and payment data security
               - Password and credential storage
               - API key and secret management
            
            3. **Data Storage Security**:
               - Database security configuration
               - File storage permissions
               - Backup security
               - Data retention policies
            
            4. **Data Transmission Security**:
               - HTTPS enforcement
               - Certificate validation
               - Secure communication protocols
               - Data integrity verification
            
            5. **Compliance Considerations**:
               - GDPR compliance
               - PCI DSS requirements
               - HIPAA considerations
               - Industry-specific regulations
            
            Focus on identifying data exposure risks and protection gaps."""
            
            response = self.agent_manager.query_agent(self.agent_name, query)
            
            if response:
                data_protection_result = self._parse_data_protection_audit(response)
                return data_protection_result
            
            return None
            
        except Exception as e:
            console.print(f"Data protection audit failed: {e}", style="red")
            return None
    
    def audit_configuration_security(self) -> Optional[Dict[str, Any]]:
        """Audit security configuration and deployment settings."""
        try:
            if not self.ensure_agent_exists():
                return None
            
            query = """Audit security configuration and deployment settings in this codebase.
            
            Please analyze:
            1. **Application Configuration**:
               - Default credentials and settings
               - Debug mode and development settings
               - Error message disclosure
               - Security headers configuration
            
            2. **Server and Infrastructure Security**:
               - Web server configuration
               - Database security settings
               - Network security configuration
               - Firewall and access control rules
            
            3. **Environment and Deployment Security**:
               - Environment variable handling
               - Configuration file security
               - Container security (if applicable)
               - Cloud service configuration
            
            4. **Dependency and Component Security**:
               - Third-party library vulnerabilities
               - Package manager security
               - Software version management
               - Security update processes
            
            5. **Monitoring and Logging**:
               - Security event logging
               - Log protection and integrity
               - Monitoring and alerting setup
               - Incident response capabilities
            
            Identify misconfigurations and provide hardening recommendations."""
            
            response = self.agent_manager.query_agent(self.agent_name, query)
            
            if response:
                config_result = self._parse_configuration_audit(response)
                return config_result
            
            return None
            
        except Exception as e:
            console.print(f"Configuration audit failed: {e}", style="red")
            return None
    
    def generate_security_report(self, include_all: bool = True) -> Optional[Dict[str, Any]]:
        """Generate comprehensive security audit report."""
        try:
            console.print("Generating comprehensive security audit report...", style="blue")
            
            report = {
                "timestamp": None,
                "overall_security_posture": None,
                "authentication_audit": None,
                "input_validation_audit": None,
                "data_protection_audit": None,
                "configuration_audit": None,
                "vulnerability_summary": [],
                "risk_assessment": {},
                "remediation_priorities": []
            }
            
            console.print("Performing comprehensive security audit...", style="dim")
            overall_audit = self.perform_comprehensive_security_audit()
            if overall_audit:
                report["overall_security_posture"] = overall_audit
            
            if include_all:
                console.print("Auditing authentication systems...", style="dim")
                auth_audit = self.audit_authentication_system()
                if auth_audit:
                    report["authentication_audit"] = auth_audit
                
                console.print("Auditing input validation...", style="dim")
                validation_audit = self.audit_input_validation()
                if validation_audit:
                    report["input_validation_audit"] = validation_audit
                
                console.print("Auditing data protection...", style="dim")
                data_audit = self.audit_data_protection()
                if data_audit:
                    report["data_protection_audit"] = data_audit
                
                console.print("Auditing security configuration...", style="dim")
                config_audit = self.audit_configuration_security()
                if config_audit:
                    report["configuration_audit"] = config_audit
            
            report["vulnerability_summary"] = self._extract_vulnerabilities(report)
            report["risk_assessment"] = self._assess_overall_risk(report)
            report["remediation_priorities"] = self._prioritize_remediation(report)
            
            return report
            
        except Exception as e:
            console.print(f"Security report generation failed: {e}", style="red")
            return None
    
    def _parse_security_audit(self, response: str) -> Dict[str, Any]:
        """Parse comprehensive security audit response."""
        try:
            vulnerabilities = []
            
            owasp_patterns = [
                (r'injection', 'Injection'),
                (r'authentication', 'Broken Authentication'),
                (r'sensitive.*data', 'Sensitive Data Exposure'),
                (r'xxe', 'XML External Entities'),
                (r'access.*control', 'Broken Access Control'),
                (r'misconfiguration', 'Security Misconfiguration'),
                (r'xss|cross.*site', 'Cross-Site Scripting'),
                (r'deserialization', 'Insecure Deserialization'),
                (r'vulnerable.*components', 'Vulnerable Components'),
                (r'logging.*monitoring', 'Insufficient Logging & Monitoring')
            ]
            
            for pattern, category in owasp_patterns:
                matches = re.finditer(f'{pattern}.*?(?=\n(?:\d+\.|\*|[A-Z])|$)', 
                                    response, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    vulnerabilities.append({
                        "category": category,
                        "description": match.group(0).strip(),
                        "risk_level": self._extract_risk_level(match.group(0))
                    })
            
            return {
                "vulnerabilities_found": vulnerabilities,
                "total_issues": len(vulnerabilities),
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "raw_response": response,
                "parsing_error": str(e)
            }
    
    def _parse_authentication_audit(self, response: str) -> Dict[str, Any]:
        """Parse authentication audit response."""
        try:
            auth_issues = []
            
            auth_patterns = [
                (r'password.*hash', 'Password Hashing'),
                (r'session.*management', 'Session Management'),
                (r'token.*handling', 'Token Handling'),
                (r'multi.*factor', 'Multi-Factor Authentication'),
                (r'brute.*force', 'Brute Force Protection'),
                (r'csrf', 'CSRF Protection')
            ]
            
            for pattern, issue_type in auth_patterns:
                matches = re.finditer(f'{pattern}.*?(?=\n(?:\d+\.|\*|[A-Z])|$)', 
                                    response, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    auth_issues.append({
                        "issue_type": issue_type,
                        "description": match.group(0).strip(),
                        "risk_level": self._extract_risk_level(match.group(0))
                    })
            
            return {
                "authentication_issues": auth_issues,
                "total_auth_issues": len(auth_issues),
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "raw_response": response,
                "parsing_error": str(e)
            }
    
    def _parse_input_validation_audit(self, response: str) -> Dict[str, Any]:
        """Parse input validation audit response."""
        try:
            validation_issues = []
            
            validation_patterns = [
                (r'sql.*injection', 'SQL Injection'),
                (r'xss|cross.*site.*scripting', 'Cross-Site Scripting'),
                (r'command.*injection', 'Command Injection'),
                (r'ldap.*injection', 'LDAP Injection'),
                (r'xml.*injection', 'XML Injection'),
                (r'input.*validation', 'Input Validation')
            ]
            
            for pattern, issue_type in validation_patterns:
                matches = re.finditer(f'{pattern}.*?(?=\n(?:\d+\.|\*|[A-Z])|$)', 
                                    response, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    validation_issues.append({
                        "issue_type": issue_type,
                        "description": match.group(0).strip(),
                        "risk_level": self._extract_risk_level(match.group(0))
                    })
            
            return {
                "validation_issues": validation_issues,
                "total_validation_issues": len(validation_issues),
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "raw_response": response,
                "parsing_error": str(e)
            }
    
    def _parse_data_protection_audit(self, response: str) -> Dict[str, Any]:
        """Parse data protection audit response."""
        try:
            data_issues = []
            
            data_patterns = [
                (r'encryption', 'Encryption'),
                (r'sensitive.*data', 'Sensitive Data'),
                (r'pii|personally.*identifiable', 'PII Protection'),
                (r'tls|ssl', 'Transport Security'),
                (r'key.*management', 'Key Management'),
                (r'data.*storage', 'Data Storage Security')
            ]
            
            for pattern, issue_type in data_patterns:
                matches = re.finditer(f'{pattern}.*?(?=\n(?:\d+\.|\*|[A-Z])|$)', 
                                    response, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    data_issues.append({
                        "issue_type": issue_type,
                        "description": match.group(0).strip(),
                        "risk_level": self._extract_risk_level(match.group(0))
                    })
            
            return {
                "data_protection_issues": data_issues,
                "total_data_issues": len(data_issues),
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "raw_response": response,
                "parsing_error": str(e)
            }
    
    def _parse_configuration_audit(self, response: str) -> Dict[str, Any]:
        """Parse configuration audit response."""
        try:
            config_issues = []
            
            config_patterns = [
                (r'default.*credentials', 'Default Credentials'),
                (r'debug.*mode', 'Debug Mode'),
                (r'error.*message', 'Error Message Disclosure'),
                (r'security.*headers', 'Security Headers'),
                (r'dependency|vulnerable.*components', 'Vulnerable Dependencies'),
                (r'logging.*monitoring', 'Logging & Monitoring')
            ]
            
            for pattern, issue_type in config_patterns:
                matches = re.finditer(f'{pattern}.*?(?=\n(?:\d+\.|\*|[A-Z])|$)', 
                                    response, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    config_issues.append({
                        "issue_type": issue_type,
                        "description": match.group(0).strip(),
                        "risk_level": self._extract_risk_level(match.group(0))
                    })
            
            return {
                "configuration_issues": config_issues,
                "total_config_issues": len(config_issues),
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "raw_response": response,
                "parsing_error": str(e)
            }
    
    def _extract_risk_level(self, text: str) -> str:
        """Extract risk level from text."""
        text_lower = text.lower()
        if 'critical' in text_lower:
            return 'Critical'
        elif 'high' in text_lower:
            return 'High'
        elif 'medium' in text_lower:
            return 'Medium'
        elif 'low' in text_lower:
            return 'Low'
        else:
            return 'Medium'
    
    def _extract_vulnerabilities(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all vulnerabilities from the report."""
        all_vulnerabilities = []
        
        for section_key, section_data in report.items():
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    if 'issues' in key or 'vulnerabilities' in key:
                        if isinstance(value, list):
                            all_vulnerabilities.extend(value)
        
        return all_vulnerabilities
    
    def _assess_overall_risk(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall security risk based on findings."""
        vulnerabilities = self._extract_vulnerabilities(report)
        
        risk_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
        
        for vuln in vulnerabilities:
            risk_level = vuln.get('risk_level', 'Medium')
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        risk_score = (risk_counts['Critical'] * 4 + 
                     risk_counts['High'] * 3 + 
                     risk_counts['Medium'] * 2 + 
                     risk_counts['Low'] * 1)
        
        if risk_score >= 10:
            overall_risk = 'Critical'
        elif risk_score >= 6:
            overall_risk = 'High'
        elif risk_score >= 3:
            overall_risk = 'Medium'
        else:
            overall_risk = 'Low'
        
        return {
            'overall_risk_level': overall_risk,
            'risk_score': risk_score,
            'vulnerability_counts': risk_counts,
            'total_vulnerabilities': sum(risk_counts.values())
        }
    
    def _prioritize_remediation(self, report: Dict[str, Any]) -> List[str]:
        """Prioritize remediation actions based on risk assessment."""
        vulnerabilities = self._extract_vulnerabilities(report)
        
        priority_order = {'Critical': 1, 'High': 2, 'Medium': 3, 'Low': 4}
        sorted_vulns = sorted(vulnerabilities, 
                            key=lambda x: priority_order.get(x.get('risk_level', 'Medium'), 3))
        
        priorities = []
        for i, vuln in enumerate(sorted_vulns[:10], 1):
            issue_type = vuln.get('issue_type', vuln.get('category', 'Security Issue'))
            risk_level = vuln.get('risk_level', 'Medium')
            priorities.append(f"{i}. [{risk_level}] {issue_type}")
        
        return priorities
    
    def display_security_audit_results(self, audit_result: Dict[str, Any]):
        """Display security audit results in a formatted way."""
        if not audit_result:
            console.print("No security audit results to display", style="yellow")
            return
        
        console.print("\n[bold red]Security Audit Results[/bold red]")
        
        if "vulnerabilities_found" in audit_result:
            vulnerabilities = audit_result["vulnerabilities_found"]
            
            risk_groups = {'Critical': [], 'High': [], 'Medium': [], 'Low': []}
            for vuln in vulnerabilities:
                risk_level = vuln.get('risk_level', 'Medium')
                risk_groups[risk_level].append(vuln)
            
            for risk_level, vulns in risk_groups.items():
                if vulns:
                    color = {'Critical': 'red', 'High': 'bright_red', 'Medium': 'yellow', 'Low': 'blue'}[risk_level]
                    console.print(f"\n[bold {color}]{risk_level} Risk Issues ({len(vulns)})[/bold {color}]")
                    
                    for vuln in vulns:
                        console.print(Panel(
                            vuln['description'],
                            title=f"[bold]{vuln['category']}[/bold]",
                            border_style=color
                        ))
        
        total_issues = audit_result.get("total_issues", 0)
        console.print(f"\n[bold]Total Security Issues Found: {total_issues}[/bold]")
    
    def display_comprehensive_security_report(self, report: Dict[str, Any]):
        """Display comprehensive security report."""
        if not report:
            console.print("No security report to display", style="yellow")
            return
        
        console.print("\n[bold red]Comprehensive Security Audit Report[/bold red]\n")
        
        if report.get("risk_assessment"):
            risk_data = report["risk_assessment"]
            console.print("[bold]Security Risk Assessment[/bold]")
            
            risk_table = Table(show_header=True, header_style="bold red")
            risk_table.add_column("Risk Level", style="bold")
            risk_table.add_column("Count", style="cyan")
            risk_table.add_column("Overall Risk", style="red")
            
            risk_counts = risk_data.get("vulnerability_counts", {})
            for risk_level, count in risk_counts.items():
                if count > 0:
                    risk_table.add_row(risk_level, str(count), "")
            
            overall_risk = risk_data.get("overall_risk_level", "Unknown")
            risk_table.add_row("OVERALL", "", f"[bold]{overall_risk}[/bold]")
            
            console.print(risk_table)
            console.print()
        
        if report.get("remediation_priorities"):
            console.print("[bold yellow]Top Remediation Priorities[/bold yellow]")
            priorities = report["remediation_priorities"]
            for priority in priorities:
                console.print(f"  {priority}")
            console.print()
        
        audit_sections = [
            ("overall_security_posture", "Overall Security Posture"),
            ("authentication_audit", "Authentication Security"),
            ("input_validation_audit", "Input Validation Security"),
            ("data_protection_audit", "Data Protection Security"),
            ("configuration_audit", "Configuration Security")
        ]
        
        for section_key, section_title in audit_sections:
            if report.get(section_key):
                console.print(f"[bold cyan]{section_title}[/bold cyan]")
                section_data = report[section_key]
                
                for key, value in section_data.items():
                    if 'issues' in key and isinstance(value, list):
                        for issue in value[:3]:
                            issue_type = issue.get('issue_type', issue.get('category', 'Security Issue'))
                            risk_level = issue.get('risk_level', 'Medium')
                            description = issue.get('description', '')[:200] + "..."
                            
                            console.print(Panel(
                                description,
                                title=f"[bold]{issue_type}[/bold] - [{risk_level}]",
                                border_style="cyan"
                            ))
                console.print() 