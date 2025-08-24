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
    onImportStart?.();

    try {
      // TODO: Replace with actual API call
      // const response = await importVideoFromUrl(url);

      // Simulate API call for now
      await new Promise(resolve => setTimeout(resolve, 2000));

      toast.success('Video imported successfully!');
      onImportSuccess?.({ url });
      setUrl('');
    } catch (error) {
      const errorMessage = 'Failed to import video. Please check the URL and try again.';
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

      {/* Supported Platforms */}
      <div className="mb-6">
        <p className="text-sm text-gray-300 mb-3">Supported platforms:</p>
        <div className="grid grid-cols-4 gap-3">
          <div className="platform-icon p-3 rounded-lg text-center">
            <span className="text-red-500 text-2xl">📺</span>
            <p className="text-xs mt-1">YouTube</p>
          </div>
          <div className="platform-icon p-3 rounded-lg text-center">
            <span className="text-blue-500 text-2xl">🎵</span>
            <p className="text-xs mt-1">Vimeo</p>
          </div>
          <div className="platform-icon p-3 rounded-lg text-center">
            <span className="text-purple-500 text-2xl">🎮</span>
            <p className="text-xs mt-1">Twitch</p>
          </div>
          <div className="platform-icon p-3 rounded-lg text-center">
            <span className="text-blue-600 text-2xl">👥</span>
            <p className="text-xs mt-1">Facebook</p>
          </div>
        </div>
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
