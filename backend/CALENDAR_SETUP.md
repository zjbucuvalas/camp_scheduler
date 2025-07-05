# Calendar Agent Setup Guide

This guide will help you set up the Calendar Agent with Google Calendar API integration.

## Prerequisites

- Python 3.8 or higher
- Google Account with access to Google Calendar
- Google Cloud Console project (or ability to create one)

## Step 1: Google Cloud Console Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to **APIs & Services** > **Library**
   - Search for "Google Calendar API"
   - Click on it and press **Enable**

## Step 2: Create Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - Choose **External** user type
   - Fill in the required app information
   - Add your email to test users
4. For Application type, choose **Desktop application**
5. Give it a name (e.g., "Calendar Agent")
6. Click **Create**

## Step 3: Download and Install Credentials

1. Download the credentials file (it will be named something like `client_secret_xxx.json`)
2. Rename it to `credentials.json`
3. Move it to the `backend/credentials/` directory

```bash
# Example - adjust the path to your downloaded file
mv ~/Downloads/client_secret_xxx.json backend/credentials/credentials.json
```

## Step 4: Install Dependencies

Make sure you have the required Python packages:

```bash
cd backend
pip install -r requirements.txt
```

## Step 5: First Time Authentication

1. Start the backend server:
```bash
cd backend
python main.py
```

2. The first time the Calendar Agent initializes, it will:
   - Open a browser window for Google OAuth authentication
   - Ask you to sign in to your Google account
   - Request permission to access your calendar
   - Save the authentication token for future use

3. Grant the requested permissions

## Step 6: Verify Setup

You can verify the setup by:

1. Checking the health endpoint:
```bash
curl http://localhost:8000/api/health
```

2. Checking the calendar agent status:
```bash
curl http://localhost:8000/api/calendar/status
```

3. Testing event creation through the chat interface or API

## How It Works

### Integration with Stephie

The Calendar Agent integrates seamlessly with your scheduling assistant (Stephie). When users mention calendar-related keywords in their messages, Stephie automatically delegates to the Calendar Agent:

**Calendar Keywords Detected:**
- "schedule", "add to calendar", "create event", "book", "appointment"
- "meeting", "add event", "calendar", "remind me", "set reminder"
- "plan", "organize", "camp registration", "enroll", "sign up for"
- And many more...

### Example Usage

**User:** "Can you add the summer camp session to my calendar? It's from July 15-19, 9 AM to 3 PM daily at Columbus Community Center."

**Stephie responds:** "I'll add that camp session to your calendar right away..."

**Calendar Agent:** Creates the appropriate calendar events with camp details.

## API Endpoints

### Chat Interface
- `POST /api/chat` - Send messages to Stephie (automatically delegates calendar requests)

### Direct Calendar API
- `POST /api/calendar/add-event` - Add events directly
- `GET /api/calendar/status` - Check calendar agent status

### Example Direct API Call
```bash
curl -X POST http://localhost:8000/api/calendar/add-event \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Summer Camp Session",
    "start_datetime": "2024-07-15 09:00:00",
    "end_datetime": "2024-07-15 15:00:00",
    "description": "Daily summer camp activities",
    "location": "Columbus Community Center"
  }'
```

## Configuration Options

### Timezone Settings
The Calendar Agent defaults to `America/New_York` timezone. You can modify this in the `calendar_agent.py` file if needed.

### Calendar Selection
By default, events are added to your primary calendar. You can modify the `calendarId` parameter in the `_create_calendar_event` method to use a different calendar.

## Troubleshooting

### Common Issues

1. **"No credentials.json found"**
   - Make sure you've downloaded and placed the credentials file in `backend/credentials/credentials.json`

2. **"Authentication failed"**
   - Delete the `backend/credentials/token.pickle` file and restart the server to re-authenticate

3. **"Google Calendar API error"**
   - Ensure the Google Calendar API is enabled in your Google Cloud Console
   - Check that your OAuth consent screen is properly configured

4. **"Calendar agent not available"**
   - Check the server logs for initialization errors
   - Ensure all required dependencies are installed

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Checking Logs

The Calendar Agent logs important information about:
- Authentication status
- Event creation attempts
- API errors
- Delegation from Stephie

## Security Notes

1. **Keep credentials secure**: Never commit `credentials.json` or `token.pickle` to version control
2. **Scope limitation**: The agent only requests calendar write permissions
3. **Token refresh**: Authentication tokens are automatically refreshed as needed
4. **Local storage**: Credentials are stored locally in the `backend/credentials/` directory

## File Structure

```
backend/
├── credentials/
│   ├── credentials.json    # OAuth client credentials (you provide)
│   └── token.pickle       # Authentication token (auto-generated)
├── calendar_agent.py      # Calendar Agent implementation
├── main.py               # FastAPI server with calendar integration
└── requirements.txt      # Python dependencies
```

## Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review the server logs for error messages
3. Ensure all setup steps were completed correctly
4. Test with a simple calendar event first

The Calendar Agent is designed to work seamlessly with your existing scheduling assistant, making it easy for users to add events to their calendar through natural conversation with Stephie. 