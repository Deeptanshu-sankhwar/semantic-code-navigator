"""Specialized Code Review Agent with enhanced code analysis capabilities."""

from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
import re

from .agent_manager import AgentManager

console = Console()


class CodeReviewAgent:
    """Specialized agent for comprehensive code review with codebase context."""
    
    def __init__(self, agent_name: str = "code_reviewer"):
        self.agent_name = agent_name
        self.agent_manager = None
    
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
        """Ensure the code review agent exists, create if not.
        
        Returns:
            bool: True if agent exists or was created successfully
        """
        try:
            existing_agents = self.agent_manager.list_agents()
            agent_names = [agent['name'] for agent in existing_agents]
            
            if self.agent_name in agent_names:
                console.print(f"Code review agent '{self.agent_name}' is ready", style="green")
                return True
            
            console.print(f"Creating code review agent '{self.agent_name}'...", style="blue")
            success = self.agent_manager.create_agent(self.agent_name, "code-reviewer")
            
            if success:
                console.print(f"Code review agent created successfully!", style="green")
                return True
            else:
                console.print(f"Failed to create code review agent", style="red")
                return False
                
        except Exception as e:
            console.print(f"Error ensuring agent exists: {e}", style="red")
            return False
    
    def review_code(self, code: str, context: Optional[str] = None, 
                   focus_areas: List[str] = None) -> Optional[Dict[str, Any]]:
        """Perform comprehensive code review.
        
        Args:
            code: Code to review
            context: Additional context about the code
            focus_areas: Specific areas to focus on (security, performance, etc.)
            
        Returns:
            Optional[Dict]: Structured review results or None if failed
        """
        try:
            if not self.ensure_agent_exists():
                return None
            
            question = self._build_review_question(code, context, focus_areas)
            
            console.print(Panel.fit(
                "[bold blue]Code Review in Progress[/bold blue]\n"
                "Analyzing code with full codebase context...",
                border_style="blue"
            ))
            
            response = self.agent_manager.query_agent(self.agent_name, question)
            
            if response:
                structured_review = self._parse_review_response(response)
                return structured_review
            else:
                console.print("No response from code review agent", style="red")
                return None
                
        except Exception as e:
            console.print(f"Code review failed: {e}", style="red")
            return None
    
    def review_function(self, function_name: str, language: str = None) -> Optional[Dict[str, Any]]:
        """Review a specific function from the knowledge base.
        
        Args:
            function_name: Name of the function to review
            language: Programming language filter
            
        Returns:
            Optional[Dict]: Review results or None if failed
        """
        try:
            search_filters = {"function_name": function_name}
            if language:
                search_filters["language"] = language
            
            search_results = self.agent_manager.client.semantic_search(
                query=f"function {function_name}",
                filters=search_filters,
                limit=1
            )
            
            if not search_results:
                console.print(f"Function '{function_name}' not found in knowledge base", style="yellow")
                return None
            
            function_data = search_results[0]
            code = function_data.get('chunk_content', '')
            filepath = function_data.get('filepath', 'unknown')
            lang = function_data.get('language', 'unknown')
            
            context = f"Function: {function_name}\nFile: {filepath}\nLanguage: {lang}"
            
            return self.review_code(code, context)
            
        except Exception as e:
            console.print(f"Function review failed: {e}", style="red")
            return None
    
    def security_audit(self, code: str, context: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Perform focused security audit of code.
        
        Args:
            code: Code to audit
            context: Additional context
            
        Returns:
            Optional[Dict]: Security audit results
        """
        return self.review_code(
            code, 
            context, 
            focus_areas=["security", "vulnerabilities", "input-validation", "authentication"]
        )
    
    def performance_review(self, code: str, context: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Perform focused performance review of code.
        
        Args:
            code: Code to review
            context: Additional context
            
        Returns:
            Optional[Dict]: Performance review results
        """
        return self.review_code(
            code,
            context,
            focus_areas=["performance", "optimization", "scalability", "efficiency"]
        )
    
    def _build_review_question(self, code: str, context: Optional[str] = None, 
                              focus_areas: List[str] = None) -> str:
        """Build a comprehensive review question.
        
        Args:
            code: Code to review
            context: Additional context
            focus_areas: Areas to focus on
            
        Returns:
            str: Formatted question for the agent
        """
        question_parts = []
        
        if focus_areas:
            focus_text = ", ".join(focus_areas)
            question_parts.append(f"Please focus specifically on: {focus_text}")
        
        if context:
            question_parts.append(f"Context: {context}")
        
        question_parts.append("Please perform a comprehensive code review of the following code:")
        question_parts.append(f"\n```\n{code}\n```")
        
        question_parts.append("""
Please provide:
1. Overall assessment (LGTM/Needs Changes/Major Issues)
2. Specific issues categorized by type (Security, Performance, Logic, Style)
3. Concrete suggestions with code examples where helpful
4. References to similar patterns in the codebase if applicable
5. Priority level for each issue (Critical/High/Medium/Low)
        """)
        
        return "\n\n".join(question_parts)
    
    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """Parse the agent's review response into structured data.
        
        Args:
            response: Raw response from the agent
            
        Returns:
            Dict: Structured review data
        """
        try:
            structured = {
                "overall_assessment": "Unknown",
                "issues": [],
                "recommendations": [],
                "codebase_references": [],
                "raw_response": response
            }
            
            assessment_patterns = [
                r"overall assessment[:\s]*([^\n]+)",
                r"assessment[:\s]*([^\n]+)",
                r"(LGTM|Needs Changes|Major Issues)",
            ]
            
            for pattern in assessment_patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    structured["overall_assessment"] = match.group(1).strip()
                    break
            
            categories = ["security", "performance", "logic", "style", "critical", "high", "medium", "low"]
            
            for category in categories:
                category_pattern = rf"{category}[:\s]*([^\n]+(?:\n(?!\w+:)[^\n]+)*)"
                matches = re.findall(category_pattern, response, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    structured["issues"].append({
                        "category": category.title(),
                        "description": match.strip(),
                        "priority": self._extract_priority(match)
                    })
            
            rec_patterns = [
                r"recommend(?:ation)?s?[:\s]*([^\n]+(?:\n(?!\w+:)[^\n]+)*)",
                r"suggest(?:ion)?s?[:\s]*([^\n]+(?:\n(?!\w+:)[^\n]+)*)",
            ]
            
            for pattern in rec_patterns:
                matches = re.findall(pattern, response, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    structured["recommendations"].append(match.strip())
            
            ref_patterns = [
                r"similar.*(?:pattern|function|code).*in.*codebase",
                r"reference.*(?:existing|similar).*implementation",
                r"found.*(?:pattern|example).*in.*repository"
            ]
            
            for pattern in ref_patterns:
                matches = re.findall(pattern, response, re.IGNORECASE)
                structured["codebase_references"].extend(matches)
            
            return structured
            
        except Exception as e:
            console.print(f"Warning: Could not parse review response: {e}", style="yellow")
            return {
                "overall_assessment": "Unknown",
                "issues": [],
                "recommendations": [],
                "codebase_references": [],
                "raw_response": response
            }
    
    def _extract_priority(self, text: str) -> str:
        """Extract priority level from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            str: Priority level (Critical/High/Medium/Low)
        """
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["critical", "severe", "urgent"]):
            return "Critical"
        elif any(word in text_lower for word in ["high", "important", "major"]):
            return "High"
        elif any(word in text_lower for word in ["medium", "moderate", "minor"]):
            return "Medium"
        else:
            return "Low"
    
    def display_review_results(self, review_results: Dict[str, Any]):
        """Display code review results in a formatted way.
        
        Args:
            review_results: Structured review results
        """
        if not review_results:
            console.print("No review results to display", style="yellow")
            return
        
        assessment = review_results.get("overall_assessment", "Unknown")
        assessment_style = "green" if "LGTM" in assessment else "yellow" if "Changes" in assessment else "red"
        
        console.print(Panel.fit(
            f"[bold {assessment_style}]Overall Assessment: {assessment}[/bold {assessment_style}]",
            border_style=assessment_style
        ))
        
        issues = review_results.get("issues", [])
        if issues:
            console.print("\n[bold red]Issues Found:[/bold red]")
            
            issues_table = Table(show_header=True, header_style="bold red")
            issues_table.add_column("Priority", style="red")
            issues_table.add_column("Category", style="yellow")
            issues_table.add_column("Description", style="white")
            
            for issue in issues:
                issues_table.add_row(
                    issue.get("priority", "Unknown"),
                    issue.get("category", "Unknown"),
                    issue.get("description", "No description")
                )
            
            console.print(issues_table)
        
        recommendations = review_results.get("recommendations", [])
        if recommendations:
            console.print("\n[bold green]Recommendations:[/bold green]")
            for i, rec in enumerate(recommendations, 1):
                console.print(f"{i}. {rec}")
        
        references = review_results.get("codebase_references", [])
        if references:
            console.print("\n[bold blue]Codebase References:[/bold blue]")
            for i, ref in enumerate(references, 1):
                console.print(f"{i}. {ref}")
        
        if console.is_terminal and hasattr(console, '_width') and console._width > 120:
            console.print("\n[bold dim]Full Review Response:[/bold dim]")
            console.print(Panel(review_results.get("raw_response", "No response"), 
                              border_style="dim", expand=False)) 