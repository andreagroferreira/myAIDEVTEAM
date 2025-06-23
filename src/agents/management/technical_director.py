"""
Technical Director Agent
Ensures architectural excellence and technical standards across all projects
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from src.agents.base_agent import BaseAgent, AgentConfig
from src.models import AgentRole, AgentTier, Task, TaskType
from src.config import get_logger
from crewai_tools import (
    FileReadTool,
    DirectoryReadTool,
    SerperDevTool,
)


class TechnicalDirector(BaseAgent):
    """Technical Director agent for strategic technical decisions"""
    
    def __init__(self):
        config = AgentConfig(
            identifier="technical_director",
            name="Technical Director",
            role=AgentRole.TECHNICAL_DIRECTOR,
            tier=AgentTier.MANAGEMENT,
            goal="Ensure architectural excellence and technical standards across all projects",
            backstory="""Senior architect with 15+ years experience in Laravel, Vue.js, and enterprise systems.
            Expert in microservices architecture, API design, and scalable system design.
            Known for making pragmatic technical decisions that balance innovation with stability.""",
            capabilities=[
                "architecture_review",
                "technical_decision_making",
                "cross_project_coordination",
                "standard_enforcement",
                "technology_evaluation",
                "risk_assessment",
                "team_mentoring"
            ],
            tools=[
                FileReadTool(),
                DirectoryReadTool(),
                SerperDevTool(),  # For researching best practices
            ],
            max_rpm=20,
            allow_delegation=True,
            can_manage_crew=True
        )
        super().__init__(config)
        
        # Technical Director specific attributes
        self.architecture_patterns = {
            "laravel": ["Repository Pattern", "Action Pattern", "Service Layer", "Domain Driven Design"],
            "vue": ["Composition API", "Pinia Store", "Component Patterns", "TypeScript"],
            "api": ["RESTful", "GraphQL", "JSON:API", "OpenAPI"],
            "database": ["Normalization", "Indexing", "Partitioning", "Replication"]
        }
        
        self.quality_standards = {
            "code_coverage": 80,
            "phpstan_level": 8,
            "complexity_threshold": 10,
            "response_time_ms": 200,
            "lighthouse_score": 90
        }
    
    async def initialize(self):
        """Initialize the Technical Director agent"""
        self.logger.info("Technical Director agent initializing...")
        
        # Load project configurations
        await self._load_project_configs()
        
        # Set up monitoring for architectural violations
        await self._setup_monitoring()
        
        self.logger.info("Technical Director agent ready")
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a task based on its type"""
        self.logger.info(f"Processing task: {task.title} (Type: {task.task_type.value})")
        
        result = {
            "task_id": str(task.id),
            "agent": self.config.identifier,
            "status": "completed",
            "decisions": [],
            "recommendations": [],
            "actions_taken": []
        }
        
        try:
            if task.task_type == TaskType.ANALYSIS:
                result.update(await self._perform_architecture_review(task))
            elif task.task_type == TaskType.REVIEW:
                result.update(await self._perform_code_review(task))
            elif task.task_type == TaskType.INTEGRATION:
                result.update(await self._coordinate_integration(task))
            elif task.task_type == TaskType.DEPLOYMENT:
                result.update(await self._approve_deployment(task))
            else:
                # Default technical decision making
                result.update(await self._make_technical_decision(task))
            
            result["timestamp"] = datetime.utcnow().isoformat()
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing task: {e}", exc_info=True)
            result["status"] = "failed"
            result["error"] = str(e)
            return result
    
    async def _perform_architecture_review(self, task: Task) -> Dict[str, Any]:
        """Perform architecture review"""
        self.logger.info(f"Performing architecture review for project: {task.project}")
        
        review_result = {
            "review_type": "architecture",
            "findings": [],
            "violations": [],
            "improvements": []
        }
        
        # Analyze project structure
        if task.metadata and "file_paths" in task.metadata:
            for file_path in task.metadata["file_paths"]:
                # Use tools to read and analyze files
                analysis = await self._analyze_file_architecture(file_path)
                review_result["findings"].extend(analysis["findings"])
                review_result["violations"].extend(analysis["violations"])
        
        # Check against architectural patterns
        project_type = task.metadata.get("project_type", "laravel")
        expected_patterns = self.architecture_patterns.get(project_type, [])
        
        for pattern in expected_patterns:
            if not await self._check_pattern_implementation(task.project, pattern):
                review_result["improvements"].append({
                    "pattern": pattern,
                    "priority": "high",
                    "description": f"Consider implementing {pattern} for better architecture"
                })
        
        # Generate recommendations
        review_result["recommendations"] = await self._generate_architecture_recommendations(
            review_result["findings"],
            review_result["violations"]
        )
        
        return review_result
    
    async def _perform_code_review(self, task: Task) -> Dict[str, Any]:
        """Perform high-level code review"""
        self.logger.info("Performing strategic code review")
        
        review_result = {
            "review_type": "code_quality",
            "quality_metrics": {},
            "concerns": [],
            "approvals": []
        }
        
        # Delegate detailed review to quality agents
        await self.collaborate_with("code_quality_lead", {
            "type": "review_request",
            "task_id": str(task.id),
            "focus_areas": ["architecture", "patterns", "standards"]
        })
        
        # Focus on high-level concerns
        if task.metadata.get("complexity_score", 0) > self.quality_standards["complexity_threshold"]:
            review_result["concerns"].append({
                "type": "complexity",
                "severity": "high",
                "suggestion": "Consider refactoring to reduce complexity"
            })
        
        return review_result
    
    async def _coordinate_integration(self, task: Task) -> Dict[str, Any]:
        """Coordinate cross-project integration"""
        self.logger.info("Coordinating cross-project integration")
        
        integration_plan = {
            "integration_type": task.metadata.get("integration_type", "api"),
            "projects_involved": task.metadata.get("projects", []),
            "steps": [],
            "risks": [],
            "timeline": {}
        }
        
        # Analyze integration requirements
        for project in integration_plan["projects_involved"]:
            compatibility = await self._check_project_compatibility(
                task.project, 
                project
            )
            
            if not compatibility["compatible"]:
                integration_plan["risks"].append({
                    "project": project,
                    "issue": compatibility["issue"],
                    "mitigation": compatibility["mitigation"]
                })
        
        # Create integration steps
        integration_plan["steps"] = await self._create_integration_plan(
            task.project,
            integration_plan["projects_involved"]
        )
        
        # Delegate to integration crew
        await self.report_to_crew("integration_crew", {
            "type": "integration_plan",
            "plan": integration_plan,
            "task_id": str(task.id)
        })
        
        return integration_plan
    
    async def _approve_deployment(self, task: Task) -> Dict[str, Any]:
        """Review and approve deployment"""
        self.logger.info("Reviewing deployment request")
        
        deployment_decision = {
            "approved": False,
            "conditions": [],
            "risks": [],
            "rollback_plan": {}
        }
        
        # Check quality gates
        quality_checks = await self._check_quality_gates(task.project)
        
        if all(check["passed"] for check in quality_checks):
            deployment_decision["approved"] = True
            deployment_decision["conditions"] = [
                "Monitor error rates for first 30 minutes",
                "Keep rollback ready",
                "Notify stakeholders"
            ]
        else:
            failed_checks = [c for c in quality_checks if not c["passed"]]
            deployment_decision["risks"] = [
                {
                    "check": check["name"],
                    "issue": check["reason"],
                    "severity": "high"
                }
                for check in failed_checks
            ]
        
        # Create rollback plan
        deployment_decision["rollback_plan"] = {
            "trigger_conditions": ["Error rate > 5%", "Response time > 500ms"],
            "steps": ["Revert deployment", "Clear caches", "Notify team"],
            "responsible": "deployment_manager"
        }
        
        return deployment_decision
    
    async def _make_technical_decision(self, task: Task) -> Dict[str, Any]:
        """Make general technical decisions"""
        self.logger.info("Making technical decision")
        
        decision = {
            "decision_type": "technical",
            "analysis": {},
            "recommendation": "",
            "rationale": [],
            "alternatives": []
        }
        
        # Analyze the technical question
        question = task.description or task.title
        
        # Use CrewAI agent to reason about the decision
        crewai_agent = self.get_crewai_agent()
        analysis = crewai_agent.execute(
            f"""Analyze this technical decision for a Laravel/Vue.js ecosystem:
            
            Question: {question}
            Context: {json.dumps(task.metadata or {})}
            
            Consider:
            1. Best practices for Laravel 11 and Vue 3
            2. Scalability and maintainability
            3. Team expertise and learning curve
            4. Integration with existing systems
            
            Provide a structured analysis with recommendation and rationale.
            """
        )
        
        # Parse and structure the response
        decision["analysis"] = {"raw_analysis": analysis}
        decision["recommendation"] = "Based on analysis - see details"
        decision["rationale"] = [
            "Aligns with current architecture",
            "Maintainable by the team",
            "Scalable for future needs"
        ]
        
        return decision
    
    async def handle_custom_message(self, message: Dict[str, Any]):
        """Handle Technical Director specific messages"""
        msg_type = message.get("type")
        
        if msg_type == "architecture_query":
            await self._handle_architecture_query(message)
        elif msg_type == "standard_violation":
            await self._handle_standard_violation(message)
        elif msg_type == "technology_proposal":
            await self._handle_technology_proposal(message)
    
    # Helper methods
    
    async def _load_project_configs(self):
        """Load project configurations"""
        # TODO: Load from YAML configs
        pass
    
    async def _setup_monitoring(self):
        """Set up architectural monitoring"""
        # TODO: Set up monitoring for violations
        pass
    
    async def _analyze_file_architecture(self, file_path: str) -> Dict[str, Any]:
        """Analyze file for architectural patterns"""
        return {
            "findings": [],
            "violations": []
        }
    
    async def _check_pattern_implementation(self, project: str, pattern: str) -> bool:
        """Check if a pattern is properly implemented"""
        # TODO: Implement pattern checking
        return True
    
    async def _generate_architecture_recommendations(
        self, 
        findings: List[Dict], 
        violations: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate architecture recommendations"""
        recommendations = []
        
        # Generate recommendations based on findings
        for violation in violations:
            recommendations.append({
                "type": "fix_violation",
                "priority": "high",
                "description": f"Fix: {violation}",
                "effort": "medium"
            })
        
        return recommendations
    
    async def _check_project_compatibility(
        self, 
        source_project: str, 
        target_project: str
    ) -> Dict[str, Any]:
        """Check compatibility between projects"""
        return {
            "compatible": True,
            "issue": None,
            "mitigation": None
        }
    
    async def _create_integration_plan(
        self, 
        source_project: str, 
        target_projects: List[str]
    ) -> List[Dict[str, Any]]:
        """Create integration plan steps"""
        steps = [
            {
                "order": 1,
                "action": "Analyze API contracts",
                "responsible": "api_designer",
                "duration": "2 hours"
            },
            {
                "order": 2,
                "action": "Create integration tests",
                "responsible": "test_runner",
                "duration": "4 hours"
            },
            {
                "order": 3,
                "action": "Implement integration layer",
                "responsible": "module_builder",
                "duration": "8 hours"
            },
            {
                "order": 4,
                "action": "Deploy and monitor",
                "responsible": "deployment_manager",
                "duration": "1 hour"
            }
        ]
        return steps
    
    async def _check_quality_gates(self, project: str) -> List[Dict[str, Any]]:
        """Check quality gates for deployment"""
        # TODO: Implement actual quality checks
        return [
            {"name": "Test Coverage", "passed": True, "value": 85, "threshold": 80},
            {"name": "PHPStan Level", "passed": True, "value": 8, "threshold": 8},
            {"name": "Performance", "passed": True, "value": 150, "threshold": 200}
        ]
    
    async def _handle_architecture_query(self, message: Dict[str, Any]):
        """Handle architecture queries from other agents"""
        query = message.get("query", "")
        response = {
            "type": "architecture_response",
            "query": query,
            "guidance": "Architecture guidance here",
            "examples": [],
            "references": []
        }
        
        # Send response back
        await self.collaborate_with(
            message.get("from", "unknown"),
            response
        )
    
    async def _handle_standard_violation(self, message: Dict[str, Any]):
        """Handle reported standard violations"""
        violation = message.get("violation", {})
        
        self.logger.warning(
            f"Standard violation reported: {violation.get('type')} "
            f"in project {violation.get('project')}"
        )
        
        # Create task to address violation
        await self._publish_event("create_task", {
            "title": f"Fix standard violation: {violation.get('type')}",
            "type": TaskType.BUG_FIX.value,
            "priority": "high",
            "project": violation.get("project"),
            "assigned_to": "quality_assurance_crew"
        })
    
    async def _handle_technology_proposal(self, message: Dict[str, Any]):
        """Evaluate new technology proposals"""
        proposal = message.get("proposal", {})
        
        # Evaluate proposal
        evaluation = {
            "technology": proposal.get("name"),
            "approved": False,
            "reasons": [],
            "conditions": [],
            "pilot_project": None
        }
        
        # TODO: Implement evaluation logic
        
        # Send evaluation result
        await self._publish_event("technology_evaluation", evaluation)