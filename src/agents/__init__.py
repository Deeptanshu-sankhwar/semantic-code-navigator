"""Agent package for specialized AI agents with codebase context."""

from .agent_manager import AgentManager
from .code_review_agent import CodeReviewAgent
from .architecture_discovery_agent import ArchitectureDiscoveryAgent
from .security_audit_agent import SecurityAuditAgent
from .agent_templates import AGENT_TEMPLATES, get_agent_template, list_agent_templates

__all__ = [
    'AgentManager',
    'CodeReviewAgent', 
    'ArchitectureDiscoveryAgent',
    'SecurityAuditAgent',
    'AGENT_TEMPLATES',
    'get_agent_template',
    'list_agent_templates'
] 