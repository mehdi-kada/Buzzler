export interface videoValidationConfig {
  maxSizeInMB?: number;
  maxDurationInSeconds?: number;
  allowedFormats?: string[];
  minWidth?: number;
  minHeight?: number;
  maxWidth?: number;
  maxHeight?: number;
}

export interface VideoProgressUpdate {
  taskId: string;
  status:
    | "uploading"
    | "uploaded"
    | "transcribing"
    | "analyzing"
    | "ready"
    | "failed"
    | "pending_upload";
  progressPercentage: number;
  uploadedBytes: number;
  totalBytes?: number;
  currentStep: string;
  blobName?: string;
  blobUrl?: string;
  errorMessage?: string;
  metadata?: any;
  message?: string;
}

export interface videoMeta {
  duration: number;
  height: number;
  width: number;
  format: string;
  sizeInMB: number;
  fileName: string;
}

export interface videoValidationResult {
  isValid: boolean;
  errors: string[];
  metadata?: videoMeta;
}

export interface ServerStats {
  active_uploads: number;
  max_concurrent: number;
  available_slots: number;
}

export interface UseVideoImportReturn {
  serverStats: ServerStats | null;
  taskId: string;
  errData: string;
  uploading: boolean;
  progressData: VideoProgressUpdate | null;
  importVideo: (
    url: string,
    format_selector?: string,
    custom_filename?: string,
  ) => Promise<void>;
  refreshServerStats: () => Promise<void>;
  reset: () => void;
}
