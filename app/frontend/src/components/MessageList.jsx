import React, { useEffect, useRef } from 'react';
import { useChat } from '../context/ChatContext';
import Message from './Message';
import StreamingMessage from './StreamingMessage';

const MessageList = () => {
  const { messages, isStreaming } = useChat();
  const messagesEndRef = useRef(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);
  
  return (
    <div className="message-list">
      {messages.length === 0 && !isStreaming && (
        <div className="empty-state">
          <h2>Welcome to RAG Chatbot!</h2>
          <p>Upload a document to get started, or just ask me anything.</p>
        </div>
      )}
      
      {messages.map((msg, idx) => (
        <Message key={idx} message={msg} />
      ))}
      
      {isStreaming && <StreamingMessage />}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
