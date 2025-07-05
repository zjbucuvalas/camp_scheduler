import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

interface ChatProps {
  userEmail?: string;
}

// Component to render message content with markdown support
const MessageDisplay: React.FC<{ message: Message }> = ({ message }) => {
  // Check if the message contains markdown indicators
  const hasMarkdown = (text: string): boolean => {
    return /^#|^\*|^-|\*\*|__|`|```|\[.*\]\(.*\)/.test(text.trim()) || 
           text.includes('\n# ') || text.includes('\n## ') || text.includes('\n### ') ||
           text.includes('\n- ') || text.includes('\n* ') || text.includes('\n1. ');
  };

  // For assistant messages, check if it contains markdown and render accordingly
  if (message.sender === 'assistant' && hasMarkdown(message.text)) {
    return (
      <div className="message-text markdown-content">
        <ReactMarkdown
          components={{
            h1: ({ children }) => <h1 className="markdown-h1">{children}</h1>,
            h2: ({ children }) => <h2 className="markdown-h2">{children}</h2>,
            h3: ({ children }) => <h3 className="markdown-h3">{children}</h3>,
            ul: ({ children }) => <ul className="markdown-ul">{children}</ul>,
            ol: ({ children }) => <ol className="markdown-ol">{children}</ol>,
            li: ({ children }) => <li className="markdown-li">{children}</li>,
            strong: ({ children }) => <strong className="markdown-strong">{children}</strong>,
            em: ({ children }) => <em className="markdown-em">{children}</em>,
            code: ({ children }) => <code className="markdown-code">{children}</code>,
            p: ({ children }) => <p className="markdown-p">{children}</p>,
            blockquote: ({ children }) => <blockquote className="markdown-blockquote">{children}</blockquote>,
          }}
        >
          {message.text}
        </ReactMarkdown>
      </div>
    );
  }

  // For user messages or plain text assistant messages
  return <div className="message-text">{message.text}</div>;
};

const Chat: React.FC<ChatProps> = ({ userEmail }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hi there! I'm Stephie, your family concierge. I'm here to help you with your calendar, scheduling, and summer planning needs. What can I assist you with today?",
      sender: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [contextId, setContextId] = useState<string | null>(null);
  const [isAuthenticatingCalendar, setIsAuthenticatingCalendar] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to handle calendar OAuth authorization
  const handleCalendarAuth = async (authUrl: string, originalMessage: string) => {
    try {
      setIsAuthenticatingCalendar(true);
      
      // Add a message to show we're handling authorization
      const authMessage: Message = {
        id: messages.length + 10,
        text: "🔐 I'll handle the calendar authorization for you automatically...",
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, authMessage]);

      // Open OAuth in a popup window
      const popup = window.open(
        authUrl,
        'calendar-auth',
        'width=500,height=600,scrollbars=yes,resizable=yes'
      );

      // Listen for the OAuth callback
      const checkClosed = setInterval(() => {
        if (popup?.closed) {
          clearInterval(checkClosed);
          // Check if we got the authorization code from the popup
          const urlParams = new URLSearchParams(popup?.location?.search || '');
          const authCode = urlParams.get('code');
          
          if (authCode) {
            handleOAuthCallback(authCode, originalMessage);
          } else {
            setIsAuthenticatingCalendar(false);
            const errorMessage: Message = {
              id: messages.length + 11,
              text: "❌ Calendar authorization was cancelled or failed. Please try your calendar request again.",
              sender: 'assistant',
              timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMessage]);
          }
        }
      }, 1000);

      // Handle message from popup (if using postMessage)
      const handleMessage = (event: MessageEvent) => {
        if (event.origin !== window.location.origin) return;
        
        if (event.data.type === 'OAUTH_SUCCESS' && event.data.source === 'calendar_auth') {
          popup?.close();
          clearInterval(checkClosed);
          handleOAuthSuccess(originalMessage);
          window.removeEventListener('message', handleMessage);
        } else if (event.data.type === 'OAUTH_ERROR') {
          popup?.close();
          clearInterval(checkClosed);
          setIsAuthenticatingCalendar(false);
          const errorMessage: Message = {
            id: messages.length + 11,
            text: "❌ Calendar authorization failed. Please try your calendar request again.",
            sender: 'assistant',
            timestamp: new Date(),
          };
          setMessages(prev => [...prev, errorMessage]);
          window.removeEventListener('message', handleMessage);
        }
      };

      window.addEventListener('message', handleMessage);

    } catch (error) {
      console.error('Error handling calendar auth:', error);
      setIsAuthenticatingCalendar(false);
      const errorMessage: Message = {
        id: messages.length + 11,
        text: "❌ Error with calendar authorization. Please try again.",
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Function to handle OAuth callback
  const handleOAuthCallback = async (authCode: string, originalMessage: string) => {
    try {
      // Send the authorization code to the backend
      const response = await fetch('http://localhost:8000/api/calendar/oauth-callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: authCode }),
      });

      if (response.ok) {
        const successMessage: Message = {
          id: messages.length + 12,
          text: "✅ Calendar access authorized successfully! Let me process your calendar request now...",
          sender: 'assistant',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, successMessage]);

        // Retry the original calendar request
        setTimeout(() => {
          retryCalendarRequest(originalMessage);
        }, 1000);
      } else {
        throw new Error('OAuth callback failed');
      }
    } catch (error) {
      console.error('Error in OAuth callback:', error);
      const errorMessage: Message = {
        id: messages.length + 12,
        text: "❌ Failed to complete calendar authorization. Please try your request again.",
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsAuthenticatingCalendar(false);
    }
  };

  // Function to handle OAuth success (when OAuth completes server-side)
  const handleOAuthSuccess = async (originalMessage: string) => {
    try {
      const successMessage: Message = {
        id: messages.length + 12,
        text: "✅ Calendar access authorized successfully! Let me process your calendar request now...",
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, successMessage]);

      // Retry the original calendar request
      setTimeout(() => {
        retryCalendarRequest(originalMessage);
      }, 1000);
    } catch (error) {
      console.error('Error in OAuth success handler:', error);
      const errorMessage: Message = {
        id: messages.length + 12,
        text: "❌ Failed to complete calendar authorization. Please try your request again.",
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsAuthenticatingCalendar(false);
    }
  };

  // Function to retry the original calendar request after authorization
  const retryCalendarRequest = async (originalMessage: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: originalMessage,
          user_email: userEmail,
          context_id: contextId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantResponse: Message = {
          id: messages.length + 13,
          text: data.response,
          sender: 'assistant',
          timestamp: new Date(data.timestamp),
        };
        setMessages(prev => [...prev, assistantResponse]);
      }
    } catch (error) {
      console.error('Error retrying calendar request:', error);
      const errorMessage: Message = {
        id: messages.length + 13,
        text: "❌ Error processing your calendar request. Please try again.",
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '' || isLoading || isAuthenticatingCalendar) return;

    const newMessage: Message = {
      id: messages.length + 1,
      text: inputMessage,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newMessage]);
    const currentInput = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      // Call the backend API
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentInput,
          user_email: userEmail,
          context_id: contextId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Update context ID for conversation continuity
      if (data.context_id) {
        setContextId(data.context_id);
      }

      // Check if the response contains an OAuth URL for calendar authorization
      const responseText = data.response;
      const oauthUrlMatch = responseText.match(/https:\/\/accounts\.google\.com\/o\/oauth2\/auth\?[^\s\n]+/);
      
      if (oauthUrlMatch && responseText.includes('calendar')) {
        // Handle OAuth automatically instead of showing the URL to the user
        const authUrl = oauthUrlMatch[0];
        handleCalendarAuth(authUrl, currentInput);
        
        // Show a user-friendly message instead of the OAuth URL
        const assistantResponse: Message = {
          id: messages.length + 2,
          text: "I can help you add that to your calendar! Let me just get permission to access your Google Calendar first...",
          sender: 'assistant',
          timestamp: new Date(data.timestamp),
        };
        setMessages(prev => [...prev, assistantResponse]);
      } else {
        // Normal response handling
        const assistantResponse: Message = {
          id: messages.length + 2,
          text: responseText,
          sender: 'assistant',
          timestamp: new Date(data.timestamp),
        };
        setMessages(prev => [...prev, assistantResponse]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: messages.length + 2,
        text: "I apologize, but I'm having trouble connecting to the scheduling assistant right now. Please make sure the backend server is running and try again.",
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div>
          <h3>💬 Stephie</h3>
          <div className="chat-subtitle">your family concierge</div>
        </div>
        {userEmail && (
          <div className="chat-user-info">
            Chatting as {userEmail.split('@')[0]}
          </div>
        )}
      </div>
      
      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`chat-message ${message.sender === 'user' ? 'user-message' : 'assistant-message'}`}
          >
            <div className="message-content">
              <MessageDisplay message={message} />
              <div className="message-time">{formatTime(message.timestamp)}</div>
            </div>
          </div>
        ))}
        {(isLoading || isAuthenticatingCalendar) && (
          <div className="chat-message assistant-message">
            <div className="message-content">
              <div className="message-text">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                {isAuthenticatingCalendar && (
                  <div style={{ marginTop: '8px', fontSize: '0.9em', opacity: 0.8 }}>
                    Authorizing calendar access...
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <textarea
            className="chat-input"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about family scheduling, summer camps, or calendar planning..."
            rows={2}
            disabled={isAuthenticatingCalendar}
          />
          <button
            className="chat-send-button"
            onClick={handleSendMessage}
            disabled={inputMessage.trim() === '' || isLoading || isAuthenticatingCalendar}
          >
            {isLoading || isAuthenticatingCalendar ? '...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat; 