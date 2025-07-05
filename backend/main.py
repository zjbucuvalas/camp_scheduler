import os
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("../.env")

# Import the existing AI agent system
import sys
sys.path.append('..')
from agent import MessageBroker, Message
from ai_agent import AIAgent, AIContext
from llm_integration import create_gemini_config, ProductionAIAgent, LLMProvider, LLMConfig
from camp_agent import CampAgent
from calendar_agent import CalendarAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for the agent system
broker = None
scheduling_agent = None
camp_agent = None
calendar_agent = None

class ChatMessage(BaseModel):
    message: str
    user_email: Optional[str] = None
    context_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    context_id: str
    timestamp: str

class CalendarEventRequest(BaseModel):
    title: str
    start_datetime: str
    end_datetime: Optional[str] = None
    description: Optional[str] = ""
    location: Optional[str] = ""

class CalendarEventResponse(BaseModel):
    success: bool
    event_info: Optional[str] = None
    message: str

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

IMPORTANT: When users ask to schedule, add, or create calendar events, you MUST delegate to the CalendarAgent. Do not try to create calendar events yourself.

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
    
    def _is_calendar_request(self, message: str) -> bool:
        """Check if the message is a calendar/scheduling request"""
        calendar_keywords = [
            'schedule', 'add to calendar', 'create event', 'book', 'appointment',
            'meeting', 'add event', 'calendar', 'remind me', 'set reminder',
            'plan', 'organize', 'time slot', 'availability', 'busy', 'free time',
            'block time', 'reserve', 'pencil in', 'put on calendar', 'add to schedule',
            'schedule for', 'book for', 'set up meeting', 'arrange', 'coordinate time',
            'when can we', 'what time', 'available', 'schedule this', 'add this to',
            'put this on', 'calendar event', 'calendar entry', 'save the date',
            'mark calendar', 'schedule reminder', 'set appointment', 'book appointment',
            'camp registration', 'enroll', 'sign up for', 'register for camp',
            'camp dates', 'camp schedule', 'camp session', 'camp week'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in calendar_keywords)
    
    async def process_chat_message(self, message: str, user_email: str = None, context_id: str = None) -> tuple[str, str]:
        """Process a chat message and return response with context ID"""
        try:
            # Check if this is a calendar/scheduling request FIRST (priority over camp questions)
            if self._is_calendar_request(message) and calendar_agent:
                logger.info(f"Delegating calendar request to CalendarAgent: {message[:50]}...")
                # Delegate to calendar agent
                calendar_response = await calendar_agent.process_calendar_request(message, context_id)
                return calendar_response, context_id or f"calendar_{hash(message)}"
            
            # Check if this is a camp-related question (informational)
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
    global broker, scheduling_agent, camp_agent, calendar_agent
    
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
        
        # Create the calendar agent
        calendar_agent = CalendarAgent(broker, gemini_config)
        
        # Initialize the agents
        await scheduling_agent.initialize()
        await scheduling_agent.start()
        
        await camp_agent.initialize()
        await camp_agent.start()
        
        await calendar_agent.initialize()
        await calendar_agent.start()
        
        logger.info("Scheduling assistant, camp agent, and calendar agent started successfully")
        
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
        
        if calendar_agent:
            await calendar_agent.stop()
        
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
        "calendar_agent_available": calendar_agent is not None,
        "scheduling_agent_status": scheduling_agent.get_production_status() if scheduling_agent else None,
        "camp_agent_status": camp_agent.get_production_status() if camp_agent else None,
        "calendar_agent_status": calendar_agent.get_calendar_status() if calendar_agent else None
    }

@app.get("/api/agent/status")
async def get_agent_status():
    """Get the current status of the agents"""
    if not scheduling_agent and not camp_agent and not calendar_agent:
        raise HTTPException(status_code=404, detail="No agents found")
    
    status = {}
    if scheduling_agent:
        status["scheduling_agent"] = scheduling_agent.get_production_status()
    if camp_agent:
        status["camp_agent"] = camp_agent.get_production_status()
    if calendar_agent:
        status["calendar_agent"] = calendar_agent.get_calendar_status()
    
    return status

@app.post("/api/calendar/add-event", response_model=CalendarEventResponse)
async def add_calendar_event(event_request: CalendarEventRequest):
    """Add an event to the calendar"""
    try:
        if not calendar_agent:
            raise HTTPException(status_code=500, detail="Calendar agent not available")
        
        # Add the event using the calendar agent
        result = await calendar_agent.add_calendar_event(
            title=event_request.title,
            start_datetime=event_request.start_datetime,
            end_datetime=event_request.end_datetime,
            description=event_request.description,
            location=event_request.location
        )
        
        return CalendarEventResponse(
            success=result["success"],
            event_info=result["event_info"],
            message=result["message"]
        )
        
    except Exception as e:
        logger.error(f"Error in add calendar event endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/calendar/status")
async def get_calendar_status():
    """Get the current status of the calendar agent"""
    if not calendar_agent:
        raise HTTPException(status_code=404, detail="Calendar agent not found")
    
    return calendar_agent.get_calendar_status()

@app.get("/api/calendar/auth-url")
async def get_calendar_auth_url():
    """Get the Google Calendar authorization URL for OAuth flow"""
    if not calendar_agent:
        raise HTTPException(status_code=404, detail="Calendar agent not found")
    
    auth_url = calendar_agent.get_auth_url()
    if not auth_url:
        raise HTTPException(status_code=500, detail="Unable to generate authorization URL")
    
    return {"auth_url": auth_url}

@app.get("/api/calendar/oauth-callback")
async def handle_calendar_oauth_callback_get(code: str = None, state: str = None):
    """Handle the OAuth callback with authorization code (GET request from Google)"""
    if not calendar_agent:
        raise HTTPException(status_code=404, detail="Calendar agent not found")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is required")
    
    success = await calendar_agent.handle_oauth_callback(code)
    if success:
        # Return HTML page that closes the popup and notifies the parent window
        html_content = """
        <html>
        <head><title>Authorization Successful</title></head>
        <body>
            <h1>✅ Calendar Authorization Successful!</h1>
            <p>You can close this window and try creating your calendar event again.</p>
            <script>
                // Notify parent window and close popup
                console.log('OAuth callback received, attempting to close popup...');
                
                // Try multiple methods to notify parent and close popup
                function notifyAndClose() {
                    if (window.opener && !window.opener.closed) {
                        console.log('Notifying parent window...');
                        window.opener.postMessage({
                            type: 'OAUTH_SUCCESS',
                            source: 'calendar_auth'
                        }, '*');
                        
                        // Small delay to ensure message is sent
                        setTimeout(() => {
                            window.close();
                        }, 100);
                    } else if (window.parent && window.parent !== window) {
                        console.log('Notifying parent frame...');
                        window.parent.postMessage({
                            type: 'OAUTH_SUCCESS',
                            source: 'calendar_auth'
                        }, '*');
                        
                        setTimeout(() => {
                            window.close();
                        }, 100);
                    } else {
                        console.log('No parent found, redirecting...');
                        // If not in popup, redirect back to the app
                        window.location.href = 'http://localhost:5173';
                    }
                }
                
                // Call immediately and also after a short delay as backup
                notifyAndClose();
                setTimeout(notifyAndClose, 500);
                
                // Auto-close after 3 seconds as fallback
                setTimeout(() => {
                    console.log('Auto-closing popup...');
                    window.close();
                }, 3000);
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    else:
        raise HTTPException(status_code=500, detail="OAuth callback handling failed")

@app.post("/api/calendar/oauth-callback")
async def handle_calendar_oauth_callback_post(callback_data: dict):
    """Handle the OAuth callback with authorization code (POST request for programmatic access)"""
    if not calendar_agent:
        raise HTTPException(status_code=404, detail="Calendar agent not found")
    
    authorization_code = callback_data.get("code")
    if not authorization_code:
        raise HTTPException(status_code=400, detail="Authorization code is required")
    
    success = await calendar_agent.handle_oauth_callback(authorization_code)
    if success:
        return {"success": True, "message": "Calendar authorization completed successfully"}
    else:
        raise HTTPException(status_code=500, detail="OAuth callback handling failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 