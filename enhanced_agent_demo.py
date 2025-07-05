"""
Demo script showing the Enhanced AI Agent with direct parameter interface
"""

import asyncio
import logging
import os
from agent import MessageBroker, Task
from enhanced_agent import (
    EnhancedAIAgent, 
    create_business_analyst, 
    create_creative_writer, 
    create_technical_assistant,
    create_customer_support
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    """Main demo function for Enhanced AI Agents"""
    print("🚀 Enhanced AI Agent Demo")
    print("=" * 40)
    print("Now agents accept direct parameters:")
    print("- company_name: Company/organization context")
    print("- model_name: LLM model to use")
    print("- heat: Temperature for creativity (0.0-1.0)")
    print("- token_limit: Maximum response tokens")
    print("- provider: LLM provider (openai, anthropic, google)")
    print()
    
    # Create message broker
    broker = MessageBroker()
    
    # Example 1: Direct parameter usage
    print("📝 Example 1: Direct Parameter Usage")
    print("-" * 35)
    
    direct_agent = EnhancedAIAgent(
        name="DirectAgent",
        broker=broker,
        company_name="Tech Innovations Inc",
        model_name="gpt-4",
        heat=0.7,
        token_limit=1500,
        provider="openai",
        system_prompt="You are a versatile AI assistant for a tech company."
    )
    
    await direct_agent.start()
    
    status = direct_agent.get_enhanced_status()
    print(f"✅ Created {status['name']}:")
    print(f"   Company: {status['company_name']}")
    print(f"   Model: {status['model_name']}")
    print(f"   Heat: {status['heat']}")
    print(f"   Token Limit: {status['token_limit']}")
    print(f"   Provider: {status['provider']}")
    
    # Example 2: Using convenience functions
    print("\n🏭 Example 2: Convenience Functions")
    print("-" * 35)
    
    # Business analyst with conservative settings
    analyst = create_business_analyst(
        name="DataAnalyst",
        broker=broker,
        company_name="Analytics Pro Ltd",
        model_name="gpt-4",
        heat=0.2,  # Low heat for analytical work
        provider="openai"
    )
    
    # Creative writer with high creativity
    writer = create_creative_writer(
        name="ContentCreator",
        broker=broker,
        company_name="Creative Agency X",
        model_name="claude-3-sonnet-20240229",
        heat=0.9,  # High heat for creativity
        provider="anthropic"  # Using Anthropic for creative tasks
    )
    
    # Technical assistant with precise settings
    tech_expert = create_technical_assistant(
        name="TechGuru",
        broker=broker,
        company_name="DevOps Solutions",
        model_name="gemini-1.5-pro",
        heat=0.1,  # Very low heat for technical accuracy
        provider="google"  # Using Gemini for technical work
    )
    
    # Customer support with balanced settings
    support_agent = create_customer_support(
        name="SupportBot",
        broker=broker,
        company_name="Customer First Corp",
        model_name="gpt-3.5-turbo",
        heat=0.4,  # Balanced heat for customer service
        provider="openai"
    )
    
    # Start all agents
    agents = [analyst, writer, tech_expert, support_agent]
    for agent in agents:
        await agent.start()
    
    await asyncio.sleep(1)
    
    print("\n📊 Agent Portfolio:")
    for agent in agents:
        status = agent.get_enhanced_status()
        print(f"  {status['name']} @ {status['company_name']}:")
        print(f"    Model: {status['model_name']} | Heat: {status['heat']} | Tokens: {status['token_limit']}")
    
    # Example 3: Different use cases with tailored parameters
    print("\n🎯 Example 3: Task-Specific Configurations")
    print("-" * 40)
    
    # Task 1: Data analysis (low heat, high tokens)
    analysis_task = Task(
        name="Market Analysis",
        description="Analyze market trends and provide recommendations",
        data={
            "market_data": "Q1 sales up 15%, Q2 flat, Q3 down 8%, Q4 up 22%",
            "competitors": "CompA, CompB, CompC",
            "budget": "$500K for next quarter"
        }
    )
    
    print(f"📊 Sending analysis task to {analyst.name} (heat: {analyst.heat})")
    analyst.add_task(analysis_task)
    
    # Task 2: Creative content (high heat, medium tokens)
    creative_task = Task(
        name="Brand Story",
        description="Create engaging brand story for product launch",
        data={
            "product": "Smart Home Assistant",
            "target_audience": "Tech-savvy families",
            "brand_values": "Innovation, Privacy, Simplicity"
        }
    )
    
    print(f"✍️ Sending creative task to {writer.name} (heat: {writer.heat})")
    writer.add_task(creative_task)
    
    # Task 3: Technical documentation (very low heat, high tokens)
    tech_task = Task(
        name="API Documentation",
        description="Create comprehensive API documentation",
        data={
            "api_endpoints": "/users, /orders, /payments",
            "authentication": "OAuth 2.0",
            "rate_limits": "100 requests/minute"
        }
    )
    
    print(f"🔧 Sending technical task to {tech_expert.name} (heat: {tech_expert.heat})")
    tech_expert.add_task(tech_task)
    
    # Task 4: Customer support (balanced heat, low tokens)
    support_task = Task(
        name="Customer Inquiry",
        description="Handle customer billing question",
        data={
            "customer_issue": "Billing discrepancy on last invoice",
            "customer_tier": "Premium",
            "urgency": "Medium"
        }
    )
    
    print(f"🎧 Sending support task to {support_agent.name} (heat: {support_agent.heat})")
    support_agent.add_task(support_task)
    
    # Wait for processing
    print("\n⏳ Processing tasks...")
    await asyncio.sleep(5)
    
    # Example 4: Dynamic parameter updates
    print("\n🔄 Example 4: Dynamic Parameter Updates")
    print("-" * 37)
    
    print("Before updates:")
    print(f"  {direct_agent.name}: heat={direct_agent.heat}, tokens={direct_agent.token_limit}")
    
    # Update parameters dynamically
    direct_agent.update_parameters(
        heat=0.9,  # Increase creativity
        token_limit=2500,  # Increase response length
        company_name="Advanced AI Corp"  # Change company context
    )
    
    print("After updates:")
    print(f"  {direct_agent.name}: heat={direct_agent.heat}, tokens={direct_agent.token_limit}")
    print(f"  Company: {direct_agent.company_name}")
    
    # Example 5: Multi-provider comparison
    print("\n🔄 Example 5: Multi-Provider Comparison")
    print("-" * 37)
    
    # Create same agent type with different providers
    comparison_agents = []
    
    providers = [
        ("openai", "gpt-4"),
        ("anthropic", "claude-3-sonnet-20240229"),
        ("google", "gemini-1.5-pro")
    ]
    
    for provider, model in providers:
        try:
            agent = EnhancedAIAgent(
                name=f"Comparison-{provider.title()}",
                broker=broker,
                company_name="Multi-AI Corp",
                model_name=model,
                heat=0.5,
                token_limit=1000,
                provider=provider
            )
            
            await agent.start()
            comparison_agents.append(agent)
            
            print(f"✅ Created {agent.name} using {provider} {model}")
            
        except Exception as e:
            print(f"⚠️ Skipped {provider}: {e}")
    
    # Send same task to all comparison agents
    if comparison_agents:
        comparison_task = Task(
            name="Innovation Ideas",
            description="Generate 3 innovative product ideas",
            data={"industry": "fintech", "budget": "unlimited"}
        )
        
        print(f"\n📤 Sending same task to {len(comparison_agents)} different providers...")
        for agent in comparison_agents:
            agent.add_task(comparison_task)
    
    await asyncio.sleep(3)
    
    # Final status report
    print("\n📈 Final Status Report:")
    print("-" * 22)
    
    all_agents = [direct_agent] + agents + comparison_agents
    
    for agent in all_agents:
        status = agent.get_enhanced_status()
        print(f"  {status['name']}:")
        print(f"    Company: {status['company_name']}")
        print(f"    Provider: {status['provider']}")
        print(f"    Model: {status['model_name']}")
        print(f"    Heat: {status['heat']}")
        print(f"    Token Limit: {status['token_limit']}")
        print(f"    Requests: {status['request_count']}")
        print(f"    Errors: {status['error_count']}")
        print()
    
    # Stop all agents
    print("🛑 Stopping all agents...")
    for agent in all_agents:
        await agent.stop()
    
    print("\n✅ Enhanced Agent Demo completed!")
    print("\nKey Features Demonstrated:")
    print("  ✅ Direct parameter interface (company_name, model_name, heat, token_limit)")
    print("  ✅ Automatic company context integration")
    print("  ✅ Multi-provider support (OpenAI, Anthropic, Google)")
    print("  ✅ Convenience functions for common agent types")
    print("  ✅ Dynamic parameter updates")
    print("  ✅ Task-specific configurations")
    print("  ✅ Enhanced status reporting")

if __name__ == "__main__":
    asyncio.run(main()) 