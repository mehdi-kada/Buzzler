import api from "./auth_interceptor"; // Authenticated axios instance for backend calls
import { useUploadStore } from "../store/uploadStore";
import { toast } from "sonner";
import { BlockBlobClient } from "@azure/storage-blob";

// Add response interceptor to the authenticated api instance for backend calls
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const message =
        error.response.data?.detail ||
        error.response.data?.message ||
        error.response.data?.error ||
        `Error ${error.response.status}: ${error.response.statusText}`;
      toast.error(message);
    } else if (error.request) {
      toast.error("Network error. Please check your connection.");
    } else {
      toast.error("An unexpected error occurred.");
    }
    return Promise.reject(error);
  },
);

/**
 * Get Azure SAS URL from backend for file upload
 */
export const getAzureSasUrl = async (
  fileName: string,
  fileSize: number,
): Promise<{ sasUrl: string; filePath: string; videoId: number }> => {
  try {
    const response = await api.post<{
      sas_url: string;
      file_path: string;
      video_id: number;
    }>("/upload/generate-sas", {
      file_name: fileName,
      file_path: fileName, // Using fileName as file_path for now, as this is what the backend expects
    });
    return {
      sasUrl: response.data.sas_url,
      filePath: response.data.file_path,
      videoId: response.data.video_id,
    };
  } catch (error) {
    // The error will be caught by the interceptor and a toast will be shown
    throw error;
  }
};

/**
 * Upload file directly to Azure using SAS URL
 * Uses Azure Storage Blob SDK for robust, chunked uploads with parallelism
 */
export const uploadFileToAzure = async (
  sasUrl: string,
  file: File,
  fileId: string,
  onProgress?: (progress: number) => void,
): Promise<void> => {
  // Use Azure Storage Blob SDK for robust, chunked uploads with parallelism
  const blobClient = new BlockBlobClient(sasUrl);
  const controller = new AbortController();

  // Expose the controller in the store so UI can cancel the upload
  useUploadStore.getState().setAbortController(controller);

  const blockSize = 2 * 1024 * 1024; // 8 MB chunks
  const concurrency = 4; // Parallel chunk uploads
  const maxSingleShotSize = 8 * 1024 * 1024; // 20 MB single-shot threshold (example)

  try {
    await blobClient.uploadData(file, {
      blockSize,
      concurrency,
      maxSingleShotSize,
      blobHTTPHeaders: {
        blobContentType: file.type || "application/octet-stream",
      },
      onProgress: (ev: { loadedBytes?: number }) => {
        const total = file.size;
        if (total && ev.loadedBytes != null) {
          const percentCompleted = Math.round((ev.loadedBytes * 100) / total);

          // Only update if this is still the current upload
          const currentFileId = useUploadStore.getState().fileId;

          if (currentFileId === fileId) {
            useUploadStore.getState().setProgress(percentCompleted);

            // Also call the onProgress callback if provided
            if (onProgress) {
              onProgress(percentCompleted);
            }
          }
        }
      },
      abortSignal: controller.signal,
    });
  } catch (error) {
    // If the error is an abort, surface a cancellation message; otherwise show the error message
    const isAbort =
      (error as any)?.name === "AbortError" ||
      (error as any)?.message === "The operation was aborted.";
    if (isAbort) {
      toast.error("Upload cancelled.");
    } else if (error instanceof Error) {
      toast.error(`Upload failed: ${error.message}`);
    } else {
      toast.error("File upload to Azure failed");
    }
    throw error;
  } finally {
    // Clear stored controller once upload finishes (success, failure, or abort)
    useUploadStore.getState().setAbortController(null);
  }
};

/**
 * Notify backend that file upload is complete
 */
export const sendUploadInfoToBackend = async (
  fileName: string,
  fileSize: number,
  azureBlobUrl: string,
  videoId: number,
) => {
  try {
    const response = await api.post(`/upload/complete?video_id=${videoId}`, {
      file_name: fileName,
      file_size: fileSize,
      azure_blob_url: azureBlobUrl,
    });
    toast.success("File uploaded and registered successfully!");
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Complete upload workflow: get SAS URL, upload to Azure, notify backend
 */
export const uploadFileComplete = async (
  file: File,
  fileId: string,
  onProgress?: (progress: number) => void,
) => {
  try {
    useUploadStore.getState().setUploading(true, file.name, fileId);

    // Step 1: Get SAS URL and video ID from backend
    const { sasUrl, filePath, videoId } = await getAzureSasUrl(
      file.name,
      file.size,
    );

    console.log("SAS URL and video ID retrieved:", {
      sasUrl,
      filePath,
      videoId,
    });

    // Step 2: Upload file to Azure
    await uploadFileToAzure(sasUrl, file, fileId, onProgress);

    // Step 3: Notify backend that upload is complete
    const azureBlobUrl = sasUrl.split("?")[0];
    const result = await sendUploadInfoToBackend(
      file.name,
      file.size,
      azureBlobUrl,
      videoId,
    );

    // Mark completed in store to keep progress at 100% and allow UI to reflect completion
    try {
      const store = useUploadStore.getState();
      // Ensure progress is at 100%
      store.setProgress(100);
      // If the store supports a completion flag, set it (optional, backward compatible)
      if (typeof (store as any).setCompleted === "function") {
        (store as any).setCompleted(file.name, fileId, videoId);
      }
      // Do NOT call setUploading(false) here, since some implementations reset progress on that call.
      // Let the UI decide when to clear the completed state.
    } catch {
      // no-op if store is unavailable for any reason
    }

    return result;
  } catch (error) {
    useUploadStore.getState().setUploading(false);
    throw error;
  }
};
