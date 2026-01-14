import { useState } from 'react';
import { uploadFile } from '../services/api';

export const useFileUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  
  const upload = async (file) => {
    setUploading(true);
    setProgress(0);
    setError(null);
    
    try {
      const result = await uploadFile(file, setProgress);
      setUploading(false);
      return result;
    } catch (err) {
      setError(err.message);
      setUploading(false);
      throw err;
    }
  };
  
  return { upload, uploading, progress, error };
};
