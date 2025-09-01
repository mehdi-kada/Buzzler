"use client";

import React, { useState } from 'react';
import { toast } from 'sonner';
import api from '@/lib/axios/auth_interceptor';
import { VideoProgressUpdate } from '@/types/video_validation';

type VideoImportProps = {
  onImportStart?: (taskId: string) => void;
  onImportSuccess?: (videoData: any) => void;
  onImportError?: (error: string) => void;
};

export default function VideoImport({
  onImportStart,
  onImportSuccess,
  onImportError
}: VideoImportProps) {
  const [url, setUrl] = useState('');
  const [isImporting, setIsImporting] = useState(false);

  const handleImport = async () => {
    if (!url.trim()) {
      toast.error('Please enter a valid URL');
      return;
    }

    // Basic URL validation
    try {
      new URL(url);
    } catch {
      toast.error('Please enter a valid URL');
      return;
    }

    setIsImporting(true);
    
    try {
      // Call the backend API to start the import process
      const response = await api.post('/import/import-video', {
        url: url,
        custom_file_name: null,
      });

      const { task_id, status, message } = response.data;
      
      // Notify parent component that import has started
      onImportStart?.(task_id);
      
      toast.success(message || 'Video import started successfully!');
    } catch (error: any) {
      let errorMessage = 'Failed to import video. Please check the URL and try again.';
      
      // Handle different error response formats
      if (error?.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (typeof detail === 'object') {
          if (detail.msg) {
            errorMessage = detail.msg;
          } else if (Array.isArray(detail)) {
            errorMessage = detail.map((error: any) => 
              error.msg || JSON.stringify(error)
            ).join(', ');
          } else {
            errorMessage = JSON.stringify(detail);
          }
        }
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      toast.error(errorMessage);
      onImportError?.(errorMessage);
    } finally {
      setIsImporting(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isImporting) {
      handleImport();
    }
  };

  return (
    <div className="form-input p-6 rounded-2xl">
      <h3 className="text-xl font-semibold mb-4">Import from URL</h3>

      <div className="mb-6">
        <input
          type="url"
          className="form-input w-full px-4 py-3 rounded-lg"
          placeholder="https://youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isImporting}
        />
      </div>

      <button
        className={`btn-primary px-6 py-3 rounded-lg font-semibold ${
          isImporting || !url.trim() ? 'opacity-60 cursor-not-allowed' : ''
        }`}
        onClick={handleImport}
        disabled={isImporting || !url.trim()}
      >
        {isImporting ? 'Importing...' : 'Import Video'}
      </button>
    </div>
  );
}
