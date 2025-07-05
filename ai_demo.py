"""
Demo script showing AI agents with system prompts and task prompts
"""

import asyncio
import logging
from agent import MessageBroker, Task
from ai_agent import AIAgent, AnalystAgent, ResearchAgent, CoordinatorAIAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    """Main demo function for AI agents"""
    print("🧠 Starting AI Multi-Agent System Demo")
    print("=" * 50)
    
    # Create a message broker
    broker = MessageBroker()
    
    # Create AI agents with different system prompts
    coordinator = CoordinatorAIAgent("AI-Coordinator", broker)
    
    analyst = AnalystAgent("Data-Analyst", broker)
    
    researcher = ResearchAgent("Research-Agent", broker)
    
    # Create a custom AI agent with specific system prompt
    custom_agent = AIAgent(
        "Custom-AI", 
        broker,
        system_prompt="""You are a creative AI agent specialized in content generation. 
        Your role is to create engaging, informative content while maintaining accuracy and creativity.
        Always provide well-structured responses with clear explanations."""
    )
    
    # Start all agents
    await coordinator.start()
    await analyst.start()
    await researcher.start()
    await custom_agent.start()
    
    # Give agents time to initialize
    await asyncio.sleep(1)
    
    print("\n🤖 AI Agent Status:")
    print("-" * 35)
    for agent in [coordinator, analyst, researcher, custom_agent]:
        status = agent.get_ai_status()
        print(f"Agent: {status['name']}")
        print(f"  - Type: {status['type']}")
        print(f"  - System Prompt: {status['system_prompt']}")
        print(f"  - Prompt Templates: {status['prompt_templates']}")
        print(f"  - Task Prompts: {status['task_prompts']}")
        print(f"  - LLM Model: {status['llm_config']['model']}")
        print()
    
    print("\n📝 Testing System Prompts:")
    print("-" * 30)
    
    # Test system prompt handling
    simple_task = Task(
        name="Simple Analysis",
        description="Analyze basic data patterns",
        data={"data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "type": "numeric"}
    )
    
    print("Sending analysis task to Data-Analyst...")
    analyst.add_task(simple_task)
    
    # Wait for processing
    await asyncio.sleep(2)
    
    print("\n🎯 Testing Task-Specific Prompts:")
    print("-" * 35)
    
    # Test task-specific prompts
    trend_analysis_task = Task(
        name="Trend Analysis",
        description="Perform trend analysis on sales data",
        data={
            "prompt_template": "trend_analysis",
            "data": "Sales data: Q1: 100k, Q2: 120k, Q3: 110k, Q4: 140k",
            "time_period": "2024",
            "metrics": "revenue, growth rate"
        }
    )
    
    print("Sending trend analysis task to Data-Analyst...")
    analyst.add_task(trend_analysis_task)
    
    # Test research task
    literature_review_task = Task(
        name="Literature Review",
        description="Conduct literature review on AI ethics",
        data={
            "prompt_template": "literature_review",
            "topic": "AI Ethics in Healthcare",
            "scope": "2020-2024",
            "questions": "What are the main ethical concerns? How are they being addressed?"
        }
    )
    
    print("Sending literature review task to Research-Agent...")
    researcher.add_task(literature_review_task)
    
    # Wait for processing
    await asyncio.sleep(3)
    
    print("\n🔄 Testing Prompt Updates:")
    print("-" * 28)
    
    # Test dynamic prompt updates
    print("Updating system prompt for Custom-AI...")
    custom_agent.update_system_prompt(
        """You are now a technical documentation specialist AI agent. 
        Your role is to create clear, comprehensive technical documentation.
        Focus on accuracy, clarity, and practical examples."""
    )
    
    # Test LLM configuration update
    print("Updating LLM configuration...")
    custom_agent.update_llm_config(
        temperature=0.3,
        max_tokens=1500,
        model="gpt-4-turbo"
    )
    
    # Add a new task prompt template
    print("Adding new task prompt template...")
    custom_agent.add_task_prompt(
        "documentation",
        """Create technical documentation for the following:

Topic: {topic}
Audience: {audience}
Format: {format}
Key Points: {key_points}

Provide comprehensive documentation with examples and best practices."""
    )
    
    # Test the new prompt template
    doc_task = Task(
        name="Create Documentation",
        description="Generate API documentation",
        data={
            "prompt_template": "documentation",
            "topic": "REST API Endpoints",
            "audience": "developers",
            "format": "markdown",
            "key_points": "authentication, error handling, rate limits"
        }
    )
    
    print("Testing new documentation prompt...")
    custom_agent.add_task(doc_task)
    
    # Wait for processing
    await asyncio.sleep(2)
    
    print("\n🤝 Testing AI Agent Communication:")
    print("-" * 40)
    
    # Test AI-specific communication
    print("Sending AI request to Custom-AI...")
    await coordinator.send_message(
        content={
            "type": "prompt_completion",
            "prompt": "Generate a summary of best practices for multi-agent systems",
            "context_id": "best_practices"
        },
        message_type="ai_request",
        receiver_id=custom_agent.id
    )
    
    # Test context sharing
    print("Testing context sharing between agents...")
    context = custom_agent.create_context("shared_context")
    context.add_message("user", "What are the key components of a multi-agent system?")
    context.add_message("assistant", "Key components include agents, message broker, task management, and coordination mechanisms.")
    
    await custom_agent.share_context("shared_context", analyst.id)
    
    # Wait for message processing
    await asyncio.sleep(2)
    
    print("\n📊 Testing Prompt Templates:")
    print("-" * 30)
    
    # Test different prompt templates
    print("Testing collaboration prompt...")
    collaboration_task = Task(
        name="Collaboration Task",
        description="Coordinate with other agents",
        data={
            "prompt_template": "collaboration",
            "role": "data processor",
            "context": "quarterly report generation",
            "other_agents": "analyst, researcher",
            "goal": "comprehensive quarterly business report"
        }
    )
    
    coordinator.add_task(collaboration_task)
    
    # Wait for processing
    await asyncio.sleep(2)
    
    print("\n📈 Final AI Status Report:")
    print("-" * 30)
    
    for agent in [coordinator, analyst, researcher, custom_agent]:
        status = agent.get_ai_status()
        print(f"Agent: {status['name']}")
        print(f"  - Processed Tasks: {status['task_count']}")
        print(f"  - Active Contexts: {status['contexts']}")
        print(f"  - Current Model: {status['llm_config']['model']}")
        print(f"  - Temperature: {status['llm_config']['temperature']}")
        print()
    
    print("\n💡 Key Features Demonstrated:")
    print("-" * 35)
    print("✅ System prompts for agent personality/role")
    print("✅ Task-specific prompt templates")
    print("✅ Dynamic prompt updates")
    print("✅ LLM configuration management")
    print("✅ Context management and sharing")
    print("✅ AI-specific message handling")
    print("✅ Specialized agent types (Analyst, Researcher, etc.)")
    
    # Stop all agents
    print("\n🛑 Stopping AI agents...")
    await coordinator.stop()
    await analyst.stop()
    await researcher.stop()
    await custom_agent.stop()
    
    print("✅ AI Demo completed successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 