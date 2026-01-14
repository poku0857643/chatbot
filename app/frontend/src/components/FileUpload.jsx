import React, { useRef } from 'react';
import { useChat } from '../context/ChatContext';
import { useFileUpload } from '../hooks/useFileUpload';

const FileUpload = () => {
  const fileInputRef = useRef(null);
  const { uploadedFiles, setUploadedFiles } = useChat();
  const { upload, uploading, progress, error } = useFileUpload();
  
  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    try {
      const result = await upload(file);
      setUploadedFiles(prev => [...prev, result]);
      fileInputRef.current.value = '';
      alert(`File uploaded successfully! Created ${result.chunks_created} chunks.`);
    } catch (err) {
      console.error('Upload failed:', err);
      alert(`Upload failed: ${error || err.message}`);
    }
  };
  
  return (
    <div className="file-upload">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt,.docx"
        onChange={handleFileSelect}
        disabled={uploading}
        style={{ display: 'none' }}
      />
      
      <button
        onClick={() => fileInputRef.current.click()}
        disabled={uploading}
        className="upload-button"
      >
        {uploading ? `Uploading... ${progress}%` : '📁 Upload Document'}
      </button>
      
      {uploadedFiles.length > 0 && (
        <div className="uploaded-files-count">
          ({uploadedFiles.length} file{uploadedFiles.length !== 1 ? 's' : ''})
        </div>
      )}
    </div>
  );
};

export default FileUpload;
