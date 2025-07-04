import './App.css'
import { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import GoogleSignIn from './components/GoogleSignIn';
import Chat from './components/Chat';
import { OAUTH_CONFIG } from './config/oauth';

function App() {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [calendarEvents, setCalendarEvents] = useState<any[]>([]);
  const [isLoadingCalendar, setIsLoadingCalendar] = useState(false);
  const [calendarError, setCalendarError] = useState<string | null>(null);

  const handleSignIn = (accessToken: string, userEmail: string) => {
    console.log('Received access token and user email from Google Sign-In');
    console.log('User email:', userEmail);
    
    // Store the access token and user email
    setAccessToken(accessToken);
    setUserEmail(userEmail);
    
    console.log('Access token and user email stored');
  };

  const handleSignOut = () => {
    setAccessToken(null);
    setUserEmail(null);
    setCalendarEvents([]);
    setCalendarError(null);
  };

  // Load calendar events using OAuth token
  const loadCalendarEvents = async (token: string) => {
    setIsLoadingCalendar(true);
    setCalendarError(null);
    
    try {
      const response = await fetch(
        `${OAUTH_CONFIG.CALENDAR_ENDPOINT}/calendars/primary/events?` +
        `timeMin=${new Date().toISOString()}&` +
        `maxResults=100&` +
        `singleEvents=true&` +
        `orderBy=startTime`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Convert Google Calendar events to FullCalendar format
      const events = data.items?.map((event: any) => ({
        id: event.id,
        title: event.summary || 'No Title',
        start: event.start?.dateTime || event.start?.date,
        end: event.end?.dateTime || event.end?.date,
        url: event.htmlLink,
        description: event.description,
        location: event.location,
        allDay: !event.start?.dateTime, // If no time, it's an all-day event
      })) || [];

      setCalendarEvents(events);
      console.log('Calendar events loaded:', events.length);
    } catch (error) {
      console.error('Error loading calendar events:', error);
      setCalendarError('Failed to load calendar events. Please try signing in again.');
    } finally {
      setIsLoadingCalendar(false);
    }
  };

  // Load calendar when access token changes
  useEffect(() => {
    if (accessToken) {
      loadCalendarEvents(accessToken);
    }
  }, [accessToken]);

  return (
    <div>
      <h1 className="main-title">Peppy Calendar</h1>
      
      {!accessToken ? (
        <div className="signin-container">
          <GoogleSignIn onSignIn={handleSignIn} onSignOut={handleSignOut} />
        </div>
      ) : (
        <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
          <GoogleSignIn onSignIn={handleSignIn} onSignOut={handleSignOut} />
        </div>
      )}
      
      {accessToken && userEmail ? (
        <div>
          <h2 className="welcome-message">Welcome, {userEmail}!</h2>
          
          {calendarError && (
            <div className="error-message">
              {calendarError}
              <button 
                onClick={() => loadCalendarEvents(accessToken)}
                style={{ marginLeft: '10px', padding: '5px 10px' }}
              >
                Retry
              </button>
            </div>
          )}
          
          {isLoadingCalendar && (
            <div className="loading-message">
              Loading calendar events...
            </div>
          )}
          
          <div className="main-content">
            <div className="calendar-section">
              <div className="calendar-container">
                <FullCalendar
                  plugins={[dayGridPlugin]}
                  initialView="dayGridMonth"
                  events={calendarEvents}
                  height={600}
                  fixedWeekCount={false}
                  showNonCurrentDates={false}
                  eventDidMount={(info) => {
                    console.log('Event loaded:', info.event.title);
                  }}
                  eventClick={(info) => {
                    if (info.event.url) {
                      window.open(info.event.url, '_blank');
                      info.jsEvent.preventDefault();
                    }
                  }}
                  headerToolbar={{
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth'
                  }}
                  titleFormat={{ 
                    year: 'numeric', 
                    month: 'long' 
                  }}
                  eventContent={(eventInfo) => {
                    return (
                      <div style={{ padding: '2px 4px', fontSize: '12px' }}>
                        <div style={{ fontWeight: 'bold' }}>{eventInfo.event.title}</div>
                        {eventInfo.event.extendedProps.location && (
                          <div style={{ fontSize: '10px', opacity: 0.7 }}>
                            📍 {eventInfo.event.extendedProps.location}
                          </div>
                        )}
                      </div>
                    );
                  }}
                />
              </div>
            </div>
            
            <div className="chat-section">
              <Chat userEmail={userEmail} />
            </div>
          </div>
        </div>
      ) : (
        <div className="signin-container">
          <p>Please sign in with your Google account to view your calendar.</p>
        </div>
      )}
    </div>
  );
}

export default App;
