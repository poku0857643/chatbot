import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadFile = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      onProgress?.(progress);
    },
  });
  
  return response.data;
};

export const sendMessage = async (message, conversationHistory, useRAG = true) => {
  const response = await apiClient.post('/chat', {
    message,
    conversation_history: conversationHistory,
    use_rag: useRAG,
  });
  
  return response.data;
};

export default apiClient;
