"""
Demo script showing how to use the prompt loader with AI agents
"""

import asyncio
import logging
from agent import MessageBroker, Task
from ai_agent import AIAgent
from prompt_loader import PromptLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    """Main demo function for prompt loader"""
    print("📝 Prompt Loader Demo")
    print("=" * 30)
    
    # Create prompt loader
    try:
        loader = PromptLoader()
        print("✅ Prompt loader initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing prompt loader: {e}")
        return
    
    # Show statistics
    stats = loader.get_statistics()
    print(f"\n📊 Prompt Statistics:")
    print(f"  Total prompts: {stats['total_prompts']}")
    print(f"  System prompts: {stats['system_prompts']}")
    print(f"  Task prompts: {stats['task_prompts']}")
    print(f"  Templates: {stats['templates']}")
    print(f"  Examples: {stats['examples']}")
    
    # List available prompts
    print(f"\n📋 Available System Prompts:")
    for prompt in loader.list_prompts("system"):
        print(f"  - {prompt}")
    
    print(f"\n📋 Available Task Prompts:")
    for prompt in loader.list_prompts("task"):
        print(f"  - {prompt}")
    
    # Create message broker
    broker = MessageBroker()
    
    # Create AI agents using loaded system prompts
    print(f"\n🤖 Creating AI Agents with Loaded Prompts:")
    
    # Create analyst agent with loaded system prompt
    analyst_system_prompt = loader.get_system_prompt("analyst")
    if analyst_system_prompt:
        analyst = AIAgent("Data-Analyst", broker, analyst_system_prompt)
        print(f"  ✅ Created Data-Analyst with analyst system prompt")
    else:
        print(f"  ❌ Could not load analyst system prompt")
        return
    
    # Create researcher agent with loaded system prompt
    researcher_system_prompt = loader.get_system_prompt("researcher")
    if researcher_system_prompt:
        researcher = AIAgent("Research-Agent", broker, researcher_system_prompt)
        print(f"  ✅ Created Research-Agent with researcher system prompt")
    else:
        print(f"  ❌ Could not load researcher system prompt")
        return
    
    # Create coordinator agent with loaded system prompt
    coordinator_system_prompt = loader.get_system_prompt("coordinator")
    if coordinator_system_prompt:
        coordinator = AIAgent("Coordinator", broker, coordinator_system_prompt)
        print(f"  ✅ Created Coordinator with coordinator system prompt")
    else:
        print(f"  ❌ Could not load coordinator system prompt")
        return
    
    # Start agents
    await analyst.start()
    await researcher.start()
    await coordinator.start()
    
    # Add task prompt templates to agents
    print(f"\n🎯 Adding Task Prompt Templates:")
    
    # Add data analysis template to analyst
    data_analysis_template = loader.create_prompt_template("data_analysis", "task")
    if data_analysis_template:
        analyst.task_prompts["data_analysis"] = data_analysis_template
        print(f"  ✅ Added data_analysis template to Data-Analyst")
    
    # Add research template to researcher
    research_template = loader.create_prompt_template("research", "task")
    if research_template:
        researcher.task_prompts["research"] = research_template
        print(f"  ✅ Added research template to Research-Agent")
    
    # Add coordination template to coordinator
    coordination_template = loader.create_prompt_template("coordination", "task")
    if coordination_template:
        coordinator.task_prompts["coordination"] = coordination_template
        print(f"  ✅ Added coordination template to Coordinator")
    
    # Test with example data
    print(f"\n🧪 Testing with Example Tasks:")
    
    # Test data analysis task
    analysis_task = Task(
        name="Sales Analysis",
        description="Analyze Q4 sales data",
        data={
            "prompt_template": "data_analysis",
            "task_name": "Q4 Sales Analysis",
            "analysis_type": "Performance Analysis",
            "priority": "High",
            "deadline": "2024-01-15",
            "dataset": "sales_q4_2023.csv",
            "data_source": "CRM System",
            "data_format": "CSV",
            "time_period": "Q4 2023",
            "sample_size": "10,000 records",
            "objective": "Identify top-performing products and regions",
            "key_metrics": "Revenue, Units Sold, Profit Margin",
            "dimensions": "Product, Region, Time",
            "report_format": "Executive Summary + Detailed Report",
            "audience": "Executive Team"
        }
    )
    
    print(f"  📊 Sending analysis task to Data-Analyst...")
    analyst.add_task(analysis_task)
    
    # Test research task
    research_task = Task(
        name="Market Research",
        description="Research AI market trends",
        data={
            "prompt_template": "research",
            "task_name": "AI Market Research",
            "research_type": "Market Analysis",
            "priority": "Medium",
            "deadline": "2024-01-20",
            "topic": "AI Technology Market",
            "research_questions": "What are the key trends? Who are the major players?",
            "scope": "Global market, 2023-2024",
            "time_frame": "2023-2024",
            "depth_level": "Comprehensive",
            "minimum_sources": "20",
            "report_format": "Research Report",
            "audience": "Strategy Team"
        }
    )
    
    print(f"  🔍 Sending research task to Research-Agent...")
    researcher.add_task(research_task)
    
    # Test coordination task
    coordination_task = Task(
        name="Project Coordination",
        description="Coordinate Q1 planning project",
        data={
            "prompt_template": "coordination",
            "task_name": "Q1 Planning Coordination",
            "project_type": "Strategic Planning",
            "priority": "High",
            "deadline": "2024-01-10",
            "objective": "Develop comprehensive Q1 2024 business plan",
            "available_agents": "Data-Analyst, Research-Agent, Strategy-Agent",
            "team_size": "3 agents",
            "phases": "Research, Analysis, Planning, Review",
            "deliverables": "Q1 Business Plan, Budget Forecast, Action Plan"
        }
    )
    
    print(f"  🎯 Sending coordination task to Coordinator...")
    coordinator.add_task(coordination_task)
    
    # Wait for processing
    print(f"\n⏳ Processing tasks...")
    await asyncio.sleep(5)
    
    # Show prompt metadata
    print(f"\n🔍 Prompt Metadata Examples:")
    
    # Show analyst prompt info
    analyst_info = loader.get_prompt_info("analyst")
    if analyst_info:
        print(f"  📊 Analyst Prompt:")
        print(f"    Description: {analyst_info['description']}")
        print(f"    Variables: {len(analyst_info['variables'])}")
        print(f"    Tags: {analyst_info['tags']}")
        print(f"    Preview: {analyst_info['preview'][:100]}...")
    
    # Show data analysis template info
    data_analysis_info = loader.get_prompt_info("data_analysis")
    if data_analysis_info:
        print(f"  📈 Data Analysis Template:")
        print(f"    Variables: {len(data_analysis_info['variables'])}")
        print(f"    Key Variables: {data_analysis_info['variables'][:5]}...")
    
    # Test search functionality
    print(f"\n🔍 Search Examples:")
    
    # Search for analysis-related prompts
    analysis_prompts = loader.search_prompts("analysis")
    print(f"  Analysis-related prompts: {analysis_prompts}")
    
    # Search for coordination prompts
    coordination_prompts = loader.search_prompts("coordination")
    print(f"  Coordination-related prompts: {coordination_prompts}")
    
    # Export prompts
    print(f"\n💾 Exporting prompts...")
    loader.export_prompts("prompts_export.json")
    print(f"  ✅ Exported all prompts to prompts_export.json")
    
    # Show final agent status
    print(f"\n📈 Final Agent Status:")
    for agent in [analyst, researcher, coordinator]:
        status = agent.get_ai_status()
        print(f"  {status['name']}:")
        print(f"    - Tasks processed: {status['task_count']}")
        print(f"    - Prompt templates: {status['prompt_templates']}")
        print(f"    - Task prompts: {status['task_prompts']}")
        print(f"    - Active contexts: {status['contexts']}")
    
    # Test creating prompts from templates
    print(f"\n🎨 Creating Custom Prompts from Templates:")
    
    # Create a custom data analysis prompt
    custom_prompt = loader.create_prompt(
        "data_analysis", 
        "task",
        task_name="Customer Segmentation Analysis",
        analysis_type="Customer Segmentation",
        priority="High",
        dataset="customer_data.csv",
        objective="Identify customer segments for targeted marketing",
        key_metrics="CLV, Purchase Frequency, Churn Rate"
    )
    
    if custom_prompt:
        print(f"  ✅ Created custom data analysis prompt")
        print(f"    Preview: {custom_prompt.render()[:200]}...")
    
    # Stop agents
    print(f"\n🛑 Stopping agents...")
    await analyst.stop()
    await researcher.stop()
    await coordinator.stop()
    
    print(f"\n✅ Prompt loader demo completed successfully!")
    print(f"\n💡 Key Features Demonstrated:")
    print(f"  ✅ Loading system prompts from files")
    print(f"  ✅ Loading task prompt templates")
    print(f"  ✅ Creating AI agents with loaded prompts")
    print(f"  ✅ Using prompt templates for tasks")
    print(f"  ✅ Searching and filtering prompts")
    print(f"  ✅ Exporting prompt collections")
    print(f"  ✅ Creating custom prompts from templates")

if __name__ == "__main__":
    asyncio.run(main()) 