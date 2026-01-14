import React from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import FileUpload from './FileUpload';

const ChatInterface = () => {
  return (
    <div className="chat-interface">
      <header className="chat-header">
        <h1>RAG Chatbot</h1>
        <FileUpload />
      </header>
      
      <MessageList />
      
      <ChatInput />
    </div>
  );
};

export default ChatInterface;
