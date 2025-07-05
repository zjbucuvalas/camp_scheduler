"""
Demo script showing Google Gemini integration with the multi-agent system
"""

import asyncio
import logging
import os
from agent import MessageBroker, Task
from llm_integration import ProductionAIAgent, create_gemini_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    """Main demo function for Gemini integration"""
    print("🔮 Google Gemini Multi-Agent Demo")
    print("=" * 40)
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No Gemini API key found!")
        print("Please set one of these environment variables:")
        print("  export GOOGLE_API_KEY='your-api-key'")
        print("  export GEMINI_API_KEY='your-api-key'")
        print("\nYou can get an API key from: https://makersuite.google.com/app/apikey")
        return
    
    # Create message broker
    broker = MessageBroker()
    
    print("🔧 Creating Gemini-powered AI agents...")
    
    try:
        # Create different Gemini configurations for different use cases
        
        # 1. Data Analyst with Gemini Pro
        analyst_config = create_gemini_config(
            model="gemini-1.5-pro",
            temperature=0.3,  # Low temperature for analytical tasks
            max_tokens=2000
        )
        
        analyst = ProductionAIAgent(
            "Gemini-Analyst",
            broker,
            analyst_config,
            system_prompt="""You are a data analyst powered by Google Gemini. 
            Your expertise lies in analyzing complex datasets, identifying patterns, and providing actionable insights.
            Always provide evidence-based analysis with clear methodology."""
        )
        
        # 2. Creative Writer with Gemini Pro
        writer_config = create_gemini_config(
            model="gemini-1.5-pro",
            temperature=0.8,  # Higher temperature for creativity
            max_tokens=1500
        )
        
        writer = ProductionAIAgent(
            "Gemini-Writer",
            broker,
            writer_config,
            system_prompt="""You are a creative writer powered by Google Gemini.
            You excel at generating engaging, original content including stories, articles, and marketing copy.
            Your writing is creative, compelling, and tailored to the target audience."""
        )
        
        # 3. Technical Assistant with Gemini Pro
        tech_config = create_gemini_config(
            model="gemini-1.5-pro",
            temperature=0.2,  # Very low temperature for technical accuracy
            max_tokens=2000
        )
        
        tech_assistant = ProductionAIAgent(
            "Gemini-TechAssistant",
            broker,
            tech_config,
            system_prompt="""You are a technical assistant powered by Google Gemini.
            You provide accurate technical guidance, code reviews, and system architecture advice.
            Your responses are precise, well-structured, and include practical examples."""
        )
        
        # Start all agents
        agents = [analyst, writer, tech_assistant]
        print(f"✅ Created {len(agents)} Gemini-powered agents")
        
        for agent in agents:
            await agent.start()
        
        await asyncio.sleep(1)
        
        print("\n📊 Agent Status:")
        for agent in agents:
            status = agent.get_production_status()
            print(f"  {status['name']}: {status['llm_provider']} - {status['llm_model']}")
        
        print("\n🧪 Testing Gemini Agents with Different Tasks:")
        
        # Test 1: Data Analysis Task
        print("\n1. 📊 Data Analysis Task:")
        analysis_task = Task(
            name="Sales Trend Analysis",
            description="Analyze quarterly sales trends",
            data={
                "sales_data": "Q1: $120k, Q2: $135k, Q3: $128k, Q4: $155k",
                "previous_year": "Q1: $100k, Q2: $115k, Q3: $110k, Q4: $130k",
                "focus": "growth patterns and seasonal trends"
            }
        )
        
        print("  Sending to Gemini-Analyst...")
        analyst.add_task(analysis_task)
        
        # Test 2: Creative Writing Task
        print("\n2. ✍️ Creative Writing Task:")
        writing_task = Task(
            name="Product Launch Blog Post",
            description="Write an engaging blog post for a new AI product",
            data={
                "product": "AI-Powered Code Assistant",
                "audience": "software developers",
                "tone": "professional but approachable",
                "length": "medium-form blog post",
                "key_features": "auto-completion, bug detection, performance optimization"
            }
        )
        
        print("  Sending to Gemini-Writer...")
        writer.add_task(writing_task)
        
        # Test 3: Technical Task
        print("\n3. 🔧 Technical Architecture Task:")
        tech_task = Task(
            name="System Architecture Review",
            description="Review and suggest improvements for a microservices architecture",
            data={
                "services": "user-service, order-service, payment-service, notification-service",
                "current_issues": "high latency, occasional service failures",
                "scale": "10,000 daily active users",
                "tech_stack": "Node.js, PostgreSQL, Redis, Docker"
            }
        )
        
        print("  Sending to Gemini-TechAssistant...")
        tech_assistant.add_task(tech_task)
        
        # Wait for processing
        print("\n⏳ Processing tasks with Gemini...")
        await asyncio.sleep(8)  # Gemini might be a bit slower
        
        print("\n📈 Task Completion Status:")
        for agent in agents:
            status = agent.get_production_status()
            print(f"  {status['name']}:")
            print(f"    - Requests: {status['request_count']}")
            print(f"    - Errors: {status['error_count']}")
            print(f"    - Error Rate: {status['error_rate']:.1f}%")
            print(f"    - Model: {status['llm_model']}")
        
        # Test different Gemini models (if available)
        print("\n🔄 Testing Different Gemini Models:")
        
        try:
            # Test with Gemini Flash (faster, more efficient)
            flash_config = create_gemini_config(
                model="gemini-1.5-flash",
                temperature=0.5,
                max_tokens=1000
            )
            
            flash_agent = ProductionAIAgent(
                "Gemini-Flash",
                broker,
                flash_config,
                system_prompt="You are a quick-response AI assistant powered by Gemini Flash."
            )
            
            await flash_agent.start()
            
            quick_task = Task(
                name="Quick Summary",
                description="Provide a quick summary of AI trends",
                data={"topic": "AI trends in 2024", "format": "bullet points"}
            )
            
            print("  Testing Gemini Flash for quick responses...")
            flash_agent.add_task(quick_task)
            await asyncio.sleep(3)
            
            flash_status = flash_agent.get_production_status()
            print(f"  Gemini Flash: {flash_status['request_count']} requests, {flash_status['error_rate']:.1f}% error rate")
            
            await flash_agent.stop()
            
        except Exception as e:
            print(f"  Note: Gemini Flash test skipped: {e}")
        
        # Test multimodal capabilities (if you want to extend later)
        print("\n💡 Gemini Features Demonstrated:")
        print("  ✅ Multiple Gemini model variants")
        print("  ✅ Different temperature settings for different tasks")
        print("  ✅ System instructions support")
        print("  ✅ Production-ready error handling")
        print("  ✅ Rate limiting and retries")
        print("  ✅ Seamless integration with multi-agent system")
        
        # Test agent communication
        print("\n🤝 Testing Inter-Agent Communication:")
        
        # Send a message from analyst to writer
        await analyst.send_message(
            content={
                "type": "collaboration_request",
                "task": "Create a data story based on sales analysis",
                "data": "Q4 sales increased 19% YoY, driven by strong holiday performance"
            },
            message_type="ai_request",
            receiver_id=writer.id
        )
        
        print("  📊 → ✍️ Analyst sent collaboration request to Writer")
        
        await asyncio.sleep(2)
        
        # Show final performance metrics
        print("\n📊 Final Performance Metrics:")
        total_requests = 0
        total_errors = 0
        
        for agent in agents:
            status = agent.get_production_status()
            total_requests += status['request_count']
            total_errors += status['error_count']
        
        overall_error_rate = (total_errors / max(total_requests, 1)) * 100
        print(f"  Total Requests: {total_requests}")
        print(f"  Total Errors: {total_errors}")
        print(f"  Overall Error Rate: {overall_error_rate:.1f}%")
        
        # Stop all agents
        print("\n🛑 Stopping Gemini agents...")
        for agent in agents:
            await agent.stop()
        
        print("\n✅ Gemini integration demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("Make sure your Gemini API key is valid and you have proper permissions.")

if __name__ == "__main__":
    asyncio.run(main()) 