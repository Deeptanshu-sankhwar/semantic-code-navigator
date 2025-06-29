"""Architecture Discovery Agent for deep codebase understanding and system analysis."""

import re
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.panel import Panel

from .agent_manager import AgentManager

console = Console()


class ArchitectureDiscoveryAgent:
    """Specialized agent for architecture discovery and system analysis.
    
    This agent provides deep codebase understanding by analyzing:
    - System architecture patterns and design decisions
    - Component relationships and dependencies
    - Data flow and system boundaries
    - Scalability and performance characteristics
    - Design pattern usage and architectural quality
    """
    
    def __init__(self, agent_name: str = "architecture_analyzer"):
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
        """Ensure the architecture discovery agent exists, create if not."""
        try:
            agent_info = self.agent_manager.get_agent_info(self.agent_name)
            if agent_info:
                return True
            
            console.print(f"Creating architecture discovery agent: {self.agent_name}", style="blue")
            success = self.agent_manager.create_agent(self.agent_name, "architect")
            
            if success:
                console.print(f"Architecture discovery agent created successfully", style="green")
                return True
            else:
                console.print(f"Failed to create architecture discovery agent", style="red")
                return False
                
        except Exception as e:
            console.print(f"Error ensuring agent exists: {e}", style="red")
            return False
    
    def analyze_system_architecture(self, focus_area: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Perform comprehensive system architecture analysis."""
        try:
            if not self.ensure_agent_exists():
                return None
            
            if focus_area:
                query = f"""Analyze the system architecture with focus on {focus_area}. 
                
                Please provide:
                1. Overall architectural assessment
                2. Key architectural patterns identified
                3. System components and their relationships
                4. {focus_area.title()} analysis and recommendations
                5. Potential improvements and best practices"""
            else:
                query = """Perform a comprehensive system architecture analysis of this codebase.
                
                Please analyze:
                1. Overall system architecture and design patterns
                2. Component organization and module structure  
                3. Data flow and system boundaries
                4. Dependency relationships and coupling
                5. Scalability and performance characteristics
                6. Architectural quality and improvement opportunities"""
            
            response = self.agent_manager.query_agent(self.agent_name, query)
            
            if response:
                analysis_result = self._parse_architecture_analysis(response, focus_area)
                return analysis_result
            
            return None
            
        except Exception as e:
            console.print(f"Architecture analysis failed: {e}", style="red")
            return None
    
    def discover_design_patterns(self) -> Optional[Dict[str, Any]]:
        """Discover and analyze design patterns used in the codebase."""
        try:
            if not self.ensure_agent_exists():
                return None
            
            query = """Identify and analyze design patterns used in this codebase.
            
            Please identify:
            1. Creational patterns (Singleton, Factory, Builder, etc.)
            2. Structural patterns (Adapter, Decorator, Facade, etc.) 
            3. Behavioral patterns (Observer, Strategy, Command, etc.)
            4. Architectural patterns (MVC, MVP, Repository, etc.)
            5. Domain-specific patterns relevant to this codebase
            
            For each pattern found:
            - Explain how it's implemented
            - Assess the implementation quality
            - Suggest improvements if needed
            - Show specific code examples from the codebase"""
            
            response = self.agent_manager.query_agent(self.agent_name, query)
            
            if response:
                patterns_result = self._parse_design_patterns(response)
                return patterns_result
            
            return None
            
        except Exception as e:
            console.print(f"Design pattern discovery failed: {e}", style="red")
            return None
    
    def analyze_component_dependencies(self) -> Optional[Dict[str, Any]]:
        """Analyze component dependencies and system coupling."""
        try:
            if not self.ensure_agent_exists():
                return None
            
            query = """Analyze the component dependencies and coupling in this system.
            
            Please analyze:
            1. Module/component dependency graph
            2. Coupling levels between components (tight vs loose coupling)
            3. Circular dependencies and potential issues
            4. Interface design and abstraction layers
            5. Dependency injection patterns used
            6. Opportunities to reduce coupling and improve modularity
            
            Provide specific recommendations for improving the dependency structure."""
            
            response = self.agent_manager.query_agent(self.agent_name, query)
            
            if response:
                dependencies_result = self._parse_dependencies_analysis(response)
                return dependencies_result
            
            return None
            
        except Exception as e:
            console.print(f"Dependencies analysis failed: {e}", style="red")
            return None
    
    def assess_scalability(self) -> Optional[Dict[str, Any]]:
        """Assess system scalability and performance characteristics."""
        try:
            if not self.ensure_agent_exists():
                return None
            
            query = """Assess the scalability and performance characteristics of this system.
            
            Please analyze:
            1. Horizontal vs vertical scaling capabilities
            2. Performance bottlenecks and constraints
            3. Resource utilization patterns
            4. Caching strategies and data access patterns
            5. Asynchronous processing and concurrency handling
            6. Database design and query optimization opportunities
            7. API design for scalability
            
            Provide specific recommendations for improving scalability and performance."""
            
            response = self.agent_manager.query_agent(self.agent_name, query)
            
            if response:
                scalability_result = self._parse_scalability_analysis(response)
                return scalability_result
            
            return None
            
        except Exception as e:
            console.print(f"Scalability analysis failed: {e}", style="red")
            return None
    
    def generate_architecture_report(self, include_all: bool = True) -> Optional[Dict[str, Any]]:
        """Generate comprehensive architecture discovery report."""
        try:
            console.print("Generating comprehensive architecture report...", style="blue")
            
            report = {
                "timestamp": None,
                "system_overview": None,
                "design_patterns": None,
                "dependencies": None,
                "scalability": None,
                "recommendations": []
            }
            
            console.print("Analyzing system architecture...", style="dim")
            system_analysis = self.analyze_system_architecture()
            if system_analysis:
                report["system_overview"] = system_analysis
            
            if include_all:
                console.print("Discovering design patterns...", style="dim")
                patterns = self.discover_design_patterns()
                if patterns:
                    report["design_patterns"] = patterns
                
                console.print("Analyzing dependencies...", style="dim")
                dependencies = self.analyze_component_dependencies()
                if dependencies:
                    report["dependencies"] = dependencies
                
                console.print("Assessing scalability...", style="dim")
                scalability = self.assess_scalability()
                if scalability:
                    report["scalability"] = scalability
            
            report["recommendations"] = self._generate_architecture_recommendations(report)
            
            return report
            
        except Exception as e:
            console.print(f"Architecture report generation failed: {e}", style="red")
            return None
    
    def _parse_architecture_analysis(self, response: str, focus_area: Optional[str] = None) -> Dict[str, Any]:
        """Parse architecture analysis response into structured data."""
        try:
            assessment_match = re.search(r'(?:Overall|System)\s+(?:Assessment|Architecture)[:\s]+(.*?)(?=\n\d+\.|\n[A-Z]|\n\n|$)', 
                                       response, re.DOTALL | re.IGNORECASE)
            
            patterns_match = re.search(r'(?:Patterns?|Design)[:\s]+(.*?)(?=\n\d+\.|\n[A-Z]|\n\n|$)', 
                                     response, re.DOTALL | re.IGNORECASE)
            
            return {
                "focus_area": focus_area,
                "overall_assessment": assessment_match.group(1).strip() if assessment_match else "No assessment found",
                "patterns_identified": patterns_match.group(1).strip() if patterns_match else "No patterns identified",
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "focus_area": focus_area,
                "raw_response": response,
                "parsing_error": str(e)
            }
    
    def _parse_design_patterns(self, response: str) -> Dict[str, Any]:
        """Parse design patterns analysis response."""
        try:
            patterns_found = []
            pattern_types = ["Creational", "Structural", "Behavioral", "Architectural"]
            
            for pattern_type in pattern_types:
                pattern_match = re.search(f'{pattern_type}.*?patterns?[:\s]+(.*?)(?=\n(?:Creational|Structural|Behavioral|Architectural)|\n\n|$)', 
                                        response, re.DOTALL | re.IGNORECASE)
                if pattern_match:
                    patterns_found.append({
                        "category": pattern_type,
                        "details": pattern_match.group(1).strip()
                    })
            
            return {
                "patterns_by_category": patterns_found,
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "raw_response": response,
                "parsing_error": str(e)
            }
    
    def _parse_dependencies_analysis(self, response: str) -> Dict[str, Any]:
        """Parse dependencies analysis response."""
        try:
            coupling_match = re.search(r'(?:Coupling|Dependencies)[:\s]+(.*?)(?=\n\d+\.|\n[A-Z]|\n\n|$)', 
                                     response, re.DOTALL | re.IGNORECASE)
            
            issues_match = re.search(r'(?:Issues?|Problems?|Circular)[:\s]+(.*?)(?=\n\d+\.|\n[A-Z]|\n\n|$)', 
                                   response, re.DOTALL | re.IGNORECASE)
            
            return {
                "coupling_analysis": coupling_match.group(1).strip() if coupling_match else "No coupling analysis",
                "dependency_issues": issues_match.group(1).strip() if issues_match else "No issues identified",
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "raw_response": response,
                "parsing_error": str(e)
            }
    
    def _parse_scalability_analysis(self, response: str) -> Dict[str, Any]:
        """Parse scalability analysis response."""
        try:
            bottlenecks_match = re.search(r'(?:Bottlenecks?|Performance)[:\s]+(.*?)(?=\n\d+\.|\n[A-Z]|\n\n|$)', 
                                        response, re.DOTALL | re.IGNORECASE)
            
            scaling_match = re.search(r'(?:Scaling|Scalability)[:\s]+(.*?)(?=\n\d+\.|\n[A-Z]|\n\n|$)', 
                                    response, re.DOTALL | re.IGNORECASE)
            
            return {
                "performance_bottlenecks": bottlenecks_match.group(1).strip() if bottlenecks_match else "No bottlenecks identified",
                "scaling_capabilities": scaling_match.group(1).strip() if scaling_match else "No scaling analysis",
                "raw_response": response
            }
            
        except Exception as e:
            return {
                "raw_response": response,
                "parsing_error": str(e)
            }
    
    def _generate_architecture_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate consolidated architecture recommendations."""
        recommendations = []
        
        for section_name, section_data in report.items():
            if isinstance(section_data, dict) and "improvement_recommendations" in section_data:
                recommendations.append(f"From {section_name}: {section_data['improvement_recommendations']}")
        
        return recommendations if recommendations else ["Complete architecture analysis to generate recommendations"]
    
    def display_architecture_analysis(self, analysis_result: Dict[str, Any]):
        """Display architecture analysis results in a formatted way."""
        if not analysis_result:
            console.print("No architecture analysis results to display", style="yellow")
            return
        
        console.print("\n[bold blue]Architecture Discovery Results[/bold blue]")
        
        if "focus_area" in analysis_result and analysis_result["focus_area"]:
            console.print(f"Focus Area: [cyan]{analysis_result['focus_area']}[/cyan]\n")
        
        if "overall_assessment" in analysis_result:
            console.print(Panel(
                analysis_result["overall_assessment"],
                title="[bold green]System Architecture Assessment[/bold green]",
                border_style="green"
            ))
        
        if "patterns_identified" in analysis_result:
            console.print(Panel(
                analysis_result["patterns_identified"],
                title="[bold cyan]Architectural Patterns[/bold cyan]",
                border_style="cyan"
            ))
    
    def display_comprehensive_report(self, report: Dict[str, Any]):
        """Display comprehensive architecture report."""
        if not report:
            console.print("No architecture report to display", style="yellow")
            return
        
        console.print("\n[bold blue]Comprehensive Architecture Discovery Report[/bold blue]\n")
        
        if report.get("system_overview"):
            console.print("[bold green]System Architecture Overview[/bold green]")
            self.display_architecture_analysis(report["system_overview"])
            console.print()
        
        if report.get("design_patterns"):
            console.print("[bold cyan]Design Patterns Analysis[/bold cyan]")
            patterns_data = report["design_patterns"]
            if "patterns_by_category" in patterns_data:
                for pattern_category in patterns_data["patterns_by_category"]:
                    console.print(Panel(
                        pattern_category["details"],
                        title=f"[bold]{pattern_category['category']} Patterns[/bold]",
                        border_style="cyan"
                    ))
            console.print()
        
        if report.get("dependencies"):
            console.print("[bold yellow]Dependencies Analysis[/bold yellow]")
            deps_data = report["dependencies"]
            if "coupling_analysis" in deps_data:
                console.print(Panel(
                    deps_data["coupling_analysis"],
                    title="[bold]Component Coupling[/bold]",
                    border_style="yellow"
                ))
            console.print()
        
        if report.get("scalability"):
            console.print("[bold magenta]Scalability Assessment[/bold magenta]")
            scale_data = report["scalability"]
            if "scaling_capabilities" in scale_data:
                console.print(Panel(
                    scale_data["scaling_capabilities"],
                    title="[bold]Scaling Capabilities[/bold]",
                    border_style="magenta"
                ))
            console.print()
        
        if report.get("recommendations"):
            console.print("[bold red]Consolidated Recommendations[/bold red]")
            for i, rec in enumerate(report["recommendations"], 1):
                console.print(f"{i}. {rec}") 