"""
Demo script showing how to use the multi-agent system
"""

import asyncio
import logging
from agent import MessageBroker, WorkerAgent, CoordinatorAgent, Task

# Configure logging to see the agent interactions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    """Main demo function"""
    print("🚀 Starting Multi-Agent System Demo")
    print("=" * 50)
    
    # Create a message broker
    broker = MessageBroker()
    
    # Create agents
    coordinator = CoordinatorAgent("Coordinator-1", broker)
    worker1 = WorkerAgent("Worker-1", broker)
    worker2 = WorkerAgent("Worker-2", broker)
    worker3 = WorkerAgent("Worker-3", broker)
    
    # Start all agents
    await coordinator.start()
    await worker1.start()
    await worker2.start()
    await worker3.start()
    
    # Give agents time to initialize
    await asyncio.sleep(1)
    
    print("\n📊 Agent Status:")
    print("-" * 30)
    for agent in [coordinator, worker1, worker2, worker3]:
        status = agent.get_status()
        print(f"Agent: {status['name']} | Type: {status['type']} | State: {status['state']}")
    
    print("\n🤝 Testing Agent Communication:")
    print("-" * 40)
    
    # Test ping-pong communication
    print("Testing ping-pong communication...")
    await worker1.send_message("ping", "ping", worker2.id)
    await asyncio.sleep(0.5)
    
    # Test worker registration with coordinator
    print("Registering workers with coordinator...")
    for worker in [worker1, worker2, worker3]:
        await worker.send_message(
            content={"type": "worker", "capabilities": list(worker.capabilities)},
            message_type="agent_registration",
            receiver_id=coordinator.id
        )
    
    await asyncio.sleep(1)
    
    print("\n📋 Testing Task Distribution:")
    print("-" * 35)
    
    # Create and assign tasks to coordinator
    tasks = [
        Task(name="Process Data A", description="Process dataset A", priority=3, data={"dataset": "A"}),
        Task(name="Process Data B", description="Process dataset B", priority=2, data={"dataset": "B"}),
        Task(name="Process Data C", description="Process dataset C", priority=1, data={"dataset": "C"})
    ]
    
    for task in tasks:
        coordinator.add_task(task)
        print(f"Added task: {task.name}")
    
    # Let the system process tasks
    print("\n⏳ Processing tasks...")
    await asyncio.sleep(5)
    
    print("\n📈 Final Status Report:")
    print("-" * 25)
    for agent in [coordinator, worker1, worker2, worker3]:
        status = agent.get_status()
        print(f"Agent: {status['name']}")
        print(f"  - Task Count: {status['task_count']}")
        print(f"  - Queued Tasks: {status['queued_tasks']}")
        print(f"  - Capabilities: {', '.join(status['capabilities'])}")
        print()
    
    # Test status request
    print("🔍 Testing Status Request:")
    print("-" * 25)
    await coordinator.send_message("status_request", "status_request", worker1.id)
    await asyncio.sleep(0.5)
    
    # Stop all agents
    print("\n🛑 Stopping agents...")
    await coordinator.stop()
    await worker1.stop()
    await worker2.stop()
    await worker3.stop()
    
    print("✅ Demo completed successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 