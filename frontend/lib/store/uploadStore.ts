import { create } from "zustand";

interface UploadState {
  progress: number;
  isUploading: boolean;
  fileName: string | null;
  fileId: string | null; // To track which file is being uploaded
  videoId: number | null; // To track the video ID in the database

  setProgress: (progress: number) => void;

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
  fileName: null,
  fileId: null,
  videoId: null,

  setProgress: (progress: number) => {
    // Clamp to valid bounds and update
    const clamped = Math.max(0, Math.min(100, Math.round(progress)));
    set({ progress: clamped });
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
        fileName: fileName ?? prev.fileName,
        fileId: fileId ?? prev.fileId,
        videoId: videoId ?? prev.videoId,
      });
    } else {
      // If stopping an upload, clear identifying info and reset progress
      set({
        isUploading: false,
        fileName: null,
        fileId: null,
        videoId: null,
        progress: 0,
      });
    }
  },

  reset: () =>
    set({
      progress: 0,
      isUploading: false,
      fileName: null,
      fileId: null,
      videoId: null,
    }),
}));
