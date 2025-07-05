"""
AI Agent Extension for Multi-Agent System
Handles system prompts, task prompts, and LLM integration
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from agent import Agent, MessageBroker, Task, Message
import logging
import uuid

logger = logging.getLogger(__name__)

@dataclass
class Prompt:
    """Prompt structure for AI agents"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "system"  # system, user, assistant, task
    content: str = ""
    role: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    variables: Dict[str, Any] = field(default_factory=dict)
    
    def render(self) -> str:
        """Render the prompt with variables"""
        content = self.content
        for key, value in self.variables.items():
            content = content.replace(f"{{{key}}}", str(value))
        return content

@dataclass
class AIContext:
    """Context for AI agent conversations"""
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    system_prompt: Optional[Prompt] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    context_window: int = 4000
    max_tokens: int = 2000
    temperature: float = 0.7
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        
        # Trim history if it exceeds context window
        if len(self.conversation_history) > self.context_window:
            self.conversation_history = self.conversation_history[-self.context_window:]
    
    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        """Get formatted messages for LLM"""
        messages = []
        
        # Add system prompt if exists
        if self.system_prompt:
            messages.append({
                "role": "system",
                "content": self.system_prompt.render()
            })
        
        # Add conversation history
        for msg in self.conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return messages

class PromptTemplate:
    """Template for generating prompts"""
    
    def __init__(self, name: str, template: str, variables: List[str] = None):
        self.name = name
        self.template = template
        self.variables = variables or []
        self.created_at = datetime.now()
    
    def create_prompt(self, prompt_type: str = "system", **kwargs) -> Prompt:
        """Create a prompt from this template"""
        return Prompt(
            type=prompt_type,
            content=self.template,
            variables=kwargs,
            metadata={"template": self.name}
        )

class AIAgent(Agent):
    """AI-powered agent with LLM integration and prompt handling"""
    
    def __init__(self, name: str, broker: MessageBroker, system_prompt: str = None):
        super().__init__(name, broker, "ai_agent")
        
        # AI-specific capabilities
        self.capabilities.update({
            "llm_processing", 
            "prompt_handling", 
            "conversation_management",
            "context_awareness"
        })
        
        # Prompt and context management
        self.system_prompt = None
        if system_prompt:
            self.system_prompt = Prompt(
                type="system",
                content=system_prompt,
                role="system"
            )
        
        self.contexts: Dict[str, AIContext] = {}
        self.prompt_templates: Dict[str, PromptTemplate] = {}
        
        # LLM configuration
        self.llm_config = {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
        # Task prompts for different task types
        self.task_prompts: Dict[str, PromptTemplate] = {}
        
        # Setup default prompt templates
        self._setup_default_prompts()
        
        logger.info(f"AI Agent {self.name} initialized with system prompt: {bool(system_prompt)}")
    
    def _setup_default_prompts(self):
        """Setup default prompt templates"""
        
        # Default task processing prompt
        self.add_prompt_template(
            "task_processing",
            """You are an AI agent tasked with processing the following task:

Task Name: {task_name}
Task Description: {task_description}
Task Data: {task_data}
Priority: {priority}

Please process this task and provide a detailed response. Consider the context and requirements carefully."""
        )
        
        # Default analysis prompt
        self.add_prompt_template(
            "analysis",
            """Analyze the following data and provide insights:

Data: {data}
Analysis Type: {analysis_type}
Context: {context}

Provide a comprehensive analysis with key findings and recommendations."""
        )
        
        # Default collaboration prompt
        self.add_prompt_template(
            "collaboration",
            """You are collaborating with other AI agents on a shared task:

Your Role: {role}
Task Context: {context}
Other Agents: {other_agents}
Shared Goal: {goal}

Coordinate with other agents and contribute to the shared objective."""
        )
    
    async def initialize(self):
        """Initialize the AI agent"""
        # Subscribe to AI-specific message types
        self.subscribe_to_messages("ai_request")
        self.subscribe_to_messages("prompt_update")
        self.subscribe_to_messages("context_share")
        
        # Register AI-specific message handlers
        self.register_message_handler("ai_request", self._handle_ai_request)
        self.register_message_handler("prompt_update", self._handle_prompt_update)
        self.register_message_handler("context_share", self._handle_context_share)
        
        logger.info(f"AI Agent {self.name} initialized and ready for AI tasks")
    
    async def process_task(self, task: Task) -> Any:
        """Process a task using AI capabilities"""
        logger.info(f"AI Agent {self.name} processing task: {task.name}")
        
        # Create context for this task
        context = self.create_context(f"task_{task.id}")
        
        # Determine appropriate prompt template
        prompt_template_name = task.data.get("prompt_template", "task_processing")
        
        if prompt_template_name in self.task_prompts:
            prompt_template = self.task_prompts[prompt_template_name]
        else:
            prompt_template = self.prompt_templates.get(prompt_template_name)
        
        if prompt_template:
            # Create task prompt
            task_prompt = prompt_template.create_prompt(
                prompt_type="user",
                task_name=task.name,
                task_description=task.description,
                task_data=json.dumps(task.data, indent=2),
                priority=task.priority
            )
            
            # Add to context
            context.add_message("user", task_prompt.render())
            
            # Process with LLM
            result = await self._process_with_llm(context)
            
            # Add result to context
            context.add_message("assistant", result)
            
            return result
        else:
            # Fallback to basic processing
            return f"Processed task {task.name} - no specific prompt template found"
    
    async def _process_with_llm(self, context: AIContext) -> str:
        """Process context with LLM (placeholder for actual LLM integration)"""
        # This is a placeholder - in a real implementation, you would:
        # 1. Call your LLM API (OpenAI, Anthropic, etc.)
        # 2. Handle the response
        # 3. Manage rate limiting and errors
        
        messages = context.get_messages_for_llm()
        
        # Simulate LLM processing
        await asyncio.sleep(0.5)  # Simulate API call delay
        
        # Mock response based on the last message
        last_message = messages[-1]["content"] if messages else ""
        
        mock_response = f"AI Agent {self.name} processed the request: {last_message[:100]}..."
        
        logger.info(f"LLM processing completed for context {context.conversation_id}")
        return mock_response
    
    def create_context(self, conversation_id: str = None) -> AIContext:
        """Create a new AI context"""
        if conversation_id is None:
            conversation_id = f"context_{len(self.contexts)}"
        
        context = AIContext(
            conversation_id=conversation_id,
            system_prompt=self.system_prompt
        )
        
        self.contexts[conversation_id] = context
        return context
    
    def get_context(self, conversation_id: str) -> Optional[AIContext]:
        """Get an existing context"""
        return self.contexts.get(conversation_id)
    
    def add_prompt_template(self, name: str, template: str, variables: List[str] = None):
        """Add a prompt template"""
        self.prompt_templates[name] = PromptTemplate(name, template, variables)
        logger.info(f"Added prompt template: {name}")
    
    def add_task_prompt(self, task_type: str, template: str, variables: List[str] = None):
        """Add a task-specific prompt template"""
        self.task_prompts[task_type] = PromptTemplate(f"task_{task_type}", template, variables)
        logger.info(f"Added task prompt for type: {task_type}")
    
    def update_system_prompt(self, new_prompt: str):
        """Update the system prompt"""
        self.system_prompt = Prompt(
            type="system",
            content=new_prompt,
            role="system"
        )
        logger.info(f"Updated system prompt for agent {self.name}")
    
    def update_llm_config(self, **kwargs):
        """Update LLM configuration"""
        self.llm_config.update(kwargs)
        logger.info(f"Updated LLM config for agent {self.name}: {kwargs}")
    
    # Message handlers
    async def _handle_ai_request(self, message: Message):
        """Handle AI-specific requests"""
        request_data = message.content
        
        if isinstance(request_data, dict):
            request_type = request_data.get("type", "general")
            
            if request_type == "prompt_completion":
                # Handle prompt completion request
                prompt_text = request_data.get("prompt", "")
                context_id = request_data.get("context_id", "default")
                
                context = self.get_context(context_id) or self.create_context(context_id)
                context.add_message("user", prompt_text)
                
                result = await self._process_with_llm(context)
                
                # Send response back
                await self.send_message(
                    content={"result": result, "context_id": context_id},
                    message_type="ai_response",
                    receiver_id=message.sender_id
                )
    
    async def _handle_prompt_update(self, message: Message):
        """Handle prompt update messages"""
        update_data = message.content
        
        if isinstance(update_data, dict):
            if "system_prompt" in update_data:
                self.update_system_prompt(update_data["system_prompt"])
            
            if "llm_config" in update_data:
                self.update_llm_config(**update_data["llm_config"])
    
    async def _handle_context_share(self, message: Message):
        """Handle context sharing between agents"""
        context_data = message.content
        
        if isinstance(context_data, dict):
            shared_context_id = context_data.get("context_id")
            shared_messages = context_data.get("messages", [])
            
            # Create or update context with shared information
            context = self.get_context(shared_context_id) or self.create_context(shared_context_id)
            
            for msg in shared_messages:
                context.add_message(msg["role"], msg["content"], msg.get("metadata"))
            
            logger.info(f"Received shared context from {message.sender_id}")
    
    async def share_context(self, context_id: str, target_agent_id: str):
        """Share context with another agent"""
        context = self.get_context(context_id)
        
        if context:
            await self.send_message(
                content={
                    "context_id": context_id,
                    "messages": context.conversation_history
                },
                message_type="context_share",
                receiver_id=target_agent_id
            )
            logger.info(f"Shared context {context_id} with agent {target_agent_id}")
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get AI-specific status information"""
        base_status = self.get_status()
        
        ai_status = {
            "contexts": len(self.contexts),
            "prompt_templates": len(self.prompt_templates),
            "task_prompts": len(self.task_prompts),
            "system_prompt": bool(self.system_prompt),
            "llm_config": str(self.llm_config) if hasattr(self, 'llm_config') else None
        }
        
        base_status.update(ai_status)
        return base_status

# Specialized AI Agent Types
class AnalystAgent(AIAgent):
    """AI agent specialized for data analysis tasks"""
    
    def __init__(self, name: str, broker: MessageBroker):
        system_prompt = """You are an expert data analyst AI agent. Your role is to:
1. Analyze complex datasets and identify patterns
2. Generate insights and recommendations
3. Create clear, actionable reports
4. Collaborate with other agents on analytical tasks

Always provide evidence-based analysis and clearly explain your methodology."""
        
        super().__init__(name, broker, system_prompt)
        self.capabilities.add("data_analysis")
        
        # Add analysis-specific prompt templates
        self.add_task_prompt(
            "trend_analysis",
            """Perform trend analysis on the following data:

Data: {data}
Time Period: {time_period}
Metrics: {metrics}

Identify key trends, patterns, and anomalies. Provide insights and predictions."""
        )

class ResearchAgent(AIAgent):
    """AI agent specialized for research tasks"""
    
    def __init__(self, name: str, broker: MessageBroker):
        system_prompt = """You are a research specialist AI agent. Your role is to:
1. Conduct thorough research on given topics
2. Synthesize information from multiple sources
3. Generate comprehensive research reports
4. Fact-check and verify information

Always cite sources and provide well-structured, evidence-based research."""
        
        super().__init__(name, broker, system_prompt)
        self.capabilities.add("research")
        
        # Add research-specific prompt templates
        self.add_task_prompt(
            "literature_review",
            """Conduct a literature review on the following topic:

Topic: {topic}
Scope: {scope}
Key Questions: {questions}

Provide a comprehensive review with key findings, gaps, and recommendations."""
        )

class CoordinatorAIAgent(AIAgent):
    """AI agent specialized for coordinating other agents"""
    
    def __init__(self, name: str, broker: MessageBroker):
        system_prompt = """You are a coordinator AI agent. Your role is to:
1. Orchestrate tasks across multiple AI agents
2. Manage workflow and dependencies
3. Ensure quality and consistency
4. Optimize resource allocation

Always consider the capabilities of other agents and coordinate efficiently."""
        
        super().__init__(name, broker, system_prompt)
        self.capabilities.update({"coordination", "workflow_management"})
        
        # Track managed agents
        self.managed_agents: Dict[str, Dict[str, Any]] = {}
        
        # Add coordination-specific prompt templates
        self.add_task_prompt(
            "task_delegation",
            """Delegate the following task to appropriate agents:

Task: {task_description}
Available Agents: {available_agents}
Requirements: {requirements}
Deadline: {deadline}

Determine the best agent allocation and coordination strategy."""
        ) 