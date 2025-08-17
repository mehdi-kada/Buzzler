"use client"
import React, { useCallback, useRef, useState } from "react";
import ProgressBar from "./ProgressBar";
import { uploadFileComplete } from "../../lib/axios/upload_api_functions";
import { useUploadStore } from "../../lib/store/uploadStore";
import { toast } from "sonner";

/**
 * UploadArea
 *
 * Drag-and-drop or press-to-select upload area. Collects a small metadata form
 * (title, description, tags) before starting the upload, shows the progress bar
 * while uploading and allows cancelling via the progress UI.
 *
 * This component intentionally keeps styling inline/simple so it can be dropped
 * into existing pages without requiring CSS changes.
 */

export default function UploadArea() {
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
    // user wants to cancel before starting upload
    resetForm();
  }, [resetForm]);

  const areaBaseStyle: React.CSSProperties = {
    borderRadius: 8,
    border: "2px dashed #cbd5e1",
    background: isDragging ? "#f1f5f9" : "#ffffff",
    padding: 20,
    display: "flex",
    flexDirection: "column",
    alignItems: "stretch",
    gap: 12,
    maxWidth: 800,
    boxSizing: "border-box",
  };

  const dropTextStyle: React.CSSProperties = {
    textAlign: "center",
    color: "#0f172a",
    fontSize: 15,
  };

  const controlsRowStyle: React.CSSProperties = {
    display: "flex",
    gap: 8,
    alignItems: "center",
  };

  const btnStyle: React.CSSProperties = {
    padding: "8px 12px",
    background: "#4f46e5",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    cursor: "pointer",
  };

  const secondaryBtnStyle: React.CSSProperties = {
    padding: "8px 12px",
    background: "transparent",
    color: "#334155",
    border: "1px solid #e2e8f0",
    borderRadius: 6,
    cursor: "pointer",
  };

  return (
    <div>
      <div
        style={areaBaseStyle}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragEnter={onDragOver}
        onDragLeave={onDragLeave}
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
          style={{ display: "none" }}
          onChange={onFileInputChange}
        />

        <div style={dropTextStyle}>
          <div style={{ fontWeight: 600, marginBottom: 6 }}>
            {isDragging
              ? "Drop files here to upload"
              : "Drag & drop a video or click to select"}
          </div>

          <div style={{ color: "#475569", fontSize: 13 }}>
            MP4, MOV, WEBM etc. Max 2GB.
          </div>
        </div>

        <div style={controlsRowStyle}>
          <button
            type="button"
            style={btnStyle}
            onClick={onChooseFile}
            aria-label="Choose a file to upload"
          >
            Choose file
          </button>

          <button
            type="button"
            style={secondaryBtnStyle}
            onClick={() => {
              // quick demo action: clear previously selected file
              resetForm();
            }}
          >
            Clear
          </button>

          <div style={{ marginLeft: "auto", color: "#64748b", fontSize: 13 }}>
            {file
              ? `${file.name} • ${(file.size / (1024 * 1024)).toFixed(1)} MB`
              : "No file selected"}
          </div>
        </div>

        {/* Metadata form */}
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <input
            placeholder="Title (optional)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            style={{
              padding: "8px 10px",
              borderRadius: 6,
              border: "1px solid #e6eef8",
              outline: "none",
            }}
            disabled={isUploading}
          />
          <textarea
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            style={{
              padding: "8px 10px",
              borderRadius: 6,
              border: "1px solid #e6eef8",
              outline: "none",
            }}
            disabled={isUploading}
          />
          <input
            placeholder="Tags (comma separated)"
            value={tagsRaw}
            onChange={(e) => setTagsRaw(e.target.value)}
            style={{
              padding: "8px 10px",
              borderRadius: 6,
              border: "1px solid #e6eef8",
              outline: "none",
            }}
            disabled={isUploading}
          />
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
          <button
            type="button"
            style={{
              ...secondaryBtnStyle,
              opacity: file ? 1 : 0.6,
              cursor: file ? "pointer" : "not-allowed",
            }}
            onClick={handleCancelClick}
            disabled={!file || isUploading || isSubmitting}
          >
            Cancel
          </button>

          <button
            type="button"
            style={{
              ...btnStyle,
              opacity: file ? 1 : 0.6,
              cursor: file ? "pointer" : "not-allowed",
            }}
            onClick={onStartUpload}
            disabled={!file || isUploading || isSubmitting}
          >
            {isSubmitting || isUploading ? "Uploading…" : "Upload"}
          </button>
        </div>

        {/* Show small hint when dragging files */}
        {isDragging && (
          <div style={{ color: "#0ea5a0", fontSize: 13, marginTop: 4 }}>
            Release to upload
          </div>
        )}
      </div>

      {/* Progress bar rendered below the area. The ProgressBar reads state from the upload store. */}
      <div style={{ marginTop: 12 }}>
        <ProgressBar />
      </div>
    </div>
  );
}
