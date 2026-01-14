import React from 'react';
import ReactMarkdown from 'react-markdown';

const Message = ({ message }) => {
  const { role, content, timestamp } = message;

  return (
    <div className={`message message-${role}`}>
      <div className="message-header">
        <span className="message-role">{role === 'user' ? 'You' : 'AI'}</span>
        {timestamp && <span className="message-time">{new Date(timestamp).toLocaleTimeString()}</span>}
      </div>
      <div className="message-content">
        {role === 'assistant' ? (
          <ReactMarkdown>{content}</ReactMarkdown>
        ) : (
          content
        )}
      </div>
    </div>
  );
};

export default Message;
