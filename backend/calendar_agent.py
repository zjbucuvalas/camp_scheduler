"""
Calendar Agent - Specialized agent for calendar management
Handles adding events to Google Calendar based on requests from Stephie
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dateutil.parser import parse as parse_date

from agent import MessageBroker, Message
from llm_integration import ProductionAIAgent, LLMConfig

logger = logging.getLogger(__name__)

class CalendarAgent(ProductionAIAgent):
    """Specialized calendar management agent for Google Calendar integration"""
    
    # Google Calendar API scopes - include all scopes Google may return
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'openid'
    ]
    
    def __init__(self, broker: MessageBroker, llm_config: LLMConfig):
        system_prompt = """You are a calendar management specialist. Your role is to help add events to Google Calendar based on requests from Stephie.

CRITICAL RESPONSIBILITIES:
1. Process calendar event requests with proper validation
2. Add events to Google Calendar with accurate details
3. Handle date/time parsing and timezone considerations
4. Validate required information before creating events
5. Provide clear feedback on success or failure

REQUIRED INFORMATION FOR CALENDAR EVENTS:
- Event title/name
- Start date and time
- End date and time (or duration)
- Description (optional but recommended)
- Location (optional)

VALIDATION RULES:
1. Start date must be before end date
2. Dates must be valid and in the future (unless specifically historical)
3. Event title cannot be empty
4. If camp information is provided, include it in the event description

COMMUNICATION STYLE:
- Be clear and concise
- Ask for missing information specifically
- Confirm event details before creating
- Provide success/failure feedback
- Use natural language for date/time confirmation

WHAT YOU CAN DO:
- Add events to Google Calendar
- Validate event information
- Parse natural language dates/times
- Handle timezone considerations
- Provide event confirmation details

WHAT YOU CANNOT DO:
- Delete or modify existing events (only add new ones)
- Access calendars without proper authentication
- Create events with invalid date ranges
- Add events without minimum required information

When processing requests:
- Always validate required fields
- Parse dates/times carefully
- Include camp information in descriptions when provided
- Ask for clarification if information is ambiguous
- Provide clear success/failure messages"""

        super().__init__(
            name="CalendarAgent",
            broker=broker,
            llm_config=llm_config,
            system_prompt=system_prompt
        )
        
        # Calendar service will be initialized after authentication
        self.calendar_service = None
        self.credentials = None
        
        # Path for storing credentials
        self.credentials_path = Path(__file__).parent / "credentials"
        self.credentials_path.mkdir(exist_ok=True)
        
        # Track calendar operations
        self.events_created = 0
        self.last_operation_status = None
        
        # Store OAuth flow for web application
        self.oauth_flow = None
    
    async def initialize(self):
        """Initialize the calendar agent and authenticate with Google Calendar"""
        await super().initialize()
        
        try:
            # Initialize Google Calendar service
            await self._authenticate_calendar()
            logger.info("Calendar agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize calendar agent: {e}")
            raise
    
    async def _authenticate_calendar(self):
        """Authenticate with Google Calendar API using web app flow"""
        try:
            creds = None
            token_path = self.credentials_path / 'token.pickle'
            
            # Load existing credentials
            if token_path.exists():
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, prepare for authorization
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # Check for credentials.json file
                    credentials_json = self.credentials_path / 'credentials.json'
                    if not credentials_json.exists():
                        logger.warning("No credentials.json found. Please add Google Calendar API credentials.")
                        logger.info("Visit https://console.cloud.google.com/apis/credentials to create credentials.")
                        return
                    
                    # Create web application flow
                    self.oauth_flow = Flow.from_client_secrets_file(
                        str(credentials_json), 
                        scopes=self.SCOPES
                    )
                    
                    # Set redirect URI for web application
                    self.oauth_flow.redirect_uri = 'http://localhost:8000/api/calendar/oauth-callback'
                    
                    # For now, we'll use a simplified approach where we expect
                    # the user to manually complete the OAuth flow
                    logger.info("Web application OAuth flow prepared. Calendar features will be limited without user authentication.")
                    return
                
                # Save credentials for future use
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build the Calendar service
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            self.credentials = creds
            logger.info("Google Calendar authentication successful")
            
        except Exception as e:
            logger.error(f"Calendar authentication failed: {e}")
            # Continue without calendar service - will handle gracefully
    
    def get_auth_url(self) -> Optional[str]:
        """Get the authorization URL for web application OAuth flow"""
        if not self.oauth_flow:
            return None
        
        try:
            auth_url, _ = self.oauth_flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            return auth_url
        except Exception as e:
            logger.error(f"Error generating auth URL: {e}")
            return None
    
    async def handle_oauth_callback(self, authorization_code: str) -> bool:
        """Handle the OAuth callback with authorization code"""
        if not self.oauth_flow:
            logger.error("OAuth flow not initialized")
            return False
        
        try:
            # Exchange authorization code for credentials
            self.oauth_flow.fetch_token(code=authorization_code)
            creds = self.oauth_flow.credentials
            
            # Save credentials for future use
            token_path = self.credentials_path / 'token.pickle'
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
            
            # Build the Calendar service
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            self.credentials = creds
            
            logger.info("OAuth authentication completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"OAuth callback handling failed: {e}")
            return False

    async def process_calendar_request(self, request: str, context_id: str = None) -> str:
        """Process a calendar event request from Stephie"""
        try:
            # Check if we have calendar service available
            if not self.calendar_service:
                auth_url = self.get_auth_url()
                if auth_url:
                    return f"""I'd like to help you add events to your Google Calendar, but I need permission to access your calendar first.

Please visit this URL to authorize calendar access:
{auth_url}

After authorizing, please try your calendar request again."""
                else:
                    return "I apologize, but I'm unable to access Google Calendar at the moment. Please ensure the calendar credentials are properly configured."
            
            # Create context for the request
            context = self.create_context(context_id or f"calendar_request_{hash(request)}")
            
            # Add the request to context
            context.add_message("user", f"""Process this calendar request and either:
1. Add the event to Google Calendar if all required information is provided
2. Ask for missing information if anything is unclear or missing

Calendar Request: {request}

Required information for events:
- Event title/name
- Start date and time
- End date and time (or duration)
- Description (optional but recommended for camp events)
- Location (optional)

If this is a camp-related event, make sure to include camp details in the description.
If any information is missing or unclear, ask specific questions to get the needed details.""")
            
            # Generate response using LLM
            response = await self._process_with_llm(context)
            
            # Check if the response indicates we should create an event
            should_create = self._should_create_event(response, request)
            logger.info(f"Should create event: {should_create}")
            logger.info(f"Calendar agent response: {response[:200]}...")
            
            if should_create:
                logger.info("Attempting to parse event details...")
                # Parse event details and create the event
                event_details = await self._parse_event_details(request, context)
                logger.info(f"Parsed event details: {event_details}")
                
                if event_details:
                    logger.info("Creating calendar event...")
                    creation_result = await self._create_calendar_event(event_details)
                    logger.info(f"Event creation result: {creation_result}")
                    
                    if creation_result:
                        response += f"\n\n✅ Event created successfully: {creation_result}"
                        self.events_created += 1
                        logger.info(f"Total events created: {self.events_created}")
                    else:
                        response += f"\n\n❌ Failed to create calendar event. Please check the details and try again."
                        logger.error("Event creation failed - creation_result was None")
                else:
                    logger.error("Event creation failed - could not parse event details")
                    response += f"\n\n❌ Could not extract event details from your request. Please provide more specific information about the event."
            else:
                logger.info("Event creation not triggered - should_create_event returned False")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing calendar request: {e}")
            return f"I apologize, but I encountered an error processing your calendar request: {str(e)}"
    
    def _should_create_event(self, response: str, request: str) -> bool:
        """Determine if the response indicates we should create an event"""
        # Be much more aggressive about triggering event creation
        # If we're a CalendarAgent and the request contains calendar intent, just create it
        
        response_lower = response.lower()
        request_lower = request.lower()
        
        # Check if request has clear calendar intent
        calendar_actions = [
            "add to calendar", "add to my calendar", "put on calendar",
            "schedule", "create event", "add event", "calendar event",
            "book", "reserve", "save the date", "mark calendar",
            "add this to", "add that to", "put this on", "put that on"
        ]
        
        # Check if request has calendar intent
        has_calendar_intent = any(action in request_lower for action in calendar_actions)
        
        # If the request has calendar intent, check if we have basic event info
        if has_calendar_intent:
            # Check for event title indicators
            has_title = any(word in request_lower for word in [
                "camp", "event", "meeting", "appointment", "session", "academy", 
                "cosi", "class", "workshop", "conference", "party", "dinner"
            ])
            
            # Check for date/time indicators
            has_date = any(word in request_lower for word in [
                "july", "august", "september", "october", "november", "december",
                "january", "february", "march", "april", "may", "june",
                "date", "day", "week", "month", "today", "tomorrow", "weekend",
                "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
                "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"
            ])
            
            has_time = any(word in request_lower for word in [
                "am", "pm", "morning", "afternoon", "evening", "time", "o'clock", 
                ":", "9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm"
            ])
            
            # If we have basic event information, create the event
            if has_title and (has_date or has_time):
                return True
        
        # Also check response for explicit creation indicators
        create_indicators = [
            "i can add", "can add", "i'll add", "i'll create", "i'll schedule",
            "let me add", "let me create", "let me schedule", "adding", "creating",
            "scheduling", "will add", "will create", "will schedule"
        ]
        
        has_response_intent = any(indicator in response_lower for indicator in create_indicators)
        
        # If the response indicates we're adding and we have calendar intent from request, create it
        if has_response_intent and has_calendar_intent:
            return True
        
        return False
    
    async def _parse_event_details(self, request: str, context) -> Optional[Dict[str, Any]]:
        """Parse event details from the request using LLM"""
        try:
            # Ask LLM to extract structured event data
            context.add_message("user", f"""Extract the following information from the calendar request and return it in JSON format:

Calendar Request: {request}

Required JSON structure:
{{
    "title": "Event title",
    "start_datetime": "YYYY-MM-DD HH:MM:SS",
    "end_datetime": "YYYY-MM-DD HH:MM:SS",
    "description": "Event description",
    "location": "Event location (optional)",
    "timezone": "Timezone (default: America/New_York)"
}}

If any required information is missing, return null for that field.
Only return the JSON, no additional text.""")
            
            json_response = await self._process_with_llm(context)
            
            # Try to parse the JSON response
            try:
                # Clean the response - remove markdown code blocks if present
                cleaned_response = json_response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                if cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:]   # Remove ```
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]  # Remove trailing ```
                cleaned_response = cleaned_response.strip()
                
                event_data = json.loads(cleaned_response)
                return event_data
            except json.JSONDecodeError:
                logger.error(f"Failed to parse event details JSON: {json_response}")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing event details: {e}")
            return None
    
    async def _create_calendar_event(self, event_details: Dict[str, Any]) -> Optional[str]:
        """Create an event in Google Calendar"""
        if not self.calendar_service:
            return None
        
        try:
            # Validate required fields
            if not event_details.get('title') or not event_details.get('start_datetime'):
                logger.error("Missing required event details")
                return None
            
            # Parse start and end times
            start_time = parse_date(event_details['start_datetime'])
            end_time = parse_date(event_details['end_datetime']) if event_details.get('end_datetime') else start_time + timedelta(hours=1)
            
            # Build event object
            event = {
                'summary': event_details['title'],
                'description': event_details.get('description', ''),
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': event_details.get('timezone', 'America/New_York'),
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': event_details.get('timezone', 'America/New_York'),
                },
            }
            
            # Add location if provided
            if event_details.get('location'):
                event['location'] = event_details['location']
            
            # Create the event
            created_event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            event_link = created_event.get('htmlLink')
            self.last_operation_status = "success"
            
            return f"'{event_details['title']}' on {start_time.strftime('%Y-%m-%d at %H:%M')}"
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            self.last_operation_status = "failed"
            return None
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            self.last_operation_status = "failed"
            return None
    
    def get_calendar_status(self) -> Dict[str, Any]:
        """Get the current status of the calendar agent"""
        return {
            "name": self.name,
            "authenticated": self.calendar_service is not None,
            "events_created": self.events_created,
            "last_operation_status": self.last_operation_status,
            "capabilities": [
                "Add calendar events",
                "Parse natural language dates",
                "Validate event information",
                "Google Calendar integration"
            ]
        }
    
    async def add_calendar_event(self, title: str, start_datetime: str, end_datetime: str = None, 
                               description: str = "", location: str = "") -> Dict[str, Any]:
        """Direct method to add a calendar event (for programmatic access)"""
        try:
            event_details = {
                "title": title,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "description": description,
                "location": location
            }
            
            result = await self._create_calendar_event(event_details)
            
            return {
                "success": result is not None,
                "event_info": result,
                "message": f"Event '{title}' created successfully" if result else "Failed to create event"
            }
            
        except Exception as e:
            logger.error(f"Error in add_calendar_event: {e}")
            return {
                "success": False,
                "event_info": None,
                "message": f"Error creating event: {str(e)}"
            } 