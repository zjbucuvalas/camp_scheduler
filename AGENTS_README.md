# Multi-Agent System

A flexible and extensible Python multi-agent system framework with asynchronous communication, task management, and coordination capabilities.

## Architecture Overview

The system consists of several key components:

### Core Components

1. **Agent (Abstract Base Class)**: The foundation for all agents with common functionality
2. **MessageBroker**: Handles message routing and communication between agents
3. **Message**: Data structure for inter-agent communication
4. **Task**: Data structure for task management
5. **AgentState**: Enumeration of possible agent states

### Key Features

- **Asynchronous Processing**: All agents run concurrently using asyncio
- **Message-Based Communication**: Agents communicate through a publish/subscribe pattern
- **Task Management**: Built-in task queuing and processing with priority support
- **Lifecycle Management**: Start, stop, pause, and resume agents
- **State Monitoring**: Real-time status tracking for all agents
- **Extensible Design**: Easy to create custom agent types

## Usage

### Basic Setup

```python
import asyncio
from agent import MessageBroker, WorkerAgent, CoordinatorAgent, Task

# Create a message broker
broker = MessageBroker()

# Create agents
coordinator = CoordinatorAgent("Coordinator-1", broker)
worker = WorkerAgent("Worker-1", broker)

# Start agents
await coordinator.start()
await worker.start()
```

### Creating Custom Agents

```python
from agent import Agent, Task

class CustomAgent(Agent):
    def __init__(self, name: str, broker: MessageBroker):
        super().__init__(name, broker, "custom")
        self.capabilities.add("custom_processing")
    
    async def initialize(self):
        """Initialize the agent"""
        self.subscribe_to_messages("custom_message")
        self.register_message_handler("custom_message", self._handle_custom_message)
    
    async def process_task(self, task: Task) -> Any:
        """Process a task"""
        # Your custom task processing logic here
        return f"Processed {task.name}"
    
    async def _handle_custom_message(self, message: Message):
        """Handle custom message types"""
        # Your custom message handling logic here
        pass
```

### Communication Patterns

#### Direct Messaging
```python
# Send a direct message to a specific agent
await agent1.send_message(
    content="Hello!",
    message_type="greeting",
    receiver_id=agent2.id
)
```

#### Publish/Subscribe
```python
# Subscribe to a message type
agent.subscribe_to_messages("announcements")

# Broadcast to all subscribers
await agent.send_message(
    content="System update",
    message_type="announcements"
)
```

### Task Management

```python
# Create a task
task = Task(
    name="Process Data",
    description="Process the incoming data",
    priority=3,
    data={"input": "some_data"}
)

# Add task to an agent
agent.add_task(task)
```

## Built-in Agent Types

### WorkerAgent
- Processes tasks assigned to it
- Subscribes to "work_request" messages
- Capabilities: "data_processing", "computation"

### CoordinatorAgent
- Manages and delegates tasks to worker agents
- Handles agent registration
- Capabilities: "coordination", "task_distribution"

## Agent States

- **IDLE**: Agent is initialized but not started
- **RUNNING**: Agent is actively processing tasks and messages
- **PAUSED**: Agent is temporarily stopped
- **STOPPED**: Agent has been shut down
- **ERROR**: Agent encountered an error

## Message Types

### Built-in Message Types

- `ping`: Health check message
- `pong`: Response to ping
- `task_assignment`: Assign a task to an agent
- `status_request`: Request agent status
- `status_response`: Response with agent status
- `work_request`: Request work from a worker (WorkerAgent)
- `agent_registration`: Register agent with coordinator

## Running the Demo

```bash
python demo.py
```

This will demonstrate:
- Agent creation and initialization
- Inter-agent communication
- Task distribution and processing
- Status monitoring
- Graceful shutdown

## Extending the System

### Adding New Message Types

1. Define your message type string
2. Register a handler with `register_message_handler()`
3. Subscribe to the message type if needed

### Creating Specialized Agents

1. Inherit from the `Agent` base class
2. Implement `initialize()` and `process_task()` methods
3. Add custom capabilities and message handlers
4. Register with the message broker

### Integration with External Systems

The system can be extended to integrate with:
- Redis for distributed messaging
- Database systems for persistent storage
- Web APIs for external communication
- Monitoring systems for observability

## Best Practices

1. **Error Handling**: Always handle exceptions in your custom agents
2. **Resource Management**: Properly stop agents when done
3. **Message Design**: Use structured message content for complex data
4. **Priority Management**: Use task priorities for important work
5. **Monitoring**: Regularly check agent status and health

## Future Enhancements

Potential areas for extension:
- Distributed agents across multiple processes/machines
- Advanced scheduling and load balancing
- Persistent task storage
- Web-based monitoring dashboard
- Integration with ML/AI frameworks
- Advanced security and authentication 