export const createSSEConnection = (message, conversationHistory, useRAG, onMessage, onSources, onError, onComplete) => {
  const API_URL = import.meta.env.VITE_API_URL;
  
  const payload = {
    message,
    conversation_history: conversationHistory,
    use_rag: useRAG
  };
  
  fetch(`${API_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  }).then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    function read() {
      reader.read().then(({ done, value }) => {
        if (done) {
          onComplete?.();
          return;
        }
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        lines.forEach(line => {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.text) {
                onMessage?.(data.text);
              } else if (data.sources) {
                onSources?.(data.sources);
              } else if (data.done) {
                onComplete?.();
                return;
              } else if (data.error) {
                onError?.(data.error);
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        });
        
        read();
      });
    }
    
    read();
  }).catch(error => {
    onError?.(error.message);
  });
};
