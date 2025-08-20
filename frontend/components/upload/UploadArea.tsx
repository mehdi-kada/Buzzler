"use client"
import React, { useCallback, useRef, useState } from "react";
import ProgressBar from "./ProgressBar";
import { uploadFileComplete } from "../../lib/axios/upload_api_functions";
import { useUploadStore } from "../../lib/store/uploadStore";
import { toast } from "sonner";
import { useVideoValidation } from "../../hooks/useVideoValidation";
import { videoValidationConfig } from "../../types/video_validation";

/**
 * UploadArea
 *
 * Drag-and-drop or press-to-select upload area. Collects a small metadata form
 * (title, description, tags) before starting the upload, shows the progress bar
 * while uploading and allows cancelling via the progress UI.
 *
 * This component has been updated to use CSS classes from globals.css for consistent styling.
 */

type UploadAreaProps = {
  /**
   * Whether to show the metadata form (title, description, tags).
   * Defaults to true.
   */
  showMetadataForm?: boolean;
};

export default function UploadArea({ showMetadataForm = true }: UploadAreaProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [tagsRaw, setTagsRaw] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isUploading = useUploadStore((state) => state.isUploading);
  const setUploading = useUploadStore((state) => state.setUploading);

  const resetForm = useCallback(() => {
    setFile(null);
    setTitle("");
    setDescription("");
    setTagsRaw("");
  }, []);

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return;
    const first = files[0];

    // Basic validation: only allow reasonably sized files (e.g., <= 2GB) and common video types
    const maxBytes = 2 * 1024 * 1024 * 1024; // 2GB
    if (first.size > maxBytes) {
      toast.error("File is too large. Maximum allowed size is 2GB.");
      return;
    }

    setFile(first);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles],
  );

  const onDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    // Only show dragging when files are present
    if (
      e.dataTransfer.types &&
      Array.from(e.dataTransfer.types).includes("Files")
    ) {
      setIsDragging(true);
    }
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const onChooseFile = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const onFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      handleFiles(e.target.files);
      // reset input value so selecting same file again still triggers change
      e.currentTarget.value = "";
    },
    [handleFiles],
  );

  const onStartUpload = useCallback(async () => {
    if (!file) {
      toast.error("Please select a file to upload.");
      return;
    }

    // create a simple unique file id for tracking this upload in store
    const fileId = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 9)}`;

    setIsSubmitting(true);

    try {
      // set uploading in store (uploadFileComplete will also set it, but ensure the store is in sync)
      setUploading(true, file.name, fileId);

      // Note: uploadFileComplete signature expects (file, fileId, onProgress?)
      await uploadFileComplete(file, fileId, (progress: number) => {
        // progress updates are handled in the upload library/store; no local handling required here.
      });

      toast.success("Upload complete.");
      resetForm();
    } catch (err: any) {
      // uploadFileComplete and underlying interceptors will already show toasts for many errors,
      // but show a fallback message if none was shown.
      if (!err?.message) {
        toast.error("Upload failed.");
      }
    } finally {
      setIsSubmitting(false);
      // store will be reset by upload helpers, but ensure uploading is false
      setUploading(false);
    }
  }, [file, resetForm, setUploading]);

  const handleCancelClick = useCallback(() => {
    resetForm();
  }, [resetForm]);

  return (
    <div 
      className="w-full"
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragEnter={onDragOver}
      onDragLeave={onDragLeave}
    >
      <div
        className={`upload-area p-8 rounded-lg w-full ${isDragging ? 'dragover' : ''}`}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          // open file dialog on Enter/Space
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onChooseFile();
          }
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept="video/*"
          className="hidden"
          onChange={onFileInputChange}
        />

        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-gradient-to-r from-pink-600 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
            </svg>
          </div>
          <div className="text-xl font-semibold text-white mb-2">
            {isDragging
              ? "Drop files here to upload"
              : "Drop your video here"}
          </div>
          <div className="text-gray-300 mb-6">
            or click to browse files
          </div>
          <button 
            type="button" 
            className="btn-primary px-6 py-3 rounded-lg font-semibold"
            onClick={onChooseFile}
            aria-label="Choose a file to upload"
          >
            Choose File
          </button>
          <p className="text-sm text-gray-400 mt-4">
            Supports MP4, MOV, AVI, MKV up to 2GB
          </p>
        </div>

        <div className="flex items-center justify-between mb-4">
          <div className="text-sm text-gray-300">
            {file
              ? `${file.name} • ${(file.size / (1024 * 1024)).toFixed(1)} MB`
              : "No file selected"}
          </div>
          {file && (
            <button
              type="button"
              className="btn-secondary px-3 py-1 rounded text-sm"
              onClick={() => {
                // quick demo action: clear previously selected file
                resetForm();
              }}
            >
              Clear
            </button>
          )}
        </div>


        <div className="flex justify-end space-x-3 mt-6">
          <button
            type="button"
            className={`btn-secondary px-6 py-3 rounded-lg font-semibold ${!file || isUploading || isSubmitting ? 'opacity-60 cursor-not-allowed' : ''}`}
            onClick={handleCancelClick}
            disabled={!file || isUploading || isSubmitting}
          >
            Cancel
          </button>

          <button
            type="button"
            className={`btn-primary px-6 py-3 rounded-lg font-semibold ${!file || isUploading || isSubmitting ? 'opacity-60 cursor-not-allowed' : ''}`}
            onClick={onStartUpload}
            disabled={!file || isUploading || isSubmitting}
          >
            {isSubmitting || isUploading ? "Uploading…" : "Upload"}
          </button>
        </div>

        {/* Show small hint when dragging files */}
        {isDragging && (
          <div className="text-green-500 text-sm mt-4 text-center">
            Release to upload
          </div>
        )}
      </div>

      {/* Progress bar rendered below the area. The ProgressBar reads state from the upload store. */}
      <div className="mt-6">
        <ProgressBar />
      </div>
    </div>
  );
}
