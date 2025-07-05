# Multi-Agent System with AI/LLM Integration

A comprehensive Python multi-agent system framework with built-in AI capabilities, system prompts, task prompts, and real LLM integration.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Basic demo
python3 demo.py

# AI agents demo
python3 ai_demo.py

# Production example (requires API keys)
python3 llm_integration.py
```

## 🏗️ Architecture

### Core Components

1. **Agent System** (`agent.py`)
   - Base `Agent` class with lifecycle management
   - `MessageBroker` for inter-agent communication
   - `Task` and `Message` structures
   - Built-in agent types: `WorkerAgent`, `CoordinatorAgent`

2. **AI Agent System** (`ai_agent.py`)
   - `AIAgent` with prompt handling capabilities
   - `Prompt` and `PromptTemplate` classes
   - `AIContext` for conversation management
   - Specialized agents: `AnalystAgent`, `ResearchAgent`, `CoordinatorAIAgent`

3. **LLM Integration** (`llm_integration.py`)
   - `ProductionAIAgent` with real LLM APIs
   - Support for OpenAI, Anthropic, Azure OpenAI
   - Rate limiting, error handling, retries
   - Production-ready configuration

## 🤖 Agent Types

### Basic Agents
- **Agent**: Abstract base class with core functionality
- **WorkerAgent**: Processes tasks and responds to work requests
- **CoordinatorAgent**: Manages and delegates tasks to workers

### AI Agents
- **AIAgent**: Base AI agent with prompt and context management
- **AnalystAgent**: Specialized for data analysis tasks
- **ResearchAgent**: Focused on research and information gathering
- **CoordinatorAIAgent**: AI-powered task coordination

### Production Agents
- **ProductionAIAgent**: Real LLM integration with OpenAI/Anthropic APIs

## 🎯 Key Features

### ✅ System Prompts
```python
# Create AI agent with system prompt
agent = AIAgent(
    "Assistant", 
    broker,
    system_prompt="You are a helpful AI assistant specialized in data analysis."
)
```

### ✅ Task Prompts
```python
# Add task-specific prompt templates
agent.add_task_prompt(
    "analysis",
    """Analyze the following data: {data}
    
    Provide insights on: {focus_areas}
    Format: {output_format}"""
)
```

### ✅ Dynamic Prompt Updates
```python
# Update system prompt at runtime
agent.update_system_prompt("New role: You are now a creative writer.")

# Update LLM configuration
agent.update_llm_config(temperature=0.9, max_tokens=1000)
```

### ✅ Context Management
```python
# Create and manage conversation contexts
context = agent.create_context("conversation_1")
context.add_message("user", "What is machine learning?")
context.add_message("assistant", "Machine learning is...")

# Share context between agents
await agent.share_context("conversation_1", other_agent.id)
```

### ✅ LLM Integration
```python
# Production agent with OpenAI
config = create_openai_config(model="gpt-4", temperature=0.7)
agent = ProductionAIAgent("AI-Assistant", broker, config, system_prompt)

# Production agent with Anthropic
config = create_anthropic_config(model="claude-3-sonnet-20240229")
agent = ProductionAIAgent("AI-Researcher", broker, config, system_prompt)
```

## 📋 Usage Examples

### Basic Multi-Agent System

```python
import asyncio
from agent import MessageBroker, WorkerAgent, CoordinatorAgent, Task

async def main():
    # Create broker and agents
    broker = MessageBroker()
    coordinator = CoordinatorAgent("Coordinator", broker)
    worker = WorkerAgent("Worker-1", broker)
    
    # Start agents
    await coordinator.start()
    await worker.start()
    
    # Create and assign task
    task = Task(
        name="Process Data",
        description="Process customer data",
        data={"dataset": "customers.csv"}
    )
    
    coordinator.add_task(task)
    await asyncio.sleep(2)  # Wait for processing
    
    # Stop agents
    await coordinator.stop()
    await worker.stop()

asyncio.run(main())
```

### AI Agent with Prompts

```python
from ai_agent import AIAgent, AnalystAgent
from agent import MessageBroker, Task

async def ai_example():
    broker = MessageBroker()
    
    # Create AI agent with system prompt
    analyst = AnalystAgent("Data-Analyst", broker)
    await analyst.start()
    
    # Create task with specific prompt template
    task = Task(
        name="Sales Analysis",
        description="Analyze quarterly sales data",
        data={
            "prompt_template": "trend_analysis",
            "data": "Q1: $100k, Q2: $120k, Q3: $110k, Q4: $140k",
            "time_period": "2024",
            "metrics": "revenue, growth"
        }
    )
    
    analyst.add_task(task)
    await asyncio.sleep(3)
    await analyst.stop()

asyncio.run(ai_example())
```

### Production LLM Integration

```python
from llm_integration import ProductionAIAgent, create_openai_config
from agent import MessageBroker

async def production_example():
    broker = MessageBroker()
    
    # Configure OpenAI
    config = create_openai_config(
        api_key="your-openai-key",
        model="gpt-4",
        temperature=0.7
    )
    
    # Create production agent
    agent = ProductionAIAgent(
        "Production-AI",
        broker,
        config,
        system_prompt="You are a professional business analyst."
    )
    
    await agent.start()
    
    # Process task with real LLM
    task = Task(
        name="Market Research",
        description="Research AI market trends",
        data={"market": "AI", "focus": "2024 trends"}
    )
    
    agent.add_task(task)
    await asyncio.sleep(5)
    
    # Check status
    status = agent.get_production_status()
    print(f"Requests: {status['request_count']}")
    print(f"Provider: {status['llm_provider']}")
    
    await agent.stop()

asyncio.run(production_example())
```

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-key"

# Anthropic
export ANTHROPIC_API_KEY="your-anthropic-key"

# Azure OpenAI
export AZURE_OPENAI_API_KEY="your-azure-key"
export AZURE_OPENAI_ENDPOINT="your-endpoint"
```

### Agent Configuration

```python
# Basic agent configuration
agent = Agent(name="MyAgent", broker=broker, agent_type="custom")

# AI agent configuration
ai_agent = AIAgent(
    name="AI-Assistant",
    broker=broker,
    system_prompt="Your role definition here"
)

# Production agent configuration
llm_config = LLMConfig(
    provider=LLMProvider.OPENAI,
    api_key="your-key",
    model="gpt-4",
    temperature=0.7,
    max_tokens=2000,
    timeout=30.0
)
```

## 📊 Message Types

### Built-in Messages
- `ping` / `pong`: Health checks
- `task_assignment`: Assign tasks to agents
- `status_request` / `status_response`: Status monitoring
- `work_request`: Request work from workers
- `agent_registration`: Register with coordinators

### AI-Specific Messages
- `ai_request`: AI-specific requests
- `prompt_update`: Update prompts/configuration
- `context_share`: Share conversation context

## 🛠️ Extending the System

### Custom Agent Types

```python
from agent import Agent, Task

class CustomAgent(Agent):
    def __init__(self, name: str, broker: MessageBroker):
        super().__init__(name, broker, "custom")
        self.capabilities.add("custom_processing")
    
    async def initialize(self):
        self.subscribe_to_messages("custom_message")
        self.register_message_handler("custom_message", self._handle_custom)
    
    async def process_task(self, task: Task) -> Any:
        # Your custom logic here
        return f"Processed {task.name}"
    
    async def _handle_custom(self, message: Message):
        # Handle custom messages
        pass
```

### Custom Prompt Templates

```python
# Add custom prompt templates
agent.add_prompt_template(
    "custom_analysis",
    """
    Task: {task_description}
    Data: {input_data}
    Requirements: {requirements}
    
    Please provide a {output_type} analysis focusing on {key_aspects}.
    """
)

# Use in tasks
task = Task(
    name="Custom Analysis",
    data={
        "prompt_template": "custom_analysis",
        "task_description": "Market analysis",
        "input_data": "market_data.json",
        "requirements": "trends and predictions",
        "output_type": "comprehensive",
        "key_aspects": "growth opportunities"
    }
)
```

## 🚀 Production Deployment

### Docker Support

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "your_main_script.py"]
```

### Monitoring and Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Monitor agent status
status = agent.get_production_status()
print(f"Error Rate: {status['error_rate']}%")
print(f"Request Count: {status['request_count']}")
```

### Scaling Considerations

1. **Horizontal Scaling**: Run multiple agent instances
2. **Load Balancing**: Use coordinators to distribute work
3. **Rate Limiting**: Built-in rate limiting for LLM APIs
4. **Error Handling**: Automatic retries and fallbacks
5. **Monitoring**: Comprehensive status and metrics

## 🔒 Security

- API keys via environment variables
- Rate limiting to prevent abuse
- Input validation and sanitization
- Secure message passing between agents
- Audit logging for all operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📚 Examples

Check out the demo files:
- `demo.py` - Basic multi-agent system
- `ai_demo.py` - AI agents with prompts
- `llm_integration.py` - Production LLM integration

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure environment variables are set
2. **Rate Limiting**: Adjust `rate_limit_delay` in LLM config
3. **Memory Usage**: Monitor context sizes and trim history
4. **Network Issues**: Check timeouts and retry settings

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance

- Async processing for high concurrency
- Built-in rate limiting and retries
- Efficient message passing
- Context window management
- Resource cleanup on shutdown

## 🛡️ Best Practices

1. **Error Handling**: Always handle exceptions gracefully
2. **Resource Management**: Stop agents properly
3. **API Limits**: Respect rate limits and quotas
4. **Context Size**: Monitor and trim conversation history
5. **Testing**: Test with mock LLMs before production
6. **Monitoring**: Track metrics and performance
7. **Security**: Protect API keys and sensitive data

---

## 🎉 Ready to Build?

You now have a complete multi-agent system that handles:
- ✅ **System prompts** for agent personalities
- ✅ **Task prompts** for specific operations
- ✅ **Real LLM integration** with OpenAI/Anthropic
- ✅ **Production-ready** deployment
- ✅ **Extensible architecture** for custom agents

Start building your multi-agent AI system today! 