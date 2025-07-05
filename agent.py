import asyncio
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Set
from enum import Enum
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentState(Enum):
    """Enumeration of possible agent states"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class Message:
    """Message structure for agent communication"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    receiver_id: str = ""
    content: Any = None
    message_type: str = "general"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

@dataclass
class Task:
    """Task structure for agent task management"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    status: str = "pending"
    data: Dict[str, Any] = field(default_factory=dict)
    
class MessageBroker:
    """Simple message broker for agent communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, Set[str]] = {}  # message_type -> set of agent_ids
        self.agents: Dict[str, 'Agent'] = {}
        
    def register_agent(self, agent: 'Agent'):
        """Register an agent with the broker"""
        self.agents[agent.id] = agent
        
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the broker"""
        if agent_id in self.agents:
            del self.agents[agent_id]
        # Remove from all subscriptions
        for subscribers in self.subscribers.values():
            subscribers.discard(agent_id)
            
    def subscribe(self, agent_id: str, message_type: str):
        """Subscribe an agent to a message type"""
        if message_type not in self.subscribers:
            self.subscribers[message_type] = set()
        self.subscribers[message_type].add(agent_id)
        
    def unsubscribe(self, agent_id: str, message_type: str):
        """Unsubscribe an agent from a message type"""
        if message_type in self.subscribers:
            self.subscribers[message_type].discard(agent_id)
            
    async def send_message(self, message: Message):
        """Send a message to the specified receiver or broadcast to subscribers"""
        if message.receiver_id:
            # Direct message
            if message.receiver_id in self.agents:
                await self.agents[message.receiver_id].receive_message(message)
        else:
            # Broadcast to subscribers
            if message.message_type in self.subscribers:
                for agent_id in self.subscribers[message.message_type]:
                    if agent_id in self.agents and agent_id != message.sender_id:
                        await self.agents[agent_id].receive_message(message)

class Agent(ABC):
    """Base agent class for multi-agent systems"""
    
    def __init__(self, name: str, broker: MessageBroker, agent_type: str = "generic"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.agent_type = agent_type
        self.state = AgentState.IDLE
        self.broker = broker
        
        # Task management
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []
        
        # Message handling
        self.message_handlers: Dict[str, Callable] = {}
        self.message_queue: List[Message] = []
        
        # State and data
        self.data: Dict[str, Any] = {}
        self.capabilities: Set[str] = set()
        
        # Lifecycle
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
        # Register with broker
        self.broker.register_agent(self)
        
        # Setup default message handlers
        self._setup_default_handlers()
        
        logger.info(f"Agent {self.name} ({self.id}) initialized")
    
    def _setup_default_handlers(self):
        """Setup default message handlers"""
        self.register_message_handler("ping", self._handle_ping)
        self.register_message_handler("task_assignment", self._handle_task_assignment)
        self.register_message_handler("status_request", self._handle_status_request)
    
    @abstractmethod
    async def process_task(self, task: Task) -> Any:
        """Process a task - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def initialize(self):
        """Initialize the agent - must be implemented by subclasses"""
        pass
    
    async def start(self):
        """Start the agent"""
        self.state = AgentState.RUNNING
        await self.initialize()
        logger.info(f"Agent {self.name} started")
        
        # Start main processing loop
        asyncio.create_task(self._main_loop())
    
    async def stop(self):
        """Stop the agent"""
        self.state = AgentState.STOPPED
        self.broker.unregister_agent(self.id)
        logger.info(f"Agent {self.name} stopped")
    
    async def pause(self):
        """Pause the agent"""
        self.state = AgentState.PAUSED
        logger.info(f"Agent {self.name} paused")
    
    async def resume(self):
        """Resume the agent"""
        self.state = AgentState.RUNNING
        logger.info(f"Agent {self.name} resumed")
    
    async def _main_loop(self):
        """Main processing loop"""
        while self.state != AgentState.STOPPED:
            if self.state == AgentState.RUNNING:
                try:
                    # Process messages
                    await self._process_messages()
                    
                    # Process tasks
                    await self._process_tasks()
                    
                    # Update last activity
                    self.last_activity = datetime.now()
                    
                except Exception as e:
                    logger.error(f"Error in agent {self.name} main loop: {e}")
                    self.state = AgentState.ERROR
            
            await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
    
    async def _process_messages(self):
        """Process queued messages"""
        while self.message_queue:
            message = self.message_queue.pop(0)
            await self._handle_message(message)
    
    async def _process_tasks(self):
        """Process queued tasks"""
        while self.task_queue and self.state == AgentState.RUNNING:
            task = self.task_queue.pop(0)
            try:
                task.status = "running"
                result = await self.process_task(task)
                task.status = "completed"
                logger.info(f"Agent {self.name} completed task {task.name}")
            except Exception as e:
                task.status = "failed"
                logger.error(f"Agent {self.name} failed task {task.name}: {e}")
    
    async def receive_message(self, message: Message):
        """Receive a message from the broker"""
        self.message_queue.append(message)
        logger.debug(f"Agent {self.name} received message: {message.message_type}")
    
    async def _handle_message(self, message: Message):
        """Handle a received message"""
        handler = self.message_handlers.get(message.message_type)
        if handler:
            await handler(message)
        else:
            logger.warning(f"Agent {self.name} has no handler for message type: {message.message_type}")
    
    async def send_message(self, content: Any, message_type: str = "general", 
                          receiver_id: str = "", metadata: Dict[str, Any] = None):
        """Send a message via the broker"""
        message = Message(
            sender_id=self.id,
            receiver_id=receiver_id,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        await self.broker.send_message(message)
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a message handler"""
        self.message_handlers[message_type] = handler
    
    def subscribe_to_messages(self, message_type: str):
        """Subscribe to a message type"""
        self.broker.subscribe(self.id, message_type)
    
    def unsubscribe_from_messages(self, message_type: str):
        """Unsubscribe from a message type"""
        self.broker.unsubscribe(self.id, message_type)
    
    def add_task(self, task: Task):
        """Add a task to the task queue"""
        self.tasks[task.id] = task
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority, reverse=True)
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.agent_type,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'task_count': len(self.tasks),
            'queued_tasks': len(self.task_queue),
            'capabilities': list(self.capabilities),
            'data': self.data
        }
    
    # Default message handlers
    async def _handle_ping(self, message: Message):
        """Handle ping messages"""
        await self.send_message(
            content="pong",
            message_type="pong",
            receiver_id=message.sender_id
        )
    
    async def _handle_task_assignment(self, message: Message):
        """Handle task assignment messages"""
        task_data = message.content
        if isinstance(task_data, dict):
            task = Task(
                name=task_data.get('name', ''),
                description=task_data.get('description', ''),
                priority=task_data.get('priority', 0),
                data=task_data.get('data', {})
            )
            self.add_task(task)
            logger.info(f"Agent {self.name} received task assignment: {task.name}")
    
    async def _handle_status_request(self, message: Message):
        """Handle status request messages"""
        await self.send_message(
            content=self.get_status(),
            message_type="status_response",
            receiver_id=message.sender_id
        )

# Example concrete agent implementation
class WorkerAgent(Agent):
    """Example worker agent implementation"""
    
    def __init__(self, name: str, broker: MessageBroker):
        super().__init__(name, broker, "worker")
        self.capabilities.add("data_processing")
        self.capabilities.add("computation")
    
    async def initialize(self):
        """Initialize the worker agent"""
        self.subscribe_to_messages("work_request")
        self.register_message_handler("work_request", self._handle_work_request)
        logger.info(f"Worker agent {self.name} initialized")
    
    async def process_task(self, task: Task) -> Any:
        """Process a task"""
        logger.info(f"Worker {self.name} processing task: {task.name}")
        
        # Simulate some work
        await asyncio.sleep(1)
        
        # Return result
        return f"Task {task.name} completed by {self.name}"
    
    async def _handle_work_request(self, message: Message):
        """Handle work request messages"""
        work_data = message.content
        task = Task(
            name=f"Work from {message.sender_id}",
            description=str(work_data),
            priority=1,
            data={"work_data": work_data}
        )
        self.add_task(task)

# Example coordinator agent implementation
class CoordinatorAgent(Agent):
    """Example coordinator agent implementation"""
    
    def __init__(self, name: str, broker: MessageBroker):
        super().__init__(name, broker, "coordinator")
        self.capabilities.add("coordination")
        self.capabilities.add("task_distribution")
        self.worker_agents: Set[str] = set()
    
    async def initialize(self):
        """Initialize the coordinator agent"""
        self.subscribe_to_messages("agent_registration")
        self.register_message_handler("agent_registration", self._handle_agent_registration)
        logger.info(f"Coordinator agent {self.name} initialized")
    
    async def process_task(self, task: Task) -> Any:
        """Process a task by delegating to workers"""
        if self.worker_agents:
            # Send work to available workers
            for worker_id in self.worker_agents:
                await self.send_message(
                    content=task.data,
                    message_type="work_request",
                    receiver_id=worker_id
                )
        return f"Task {task.name} delegated to {len(self.worker_agents)} workers"
    
    async def _handle_agent_registration(self, message: Message):
        """Handle agent registration messages"""
        agent_info = message.content
        if agent_info.get('type') == 'worker':
            self.worker_agents.add(message.sender_id)
            logger.info(f"Coordinator {self.name} registered worker: {message.sender_id}") 