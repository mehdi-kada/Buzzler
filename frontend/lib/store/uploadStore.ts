import { create } from "zustand";

interface UploadState {
  progress: number;
  isUploading: boolean;
  isCompleted: boolean;
  fileName: string | null;
  fileId: string | null; // To track which file is being uploaded
  videoId: number | null; // To track the video ID in the database
  abortController: AbortController | null;

  setProgress: (progress: number) => void;

  // Mark upload as completed or not; when completed=true we keep progress at 100
  setCompleted: (completed?: boolean) => void;

  // Store and manage an AbortController so UI can cancel an in-flight upload
  setAbortController: (controller: AbortController | null) => void;

  // Trigger a cancel from the store (aborts and resets state)
  cancelUpload: () => void;

  setUploading: (
    isUploading: boolean,
    fileName?: string | null,
    fileId?: string | null,
    videoId?: number | null,
  ) => void;

  // Reset the store to initial defaults
  reset: () => void;
}

export const useUploadStore = create<UploadState>((set, get) => ({
  progress: 0,
  isUploading: false,
  isCompleted: false,
  fileName: null,
  fileId: null,
  videoId: null,
  abortController: null,

  setProgress: (progress: number) => {
    // Clamp to valid bounds and update
    const clamped = Math.max(0, Math.min(100, Math.round(progress)));
    set({ progress: clamped, isCompleted: clamped >= 100 });
  },

  setCompleted: (completed: boolean = true) => {
    if (completed) {
      const current = get();
      set({
        isUploading: false,
        isCompleted: true,
        progress: Math.max(100, current.progress),
      });
    } else {
      set({ isCompleted: false });
    }
  },

  setAbortController: (controller: AbortController | null) => {
    set({ abortController: controller });
  },

  cancelUpload: () => {
    const prev = get();
    // Abort any in-flight request
    if (prev.abortController) {
      try {
        prev.abortController.abort();
      } catch {
        // ignore abort errors
      }
    }
    // Reset upload-related state
    set({
      progress: 0,
      isUploading: false,
      isCompleted: false,
      fileName: null,
      fileId: null,
      videoId: null,
      abortController: null,
    });
  },

  setUploading: (
    isUploading: boolean,
    fileName?: string | null,
    fileId?: string | null,
    videoId?: number | null,
  ) => {
    if (isUploading) {
      // If starting an upload, preserve previous values when not provided
      const prev = get();
      set({
        isUploading: true,
        isCompleted: false,
        progress: 0,
        fileName: fileName ?? prev.fileName,
        fileId: fileId ?? prev.fileId,
        videoId: videoId ?? prev.videoId,
      });
    } else {
      // If stopping an upload, abort any in-flight request and clear identifying info and reset progress
      const prev = get();
      if (prev.abortController) {
        try {
          prev.abortController.abort();
        } catch {
          // ignore abort errors
        }
      }
      set({
        isUploading: false,
        isCompleted: prev.progress >= 100,
        abortController: null,
      });
    }
  },

  reset: () =>
    set({
      progress: 0,
      isUploading: false,
      isCompleted: false,
      fileName: null,
      fileId: null,
      videoId: null,
      abortController: null,
    }),
}));
