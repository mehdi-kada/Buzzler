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
        const errorMessage =
          err?.response?.data?.detail ||
          "Error importing video. Please check the URL and try again.";
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
        const errorMessage =
          err?.response?.data?.detail ||
          (err instanceof Error ? err.message : "Failed to fetch progress");
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
