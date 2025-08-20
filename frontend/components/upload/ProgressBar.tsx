"use client";
import React from "react";
import { useUploadStore } from "../../lib/store/uploadStore";

type ProgressBarProps = {
  // optional callback when user cancels the upload
  onCancel?: () => void;
  // whether to show the component even when not uploading (defaults to false)
  persist?: boolean;
};

export default function ProgressBar({
  onCancel,
  persist = false,
}: ProgressBarProps) {
  const progress = useUploadStore((state) => state.progress);
  const isUploading = useUploadStore((state) => state.isUploading);
  const fileName = useUploadStore((state) => state.fileName);
  const setUploading = useUploadStore((state) => state.setUploading);

  // If not uploading and not persisting, render nothing
  if (!isUploading && !persist) {
    return null;
  }

  const handleCancel = () => {
    // signal to store that upload has stopped; this will also reset progress & file info
    setUploading(false);
    if (onCancel) {
      try {
        onCancel();
      } catch {
        // swallow errors from callback
      }
    }
  };

  const displayName = fileName || "Uploading file";

  return (
    <div className="form-input p-6 rounded-2xl" role="status" aria-live="polite">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{displayName}</h3>
        <span className="text-sm text-gray-300">{Math.max(0, Math.min(100, Math.round(progress)))}%</span>
      </div>
      
      <div className="progress-bar h-2 mb-4">
        <div 
          className="progress-fill" 
          style={{ width: `${progress}%` }}
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.max(0, Math.min(100, Math.round(progress)))}
          aria-label="File upload progress"
        ></div>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-center space-x-3">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span className="text-sm text-gray-300">Upload {isUploading ? "in progress" : "completed"}</span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
            <span className="text-sm text-gray-400">AI clip detection pending</span>
          </div>
          <button
            type="button"
            onClick={handleCancel}
            title="Cancel upload"
            className="btn-danger px-3 py-1 text-sm rounded"
            aria-label="Cancel upload"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
