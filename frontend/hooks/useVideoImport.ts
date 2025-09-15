import api from "@/lib/axios/auth_interceptor";
import {
  ServerStats,
  UseVideoImportReturn,
  VideoProgressUpdate,
} from "@/types/video_validation";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";


export const useVideoImport = (): UseVideoImportReturn => {
  const [serverStats, setServerStats] = useState<ServerStats | null>(null);
  const [taskId, setTaskId] = useState<string|null>(null);
  const [errData, setErrData] = useState<string|null>(null);
  const [uploading, setUploading] = useState(false);
  const [progressData, setProgressData] = useState<VideoProgressUpdate | null>(null);

  const refreshServerStats = useCallback(async () => {
    try {
      const { data } = await api.get("/import/server-stats");
      setServerStats(data.server_stats);
    } catch (err) {
      console.log("Failed to fetch server stats", err);
    }
  }, []);

  const importVideo = useCallback(
    async (
      url: string,
      custom_file_name?: string,
    ) => {
      try {
        const { data } = await api.post("/import/import-video", {
          url,
          custom_file_name: custom_file_name || null,
        });

        setTaskId(data.task_id);
        setUploading(true);
        setProgressData(null)
        setErrData(null);
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
        setProgressData(data);
        
        if (data.status === "failed"){
          setErrData(data?.errorMessage || "Upload failed");
          setUploading(false);
        }

        if (data.status === "uploaded" || data.status === "ready") {
          setUploading(false);
          toast.success("Video imported successfully!");
          await refreshServerStats();
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
    progressPoll(); //initial call

    return () => clearInterval(interval);
  }, [taskId, uploading]);

  // load server stats on load
  useEffect(() => {
    refreshServerStats();
  }, [refreshServerStats]);

  const reset = () => {
    setTaskId(null);
    setErrData(null);
    setUploading(false);
    setProgressData(null);
  };

  return {
    serverStats,
    taskId: taskId || null,
    errData: errData || null,
    uploading,
    progressData,
    importVideo,
    refreshServerStats,
    reset,
  };
};
