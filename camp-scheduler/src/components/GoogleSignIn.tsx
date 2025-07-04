import React, { useEffect, useState } from 'react';
import { OAUTH_CONFIG, buildOAuthUrl } from '../config/oauth';

interface GoogleSignInProps {
  onSignIn: (accessToken: string, userEmail: string) => void;
  onSignOut: () => void;
}

const GoogleSignIn: React.FC<GoogleSignInProps> = ({ onSignIn, onSignOut }) => {
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleSignIn = () => {
    console.log('Attempting to sign in...');
    setError(null);
    
    // Use the configuration to build OAuth URL
    const authUrl = buildOAuthUrl(window.location.origin);
    
    console.log('Redirecting to OAuth flow...');
    window.location.href = authUrl;
  };

  const handleSignOut = () => {
    console.log('Signing out...');
    setIsSignedIn(false);
    onSignOut();
    
    // Clear any stored tokens
    localStorage.removeItem('google_access_token');
    localStorage.removeItem('google_user_email');
  };

  // Check for OAuth callback and stored tokens
  useEffect(() => {
    const checkAuthState = async () => {
      try {
        // First, check if we have stored tokens
        const storedToken = localStorage.getItem('google_access_token');
        const storedEmail = localStorage.getItem('google_user_email');
        
        if (storedToken && storedEmail) {
          console.log('Found stored tokens, validating...');
          
          // Validate the stored token
          const response = await fetch(OAUTH_CONFIG.USERINFO_ENDPOINT, {
            headers: {
              'Authorization': `Bearer ${storedToken}`
            }
          });
          
          if (response.ok) {
            const userInfo = await response.json();
            console.log('Stored token is valid, signing in...');
            setIsSignedIn(true);
            onSignIn(storedToken, userInfo.email);
            setIsLoading(false);
            return;
          } else {
            console.log('Stored token is invalid, clearing...');
            localStorage.removeItem('google_access_token');
            localStorage.removeItem('google_user_email');
          }
        }
        
        // Check for OAuth callback in URL
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        const accessToken = hashParams.get('access_token');
        const error = hashParams.get('error');
        
        if (error) {
          console.error('OAuth error:', error);
          setError(`OAuth error: ${error}`);
          setIsLoading(false);
          return;
        }
        
        if (accessToken) {
          console.log('OAuth callback detected, getting user info...');
          
          // Get user email from Google's userinfo endpoint
          const response = await fetch(OAUTH_CONFIG.USERINFO_ENDPOINT, {
            headers: {
              'Authorization': `Bearer ${accessToken}`
            }
          });
          
          if (response.ok) {
            const userInfo = await response.json();
            console.log('User info retrieved successfully');
            
            // Store tokens for future use
            localStorage.setItem('google_access_token', accessToken);
            localStorage.setItem('google_user_email', userInfo.email);
            
            setIsSignedIn(true);
            onSignIn(accessToken, userInfo.email);
            
            // Clean up the URL
            window.history.replaceState({}, document.title, window.location.pathname);
          } else {
            throw new Error('Failed to get user information');
          }
        }
        
      } catch (error) {
        console.error('Error during auth check:', error);
        setError('Authentication failed. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthState();
  }, [onSignIn]);

  if (isLoading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <div style={{ padding: isSignedIn ? '0' : '20px', textAlign: 'center' }}>
      {error && (
        <div style={{ 
          color: 'red', 
          marginBottom: '15px', 
          padding: '10px', 
          border: '1px solid red', 
          borderRadius: '4px',
          backgroundColor: '#ffebee'
        }}>
          {error}
        </div>
      )}
      
      {!isSignedIn ? (
        <div>
          <h3>Google Calendar Access</h3>
          <p>Sign in with your Google account to view your calendar events.</p>
          <button 
            onClick={handleSignIn}
            style={{
              backgroundColor: '#4285f4',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: 'bold',
              boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
              transition: 'background-color 0.3s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#3367d6'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#4285f4'}
          >
            🔐 Sign in with Google
          </button>
        </div>
      ) : (
        <button 
          onClick={handleSignOut}
          style={{
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            color: 'white',
            border: '1px solid rgba(255, 255, 255, 0.4)',
            padding: '6px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.25s ease'
          }}
        >
          Sign Out
        </button>
      )}
    </div>
  );
};

export default GoogleSignIn; 