# Scheduling Assistant Backend

A FastAPI backend server that powers the scheduling assistant chat functionality using Google's Gemini-2.5-Flash-Lite-Preview-06-17 model.

## 🚀 Quick Start

### 1. Set up your Google API Key

Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

Set the environment variable:
```bash
export GOOGLE_API_KEY="your-api-key-here"
# or
export GEMINI_API_KEY="your-api-key-here"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Calendar Agent (Optional)

For calendar functionality, you'll need to configure Google Calendar API access:

1. Follow the detailed setup guide in `CALENDAR_SETUP.md`
2. Download OAuth credentials from Google Cloud Console
3. Place `credentials.json` in the `credentials/` directory

**Note**: The server will start without calendar credentials, but calendar features will be disabled.

### 4. Start the Server

#### Option A: Using the start script (recommended)
```bash
python start_server.py
```

#### Option B: Direct uvicorn command
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

### 5. Start the React Frontend

In a separate terminal, go to the camp-scheduler directory and start the React app:
```bash
cd ../camp-scheduler
npm install  # if not already installed
npm run dev
```

The React app will be available at `http://localhost:5173`

## 📋 API Endpoints

### Chat Endpoint
- **POST** `/api/chat` - Send a message to the scheduling assistant
- **GET** `/api/health` - Health check endpoint
- **GET** `/api/agent/status` - Get current agent status
- **GET** `/docs` - Interactive API documentation

### Calendar API Endpoints
- **POST** `/api/calendar/add-event` - Add events directly to Google Calendar
- **GET** `/api/calendar/status` - Check calendar agent status and authentication

## 🤖 Features

### Scheduling Assistant Capabilities
- **Calendar Management**: Help users organize and manage their calendar events
- **Meeting Scheduling**: Assist with scheduling meetings and appointments
- **Time Optimization**: Suggest optimal meeting times based on availability
- **Conflict Resolution**: Help resolve scheduling conflicts
- **Event Planning**: Support for planning and organizing events
- **Reminders**: Provide scheduling reminders and best practices

### Calendar Agent Features
- **Google Calendar Integration**: Direct integration with Google Calendar API
- **Automatic Event Creation**: Creates calendar events from natural language requests
- **Camp Registration**: Handles summer camp registration and scheduling
- **Smart Delegation**: Automatically routes calendar requests from the chat interface
- **Date/Time Parsing**: Understands various date and time formats
- **Event Validation**: Ensures all required information is present before creating events

### Technical Features
- **No Token Limit**: Configured with high token limits (8192) to avoid restrictions
- **Conversation Context**: Maintains conversation history for better responses
- **Error Handling**: Robust error handling and retry mechanisms
- **CORS Support**: Properly configured for React frontend communication
- **Real-time Responses**: Powered by Google's Gemini-2.5-Flash-Lite-Preview-06-17

## 🔧 Configuration

The system is configured with:
- **Model**: `gemini-2.5-flash-lite-preview-06-17`
- **Max Tokens**: 8192 (effectively no limit)
- **Temperature**: 0.7 (balanced creativity/consistency)
- **Timeout**: 60 seconds
- **Retry Attempts**: 3

## 🛠️ Development

### Project Structure
```
backend/
├── main.py              # FastAPI application
├── camp_agent.py        # Camp information agent
├── calendar_agent.py    # Google Calendar integration agent
├── requirements.txt     # Python dependencies
├── start_server.py     # Server startup script
├── CALENDAR_SETUP.md    # Calendar setup guide
├── credentials/         # Google Calendar API credentials
│   └── README.md       # Credential setup instructions
└── README.md           # This file
```

### Key Components
- **SchedulingAssistant**: Specialized AI agent for scheduling tasks
- **CampAgent**: Provides information about summer camps in Columbus
- **CalendarAgent**: Handles Google Calendar integration and event creation
- **Chat API**: RESTful API for frontend communication
- **Context Management**: Maintains conversation state
- **Error Handling**: Comprehensive error management

## 🔍 Testing

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Test Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me schedule a meeting for tomorrow at 2pm", "user_email": "test@example.com"}'
```

### Test Calendar Integration
```bash
# Check calendar agent status
curl http://localhost:8000/api/calendar/status

# Add event directly to calendar
curl -X POST http://localhost:8000/api/calendar/add-event \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "start_datetime": "2024-07-15 14:00:00",
    "end_datetime": "2024-07-15 15:00:00",
    "description": "Weekly team sync",
    "location": "Conference Room A"
  }'

# Test calendar request via chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a summer camp session to my calendar for July 15-19, 9am to 3pm daily"}'
```

## 🐛 Troubleshooting

### Common Issues

1. **"Google Gemini API key is required"**
   - Make sure you've set the `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable
   - Get your API key from https://makersuite.google.com/app/apikey

2. **"No module named 'fastapi'"**
   - Install dependencies: `pip install -r requirements.txt`

3. **CORS errors in frontend**
   - Make sure the backend is running on port 8000
   - Check that the React app is running on port 5173 or 3000

4. **"Scheduling assistant not available"**
   - Check if the Google API key is valid
   - Look at the server logs for initialization errors

5. **"Calendar agent not available"**
   - Follow the setup guide in `CALENDAR_SETUP.md`
   - Ensure `credentials.json` is in the `credentials/` directory
   - Check that Google Calendar API is enabled in Google Cloud Console

6. **"Authentication failed" for calendar**
   - Delete `credentials/token.pickle` to force re-authentication
   - Verify OAuth consent screen is configured correctly
   - Check that your Google account has calendar access

### Logs
The server provides detailed logging. Check the console output for:
- Agent initialization status
- API request/response details
- Error messages and stack traces

## 📚 API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger UI.

## 🔐 Security Notes

- The API key is loaded from environment variables (not hardcoded)
- CORS is configured to only allow specific origins
- Input validation is performed on all endpoints
- Error messages don't expose sensitive information

## 📈 Performance

- **Model Speed**: Uses Gemini-2.5-Flash-Lite for fast responses
- **Concurrent Requests**: Supports multiple simultaneous conversations
- **Memory Management**: Efficiently manages conversation contexts
- **Rate Limiting**: Built-in rate limiting to prevent API abuse 