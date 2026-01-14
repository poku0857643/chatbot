import React from 'react';
import ReactMarkdown from 'react-markdown';
import { useStreaming } from '../hooks/useStreaming';

const StreamingMessage = () => {
  const { streamingText, sources } = useStreaming();

  return (
    <div className="message message-assistant streaming">
      <div className="message-header">
        <span className="message-role">AI</span>
        <span className="typing-indicator">●●●</span>
      </div>
      <div className="message-content">
        <ReactMarkdown>{streamingText}</ReactMarkdown>
        <span className="cursor">|</span>
      </div>
      {sources && sources.length > 0 && (
        <div className="message-sources">
          <small>Sources: {sources.join(', ')}</small>
        </div>
      )}
    </div>
  );
};

export default StreamingMessage;
