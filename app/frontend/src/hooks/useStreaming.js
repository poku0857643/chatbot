import { useState, useCallback, useRef } from 'react';
import { createSSEConnection } from '../services/sse';

export const useStreaming = () => {
  const [streamingText, setStreamingText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [sources, setSources] = useState([]);
  const streamingTextRef = useRef('');

  const startStream = useCallback((message, conversationHistory, useRAG, onComplete) => {
    setStreamingText('');
    streamingTextRef.current = '';
    setIsStreaming(true);
    setError(null);
    setSources([]);

    createSSEConnection(
      message,
      conversationHistory,
      useRAG,
      (text) => {
        streamingTextRef.current += text;
        setStreamingText(streamingTextRef.current);
      },
      (sourcesData) => {
        setSources(sourcesData);
      },
      (err) => {
        setError(err);
        setIsStreaming(false);
      },
      () => {
        setIsStreaming(false);
        onComplete?.(streamingTextRef.current);
      }
    );
  }, []);

  return { streamingText, isStreaming, error, sources, startStream };
};
