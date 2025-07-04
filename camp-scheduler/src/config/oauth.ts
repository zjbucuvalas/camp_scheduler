// OAuth Configuration
export const OAUTH_CONFIG = {
  // Replace this with your actual Google OAuth Client ID
  // You can get this from https://console.cloud.google.com/
  CLIENT_ID: import.meta.env.VITE_GOOGLE_CLIENT_ID || '738750706924-71cdt9ni5g382tumqojhbov6paq5jgpq.apps.googleusercontent.com',
  
  // OAuth scopes required for the application
  SCOPES: [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/userinfo.email'
  ],
  
  // OAuth endpoints
  OAUTH_ENDPOINT: 'https://accounts.google.com/o/oauth2/v2/auth',
  USERINFO_ENDPOINT: 'https://www.googleapis.com/oauth2/v2/userinfo',
  CALENDAR_ENDPOINT: 'https://www.googleapis.com/calendar/v3'
};

// Helper function to build OAuth URL
export const buildOAuthUrl = (redirectUri: string): string => {
  const params = new URLSearchParams({
    client_id: OAUTH_CONFIG.CLIENT_ID,
    redirect_uri: redirectUri,
    scope: OAUTH_CONFIG.SCOPES.join(' '),
    response_type: 'token',
    prompt: 'consent'
  });
  
  return `${OAUTH_CONFIG.OAUTH_ENDPOINT}?${params.toString()}`;
}; 