import React, { useState } from 'react';
import { useChat } from '../context/ChatContext';
import { useStreaming } from '../hooks/useStreaming';

const ChatInput = () => {
  const [input, setInput] = useState('');
  const { messages, addMessage, isStreaming, setIsStreaming, setSources } = useChat();
  const { startStream } = useStreaming();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    
    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };
    addMessage(userMessage);
    setInput('');
    
    setIsStreaming(true);
    
    startStream(input, messages, true, (finalText) => {
      addMessage({
        role: 'assistant',
        content: finalText,
        timestamp: new Date().toISOString(),
      });
      setIsStreaming(false);
    });
  };
  
  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message..."
        disabled={isStreaming}
      />
      <button type="submit" disabled={!input.trim() || isStreaming}>
        Send
      </button>
    </form>
  );
};

export default ChatInput;
