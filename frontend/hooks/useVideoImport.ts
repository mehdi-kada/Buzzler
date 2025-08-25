import api from "@/lib/axios/auth_interceptor";
import {
  ServerStats,
  UseVideoImportReturn,
  VideoProgressUpdate,
} from "@/types/video_validation";
import { useCallback, useEffect, useState } from "react";

export const useVideoImport = (): UseVideoImportReturn => {
  const [serverStats, setServerStats] = useState<ServerStats | null>(null);
  const [taskId, setTaskId] = useState("");
  const [errData, setErrData] = useState("");
  const [uploading, setUploading] = useState(false);
  const [progressData, setProgress] = useState<VideoProgressUpdate | null>(
    null,
  );

  const refreshServerStats = useCallback(async () => {
    api
      .get("/import/server-stats")
      .then((result) => setServerStats(result.data.server_stats))
      .catch((error) => console.log("Error fetching server stats:", error));
  }, []);

  const importVideo = useCallback(
    async (
      url: string,
      format_selector: string = "best[ext=mp4]/best[height<=720]",
      custom_filename?: string,
    ) => {
      try {
        const { data } = await api.post("/import/import-video", {
          url,
          format_selector,
          custom_filename,
        });

        setTaskId(data.task_id);
        setUploading(true);
        await refreshServerStats();
      } catch (err: any) {
        let errorMessage = "Error importing video. Please check the URL and try again.";
        
        // Handle different error response formats
        if (err?.response?.data?.detail) {
          const detail = err.response.data.detail;
          if (typeof detail === 'string') {
            errorMessage = detail;
          } else if (typeof detail === 'object') {
            // Handle validation error objects with {type, loc, msg, input} structure
            if (detail.msg) {
              errorMessage = detail.msg;
            } else if (Array.isArray(detail)) {
              // Handle array of validation errors
              errorMessage = detail.map((error: any) => 
                error.msg || JSON.stringify(error)
              ).join(', ');
            } else {
              // Fallback for other object structures
              errorMessage = JSON.stringify(detail);
            }
          }
        }
        
        setErrData(errorMessage);
        setUploading(false);
        console.log(err);
      }
    },
    [refreshServerStats],
  );

  useEffect(() => {
    if (!taskId || !uploading) return;

    const progressPoll = async () => {
      try {
        const response = await api.get(`/import/task-status/${taskId}`);
        const data: VideoProgressUpdate = response.data;
        setProgress(data);

        if (
          data.status === "failed" ||
          data.status === "uploaded"
        ) {
          setUploading(false);
          await refreshServerStats();

          if (data.status === "failed") {
            setErrData(data?.errorMessage || "Upload failed");
          }
        }
      } catch (err: any) {
        let errorMessage = "Failed to fetch progress";
        
        // Handle different error response formats
        if (err?.response?.data?.detail) {
          const detail = err.response.data.detail;
          if (typeof detail === 'string') {
            errorMessage = detail;
          } else if (typeof detail === 'object') {
            // Handle validation error objects with {type, loc, msg, input} structure
            if (detail.msg) {
              errorMessage = detail.msg;
            } else if (Array.isArray(detail)) {
              // Handle array of validation errors
              errorMessage = detail.map((error: any) => 
                error.msg || JSON.stringify(error)
              ).join(', ');
            } else {
              // Fallback for other object structures
              errorMessage = JSON.stringify(detail);
            }
          }
        } else if (err instanceof Error) {
          errorMessage = err.message;
        }
        
        setErrData(errorMessage);
        setUploading(false);
      }
    };
    // poll every 2 seconds
    const interval = setInterval(progressPoll, 2000);
    progressPoll(); //initila call

    return () => clearInterval(interval);
  }, [taskId, uploading, refreshServerStats]);

  // load server stats on load
  useEffect(() => {
    refreshServerStats();
  }, [refreshServerStats]);

  const reset = () => {
    setTaskId("");
    setErrData("");
    setUploading(false);
    setProgress(null);
  };

  return {
    serverStats,
    taskId,
    errData,
    uploading,
    progressData,
    importVideo,
    refreshServerStats,
    reset,
  };
};
