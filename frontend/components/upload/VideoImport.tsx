"use client";

import React, { useState } from 'react';
import { toast } from 'sonner';

type VideoImportProps = {
  onImportStart?: () => void;
  onImportSuccess?: (videoData: any) => void;
  onImportError?: (error: string) => void;
};

export default function VideoImport({
  onImportStart,
  onImportSuccess,
  onImportError
}: VideoImportProps) {
  const [url, setUrl] = useState('');

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

    onImportStart?.();

    try {
      // Pass the URL to the parent component to handle the actual import
      onImportSuccess?.({ url });
      setUrl('');
    } catch (error) {
      const errorMessage = 'Failed to import video. Please check the URL and try again.';
      toast.error(errorMessage);
      onImportError?.(errorMessage);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
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
        />
      </div>


      <button
        className={`btn-primary px-6 py-3 rounded-lg font-semibold ${
          !url.trim() ? 'opacity-60 cursor-not-allowed' : ''
        }`}
        onClick={handleImport}
        disabled={!url.trim()}
      >
        Import Video
      </button>
    </div>
  );
}
