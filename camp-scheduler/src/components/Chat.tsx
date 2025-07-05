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
      text: "Hello! I'm your scheduling assistant. I'm here to help you with your calendar and scheduling needs for this summer. What can I assist you with today?",
      sender: 'assistant',
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [contextId, setContextId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '' || isLoading) return;

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

      const assistantResponse: Message = {
        id: messages.length + 2,
        text: data.response,
        sender: 'assistant',
        timestamp: new Date(data.timestamp),
      };

      setMessages(prev => [...prev, assistantResponse]);
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
        <h3>💬 Calendar Assistant</h3>
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
        {isLoading && (
          <div className="chat-message assistant-message">
            <div className="message-content">
              <div className="message-text">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
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
            placeholder="Ask me about your calendar events, scheduling, or anything else..."
            rows={2}
          />
          <button
            className="chat-send-button"
            onClick={handleSendMessage}
            disabled={inputMessage.trim() === '' || isLoading}
          >
            {isLoading ? (
              <div className="loading-spinner">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12a9 9 0 11-6.219-8.56"/>
                </svg>
              </div>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22,2 15,22 11,13 2,9"></polygon>
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat; 