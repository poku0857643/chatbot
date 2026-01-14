import React, { createContext, useState, useContext } from 'react';

const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [sources, setSources] = useState([]);
  
  const addMessage = (message) => {
    setMessages(prev => [...prev, message]);
  };
  
  const clearMessages = () => {
    setMessages([]);
  };
  
  return (
    <ChatContext.Provider value={{
      messages,
      addMessage,
      clearMessages,
      isStreaming,
      setIsStreaming,
      uploadedFiles,
      setUploadedFiles,
      sources,
      setSources,
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within ChatProvider');
  }
  return context;
};
