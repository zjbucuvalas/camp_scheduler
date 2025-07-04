# Google Calendar OAuth Setup Guide

## Prerequisites

1. **Google Cloud Project**: You need a Google Cloud project with the Calendar API enabled
2. **OAuth Credentials**: You need OAuth 2.0 credentials (Client ID) for a web application

## Step 1: Google Cloud Console Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to **APIs & Services** → **Library**
   - Search for "Google Calendar API"
   - Click on it and press **Enable**

## Step 2: Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client IDs**
3. Choose **Web application** as the application type
4. Add your authorized redirect URIs:
   - For local development: `http://localhost:5173`
   - For production: `https://yourdomain.com`
5. Save and copy the **Client ID**

## Step 3: Configure Your Application

### Option 1: Environment Variables (Recommended)

Create a `.env.local` file in the project root:

```
VITE_GOOGLE_CLIENT_ID=your_actual_client_id_here
```

### Option 2: Direct Configuration

Edit `src/config/oauth.ts` and replace the fallback CLIENT_ID with your actual Client ID.

## Step 4: Run the Application

```bash
npm run dev
```

## Troubleshooting

### Common Issues:

1. **"OAuth error: access_denied"**
   - Check that your redirect URI is correctly configured in Google Cloud Console
   - Make sure your domain matches exactly (including http/https)

2. **"Calendar loading failed"**
   - Verify that the Calendar API is enabled in Google Cloud Console
   - Check that you have the correct OAuth scopes

3. **"Authentication failed"**
   - Make sure your Client ID is correct
   - Check browser console for detailed error messages

### Required OAuth Scopes:

- `https://www.googleapis.com/auth/calendar.readonly` - Read calendar events
- `https://www.googleapis.com/auth/userinfo.email` - Get user email address

## Security Notes

- Never commit your actual Client ID to version control if it's sensitive
- The Client ID used in this example is for demonstration purposes only
- For production, use environment variables or a secure configuration management system

## Features

- ✅ Google OAuth 2.0 authentication
- ✅ Calendar event fetching
- ✅ Token persistence (localStorage)
- ✅ Automatic token validation
- ✅ Error handling and retry logic
- ✅ Clean, modern UI 