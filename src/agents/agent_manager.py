"""Agent Manager for creating, managing, and querying specialized AI agents."""

from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table

from ..config import config
from ..mindsdb_client import MindsDBClient
from .agent_templates import get_agent_template, list_agent_templates, get_template_info

console = Console()


class AgentManager:
    """Manages specialized AI agents that work with the knowledge base."""
    
    def __init__(self):
        self.client = None
        
    def __enter__(self):
        """Context manager entry."""
        self.client = MindsDBClient()
        self.client.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.client:
            self.client.disconnect()
    
    def create_agent(self, agent_name: str, template_name: str, **kwargs) -> bool:
        """Create a specialized agent using a template.
        
        Args:
            agent_name: Unique name for the agent
            template_name: Name of the template to use
            **kwargs: Additional parameters to override template defaults
            
        Returns:
            bool: True if agent creation was successful
        """
        try:
            template = get_agent_template(template_name)
            
            kb_context = self._get_kb_context()
            
            formatted_prompt = template["prompt_template"].format(
                kb_name=config.kb.name,
                total_chunks=kb_context.get("total_chunks", "unknown"),
                repo_context=kb_context.get("repo_context", "multiple repositories"),
                languages=kb_context.get("languages", "multiple languages"),
                question="{question}"
            )
            
            model = kwargs.get("model", template["model"])
            api_key_param = template["api_key_param"]
            api_key = getattr(config.kb, api_key_param)
            
            create_agent_sql = f"""
            CREATE AGENT {agent_name}
            USING
                model = '{model}',
                {api_key_param} = '{api_key}',
                include_knowledge_bases = ['{config.kb.name}'],
                prompt_template = '{formatted_prompt.replace("'", "''")}';
            """
            
            console.print(f"Creating agent: [bold cyan]{agent_name}[/bold cyan]", style="blue")
            console.print(f"Template: [dim]{template_name}[/dim]")
            console.print(f"Model: [dim]{model}[/dim]")
            
            self.client.execute_query(create_agent_sql)
            
            console.print(f"Agent '{agent_name}' created successfully!", style="green")
            return True
            
        except Exception as e:
            if "already exists" in str(e).lower():
                console.print(f"Agent '{agent_name}' already exists", style="yellow")
                return True
            else:
                console.print(f"Failed to create agent '{agent_name}': {e}", style="red")
                return False
    
    def query_agent(self, agent_name: str, question: str, **kwargs) -> Optional[str]:
        """Query an agent with a question.
        
        Args:
            agent_name: Name of the agent to query
            question: Question to ask the agent
            **kwargs: Additional query parameters
            
        Returns:
            Optional[str]: Agent's response or None if failed
        """
        try:
            console.print(f"Querying agent: [bold cyan]{agent_name}[/bold cyan]")
            console.print(f"Question: [dim]{question}[/dim]")
            
            query_sql = f"""
            SELECT answer
            FROM {agent_name}
            WHERE question = '{question.replace("'", "''")}';
            """
            
            with console.status("Agent is thinking..."):
                result = self.client.execute_query(query_sql)
            
            if result and len(result) > 0:
                answer = result[0].get('answer', 'No response received')
                console.print("Agent response received!", style="green")
                return answer
            else:
                console.print("No response from agent", style="yellow")
                return None
                
        except Exception as e:
            console.print(f"Failed to query agent '{agent_name}': {e}", style="red")
            return None
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents.
        
        Returns:
            List of agent information dictionaries
        """
        try:
            agents_query = "SHOW AGENTS;"
            result = self.client.execute_query(agents_query)
            
            agents = []
            for agent_row in result:
                agent_info = {
                    'name': agent_row.get('name', agent_row.get('NAME', '')),
                    'model': agent_row.get('model', 'unknown'),
                    'status': 'active',
                    'created': agent_row.get('created_at', 'unknown')
                }
                agents.append(agent_info)
            
            return agents
            
        except Exception as e:
            console.print(f"Failed to list agents: {e}", style="red")
            return []
    
    def delete_agent(self, agent_name: str) -> bool:
        """Delete an agent.
        
        Args:
            agent_name: Name of the agent to delete
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            console.print(f"Deleting agent: [bold red]{agent_name}[/bold red]")
            
            delete_sql = f"DROP AGENT {agent_name};"
            self.client.execute_query(delete_sql)
            
            console.print(f"Agent '{agent_name}' deleted successfully!", style="green")
            return True
            
        except Exception as e:
            if "does not exist" in str(e).lower():
                console.print(f"Agent '{agent_name}' does not exist", style="yellow")
                return True
            else:
                console.print(f"Failed to delete agent '{agent_name}': {e}", style="red")
                return False
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Optional[Dict]: Agent information or None if not found
        """
        try:
            query_sql = f"SHOW AGENTS WHERE name = '{agent_name}';"
            result = self.client.execute_query(query_sql)
            
            if result and len(result) > 0:
                return result[0]
            return None
            
        except Exception as e:
            console.print(f"Failed to get agent info for '{agent_name}': {e}", style="red")
            return None
    
    def _get_kb_context(self) -> Dict[str, Any]:
        """Get knowledge base context for agent prompts.
        
        Returns:
            Dict containing KB statistics and context
        """
        try:
            stats = self.client.get_stats()
            total_chunks = stats.get('total_records', 0)
            
            sample_query = f"SELECT * FROM {config.kb.name} LIMIT 10;"
            sample_result = self.client.execute_query(sample_query)
            
            languages = set()
            repos = set()
            
            for row in sample_result:
                if 'language' in row:
                    languages.add(row['language'])
                if 'repo' in row:
                    repos.add(row['repo'])
                
                content = row.get('chunk_content', '')
                if 'LANG:' in content:
                    import re
                    lang_match = re.search(r'LANG:([^\s]+)', content)
                    if lang_match:
                        languages.add(lang_match.group(1))
            
            return {
                'total_chunks': total_chunks,
                'languages': ', '.join(languages) if languages else 'multiple languages',
                'repo_context': f"{len(repos)} repositories" if repos else 'multiple repositories'
            }
            
        except Exception as e:
            console.print(f"Warning: Could not get KB context: {e}", style="yellow")
            return {
                'total_chunks': 'unknown',
                'languages': 'multiple languages', 
                'repo_context': 'multiple repositories'
            }
    
    def display_agents_table(self, agents: List[Dict[str, Any]]):
        """Display agents in a formatted table.
        
        Args:
            agents: List of agent information dictionaries
        """
        if not agents:
            console.print("No agents found", style="yellow")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Agent Name", style="cyan")
        table.add_column("Model", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Created", style="blue")
        
        for agent in agents:
            table.add_row(
                agent['name'],
                agent['model'],
                agent['status'],
                str(agent['created'])
            )
        
        console.print(table)
    
    def display_templates_table(self):
        """Display available agent templates in a formatted table."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Template Name", style="cyan")
        table.add_column("Specialization", style="yellow")
        table.add_column("Model", style="green")
        table.add_column("Description", style="white")
        
        for template_name in list_agent_templates():
            info = get_template_info(template_name)
            table.add_row(
                info['name'],
                info['specialization'].title(),
                info['model'],
                info['description']
            )
        
        console.print(table) 