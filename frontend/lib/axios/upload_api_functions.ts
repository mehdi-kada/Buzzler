import api from "./auth_interceptor"; // Authenticated axios instance for backend calls
import { plainAxios } from "./plain_axios"; // Plain axios instance for external uploads
import { useUploadStore } from "../store/uploadStore";
import { toast } from "sonner";

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
): Promise<string> => {
  try {
    const response = await api.post<{ sas_url: string }>(
      "/upload/generate-sas",
      {
        file_name: fileName,
        file_size: fileSize,
      },
    );
    return response.data.sas_url;
  } catch (error) {
    // The error will be caught by the interceptor and a toast will be shown
    throw error;
  }
};

/**
 * Upload file directly to Azure using SAS URL
 * Uses plain axios instance to avoid sending auth headers/cookies to Azure
 */
export const uploadFileToAzure = async (
  sasUrl: string,
  file: File,
  fileId: string,
  onProgress?: (progress: number) => void,
): Promise<void> => {
  try {
    await plainAxios.put(sasUrl, file, {
      headers: {
        "x-ms-blob-type": "BlockBlob",
        "Content-Type": file.type || "application/octet-stream",
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total,
          );

          // Only update if this is still the current upload
          const currentFileId = useUploadStore.getState().fileId;
          if (currentFileId === fileId) {
            useUploadStore.getState().setProgress(percentCompleted);

            if (onProgress) {
              onProgress(percentCompleted);
            }
          }
        }
      },
    });
  } catch (error) {
    if (error instanceof Error) {
      toast.error(`Upload failed: ${error.message}`);
    } else {
      toast.error("File upload to Azure failed");
    }
    throw error;
  } finally {
    // Only reset if this upload is still the active one for handling mulitpe uploads
    const currentFileId = useUploadStore.getState().fileId;
    if (currentFileId === fileId) {
      useUploadStore.getState().reset();
    }
  }
};

/**
 * Notify backend that file upload is complete
 */
export const sendUploadInfoToBackend = async (
  fileName: string,
  fileSize: number,
  azureBlobUrl: string,
) => {
  try {
    const response = await api.post("/upload/complete", {
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
    const sasUrl = await getAzureSasUrl(file.name, file.size);
    await uploadFileToAzure(sasUrl, file, fileId, onProgress);
    const azureBlobUrl = sasUrl.split("?")[0];

    const result = await sendUploadInfoToBackend(
      file.name,
      file.size,
      azureBlobUrl,
    );

    return result;
  } catch (error) {
    useUploadStore.getState().setUploading(false);
    throw error;
  }
};
