"use client";

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
  const isCompleted = useUploadStore((state) => state.isCompleted);
  const fileName = useUploadStore((state) => state.fileName);
  const setUploading = useUploadStore((state) => state.setUploading);

  // Debug logs removed

  // If not uploading, not completed, and not persisting, render nothing
  if (!isUploading && !isCompleted && !persist) {
    return null;
  }

  const handleCancel = () => {
    // Abort the in-flight upload via the store (this calls abort on the stored AbortController
    // and resets upload state). Keep optional onCancel callback for any extra UI logic.
    useUploadStore.getState().cancelUpload();

    if (onCancel) {
      try {
        onCancel();
      } catch {
        // swallow errors from callback
      }
    }
  };

  const percent = Math.max(0, Math.min(100, Math.round(progress)));
  const displayName = fileName || "Uploading file";

  return (
    <div
      className="form-input p-6 rounded-2xl"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{displayName}</h3>
        <span className="text-sm text-gray-300 flex items-center gap-2">
          {percent}%
          {isCompleted && (
            <svg
              className="w-4 h-4 text-green-500"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-label="Upload completed"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.707a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414L9 13.414l4.707-4.707z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </span>
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
          <span className="text-sm text-gray-300">
            Upload {isCompleted ? "completed" : "in progress"}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3"></div>
          {!isCompleted && (
            <button
              type="button"
              onClick={handleCancel}
              title="Cancel upload"
              className="btn-danger px-3 py-1 text-sm rounded"
              aria-label="Cancel upload"
            >
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
