import os
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import logging
from datetime import datetime

# Import the existing AI agent system
import sys
sys.path.append('..')
from agent import MessageBroker, Message
from ai_agent import AIAgent, AIContext
from llm_integration import create_gemini_config, ProductionAIAgent, LLMProvider, LLMConfig
from camp_agent import CampAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for the agent system
broker = None
scheduling_agent = None
camp_agent = None

class ChatMessage(BaseModel):
    message: str
    user_email: Optional[str] = None
    context_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    context_id: str
    timestamp: str

class SchedulingAssistant(ProductionAIAgent):
    """Specialized scheduling assistant agent powered by Gemini"""
    
    def __init__(self, broker: MessageBroker, llm_config: LLMConfig):
        system_prompt = """You are a helpful scheduling assistant. Your primary role is to help users manage their calendar and schedule events efficiently.

Key capabilities:
- Help users schedule meetings, appointments, and events
- Provide suggestions for optimal meeting times
- Assist with calendar management and organization
- Answer questions about upcoming events
- Help resolve scheduling conflicts
- Provide reminders and scheduling best practices

IMPORTANT: When users ask ANY questions about summer camps, you MUST delegate to the CampAgent. Do not try to answer camp questions yourself.

Communication style:
- Be friendly, professional, and proactive
- Keep responses concise and to the point
- Ask clarifying questions when needed
- Provide clear, actionable advice

When users ask about scheduling, consider factors like:
- Time zones and availability
- Meeting duration and purpose
- Potential conflicts with existing events
- Optimal times for different types of meetings
- Follow-up and preparation requirements

Remember to be conversational and helpful while maintaining focus on calendar and scheduling assistance."""

        super().__init__(
            name="SchedulingAssistant",
            broker=broker,
            llm_config=llm_config,
            system_prompt=system_prompt
        )
        
        # Track active conversations
        self.active_conversations: Dict[str, AIContext] = {}
    
    def _is_camp_question(self, message: str) -> bool:
        """Check if the message is related to camps"""
        camp_keywords = [
            'camp', 'summer camp', 'day camp', 'overnight camp', 'sleepaway camp',
            'columbus camp', 'ohio camp', 'camp for', 'camps for',
            'stem camp', 'art camp', 'sports camp', 'nature camp', 'adventure camp',
            'academic camp', 'enrichment camp', 'creative camp', 'dance camp',
            'theater camp', 'music camp', 'soccer camp', 'basketball camp',
            'swimming camp', 'tennis camp', 'golf camp', 'baseball camp',
            'football camp', 'volleyball camp', 'hockey camp', 'lacrosse camp',
            'track camp', 'cross country camp', 'wrestling camp', 'martial arts camp',
            'gymnastics camp', 'cheerleading camp', 'diving camp', 'water polo camp',
            'rowing camp', 'sailing camp', 'canoeing camp', 'kayaking camp',
            'rock climbing camp', 'zip line camp', 'ropes course camp',
            'archery camp', 'riflery camp', 'fishing camp', 'hunting camp',
            'survival camp', 'outdoor camp', 'wilderness camp', 'forest camp',
            'zoo camp', 'museum camp', 'science camp', 'technology camp',
            'computer camp', 'coding camp', 'programming camp', 'robotics camp'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in camp_keywords)
    
    async def process_chat_message(self, message: str, user_email: str = None, context_id: str = None) -> tuple[str, str]:
        """Process a chat message and return response with context ID"""
        try:
            # Check if this is a camp-related question
            if self._is_camp_question(message) and camp_agent:
                logger.info(f"Delegating camp question to CampAgent: {message[:50]}...")
                # Delegate to camp agent
                camp_response = await camp_agent.process_camp_question(message, context_id)
                return camp_response, context_id or f"camp_{hash(message)}"
            
            # Create or get existing context for scheduling questions
            if context_id and context_id in self.active_conversations:
                context = self.active_conversations[context_id]
            else:
                context_id = f"chat_{user_email or 'anonymous'}_{datetime.now().isoformat()}"
                context = self.create_context(context_id)
                self.active_conversations[context_id] = context
            
            # Add user message to context
            context.add_message("user", message)
            
            # Generate response using the LLM
            response = await self._process_with_llm(context)
            
            # Add assistant response to context
            context.add_message("assistant", response)
            
            return response, context_id
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return f"I apologize, but I encountered an error processing your request. Please try again.", context_id or "error"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the lifespan of the FastAPI application"""
    global broker, scheduling_agent, camp_agent
    
    # Startup
    try:
        logger.info("Starting up scheduling assistant backend...")
        
        # Create message broker
        broker = MessageBroker()
        
        # Create Gemini configuration for the specific model
        gemini_config = create_gemini_config(
            model="gemini-2.5-flash",
            temperature=0.7,
            max_tokens=8192,  # Set high to avoid token limits as requested
            timeout=60.0,
            retry_attempts=3,
            rate_limit_delay=1.0
        )
        
        # Create the scheduling assistant agent
        scheduling_agent = SchedulingAssistant(broker, gemini_config)
        
        # Create the camp agent
        camp_agent = CampAgent(broker, gemini_config)
        
        # Initialize the agents
        await scheduling_agent.initialize()
        await scheduling_agent.start()
        
        await camp_agent.initialize()
        await camp_agent.start()
        
        logger.info("Scheduling assistant and camp agent started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start backend: {e}")
        raise
    
    yield
    
    # Shutdown
    try:
        logger.info("Shutting down scheduling assistant backend...")
        
        if scheduling_agent:
            await scheduling_agent.stop()
        
        if camp_agent:
            await camp_agent.stop()
        
        logger.info("Backend shut down successfully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI app with lifespan management
app = FastAPI(
    title="Scheduling Assistant API",
    description="API for the scheduling assistant chat functionality",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Handle chat messages from the frontend"""
    try:
        if not scheduling_agent:
            raise HTTPException(status_code=500, detail="Scheduling assistant not available")
        
        # Process the message
        response, context_id = await scheduling_agent.process_chat_message(
            message=chat_message.message,
            user_email=chat_message.user_email,
            context_id=chat_message.context_id
        )
        
        return ChatResponse(
            response=response,
            context_id=context_id,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "scheduling_agent_available": scheduling_agent is not None,
        "camp_agent_available": camp_agent is not None,
        "scheduling_agent_status": scheduling_agent.get_production_status() if scheduling_agent else None,
        "camp_agent_status": camp_agent.get_production_status() if camp_agent else None
    }

@app.get("/api/agent/status")
async def get_agent_status():
    """Get the current status of the agents"""
    if not scheduling_agent and not camp_agent:
        raise HTTPException(status_code=404, detail="No agents found")
    
    status = {}
    if scheduling_agent:
        status["scheduling_agent"] = scheduling_agent.get_production_status()
    if camp_agent:
        status["camp_agent"] = camp_agent.get_production_status()
    
    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 