"use client";

import React, { useState, useEffect } from "react";
import UploadArea from "@/components/upload/UploadArea";
import VideoImport from "@/components/upload/VideoImport";
import ProjectSettings from "@/components/upload/ProjectSettings";
import api from "@/lib/axios/auth_interceptor";
import { VideoProgressUpdate } from "@/types/video_validation";
import { toast } from "sonner";

export default function NewUploadVideoPage() {
  const [activeTab, setActiveTab] = useState<"file" | "url">("file");
  const [projectName, setProjectName] = useState("");
  const [category, setCategory] = useState("Podcast");
  const [description, setDescription] = useState("");
  const [aiOptions, setAiOptions] = useState({
    autoClips: true,
    socialCaptions: true,
    hashtags: true,
  });
  
  const [taskId, setTaskId] = useState<string | null>(null);
  const [isImporting, setIsImporting] = useState(false);
  const [progressData, setProgressData] = useState<VideoProgressUpdate | null>(null);
  const [errData, setErrData] = useState<string | null>(null);
  
  // Handle import start
  const handleImportStart = (newTaskId: string) => {
    setTaskId(newTaskId);
    setIsImporting(true);
    setProgressData(null);
    setErrData(null);
  };
  
  // Handle import error
  const handleImportError = (error: string) => {
    setErrData(error);
    setIsImporting(false);
  };
  
  // Reset the import process
  const resetImport = () => {
    setTaskId(null);
    setIsImporting(false);
    setProgressData(null);
    setErrData(null);
  };
  
  // Poll for progress updates
  useEffect(() => {
    if (!taskId || !isImporting) return;
    
    const fetchProgress = async () => {
      try {
        const response = await api.get(`/import/task-status/${taskId}`);
        const data: VideoProgressUpdate = response.data;
        setProgressData(data);
        
        // Check if the task is completed or failed
        if (data.status === "failed") {
          setErrData(data.error_message || "Upload failed");
          setIsImporting(false);
        } else if (data.status === "ready") {
          // Keep the progress bar visible but show completion
          toast.success("Video import completed successfully!");
        }
      } catch (error: any) {
        let errorMessage = "Failed to fetch progress";
        
        // Handle different error response formats
        if (error?.response?.data?.detail) {
          const detail = error.response.data.detail;
          if (typeof detail === 'string') {
            errorMessage = detail;
          } else if (typeof detail === 'object') {
            if (detail.msg) {
              errorMessage = detail.msg;
            } else if (Array.isArray(detail)) {
              errorMessage = detail.map((error: any) => 
                error.msg || JSON.stringify(error)
              ).join(', ');
            } else {
              errorMessage = JSON.stringify(detail);
            }
          }
        } else if (error instanceof Error) {
          errorMessage = error.message;
        }
        
        setErrData(errorMessage);
        setIsImporting(false);
      }
    };
    
    // Poll every 2 seconds
    const interval = setInterval(fetchProgress, 2000);
    fetchProgress(); // Initial call
    
    return () => clearInterval(interval);
  }, [taskId, isImporting]);
  
  // Progress display component
  const VideoImportProgress = () => {
    if (!progressData) return null;
    
    const getStatusText = () => {
      switch (progressData.status) {
        case "pending_upload":
          return "Preparing upload...";
        case "uploading":
          return "Uploading video...";
        case "uploaded":
          return "Upload complete!";
        case "transcribing":
          return "Transcribing video...";
        case "analyzing":
          return "Analyzing content...";
        case "ready":
          return "Ready!";
        case "failed":
          return "Import failed";
        default:
          return "Processing...";
      }
    };
    
    const statusText = getStatusText();
    // When status is "ready", show 100% progress
    const progressPercentage = progressData.status === "ready" 
      ? 100 
      : progressData.progress_percentage || 0;
    
    // Show checkmark when task is completed
    const showCheckmark = progressData.status === "ready";
    
    return (
      <div className="form-input p-6 rounded-2xl">
        <h3 className="text-xl font-semibold mb-4">Import Progress</h3>
        
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-1">
            <div className="flex items-center">
              <span>{statusText}</span>
              {showCheckmark && (
                <svg 
                  className="ml-2 text-green-500 w-5 h-5" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth="2" 
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              )}
            </div>
            <span>{Math.round(progressPercentage)}%</span>
          </div>
          <div className="progress-bar h-2 rounded-full overflow-hidden">
            <div 
              className="progress-fill h-full" 
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>
        
        {progressData.message && (
          <div className="text-sm text-gray-300 mb-4">
            {progressData.message}
          </div>
        )}
        
        {progressData.status === "failed" && errData && (
          <div className="text-sm text-red-400 mb-4">
            {errData}
          </div>
        )}
        
        {progressData.status === "ready" && (
          <div className="text-sm text-green-400 mb-4">
            Video import completed successfully!
          </div>
        )}
        
        <button
          className="btn-secondary px-4 py-2 rounded-lg font-medium"
          onClick={resetImport}
        >
          Import Another Video
        </button>
      </div>
    );
  };
  
  // Error display component
  const VideoImportError = () => {
    if (!errData || isImporting) return null;
    
    return (
      <div className="form-input p-6 rounded-2xl">
        <h3 className="text-xl font-semibold mb-4">Import from URL</h3>
        
        <div className="text-sm text-red-400 mb-4">
          {errData}
        </div>
        
        <button
          className="btn-secondary px-4 py-2 rounded-lg font-medium"
          onClick={resetImport}
        >
          Try Again
        </button>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-black text-white relative overflow-x-hidden">
      {/* Background */}
      <div className="fixed inset-0 gradient-bg"></div>

      {/* Animated Background Elements */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-pink-600 rounded-full opacity-60 animate-pulse"></div>
        <div
          className="absolute top-3/4 right-1/4 w-1 h-1 bg-orange-500 rounded-full opacity-40 animate-pulse"
          style={{ animationDelay: "1s" }}
        ></div>
        <div
          className="absolute top-1/2 left-3/4 w-1.5 h-1.5 bg-pink-400 rounded-full opacity-50 animate-pulse"
          style={{ animationDelay: "2s" }}
        ></div>
      </div>

      <main className="relative z-10 pt-8 pb-16 px-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-4">
              Upload Your{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-orange-500 glow-effect">
                Video
              </span>
            </h1>
            <p className="text-xl text-gray-300">
              Upload a file or import from URL to start creating viral clips
            </p>
          </div>

          {/* Upload Methods Tabs */}
          <div className="flex justify-center mb-8">
            <div className="flex bg-gray-800/50 rounded-lg p-1">
              <button
                className={`px-6 py-2 rounded-md ${activeTab === "file" ? "bg-gradient-to-r from-pink-600 to-orange-500 text-white" : "text-gray-300 hover:text-white transition-colors"}`}
                onClick={() => setActiveTab("file")}
              >
                File Upload
              </button>
              <button
                className={`px-6 py-2 rounded-md ${activeTab === "url" ? "bg-gradient-to-r from-pink-600 to-orange-500 text-white" : "text-gray-300 hover:text-white transition-colors"}`}
                onClick={() => setActiveTab("url")}
              >
                URL Import
              </button>
            </div>
          </div>

          {/* File Upload Section */}
          <div className={`mb-8 ${activeTab !== "file" ? "hidden" : ""}`}>
            <div className="upload-area p-12 rounded-2xl text-center">
              <UploadArea />
            </div>
          </div>

          {/* URL Import Section */}
          <div className={`mb-8 ${activeTab !== "url" ? "hidden" : ""}`}>
            {isImporting ? (
              <VideoImportProgress />
            ) : errData ? (
              <VideoImportError />
            ) : (
              <VideoImport 
                onImportStart={handleImportStart}
                onImportError={handleImportError}
              />
            )}
          </div>

          {/* Project Settings */}
          <ProjectSettings
            projectName={projectName}
            setProjectName={setProjectName}
            category={category}
            setCategory={setCategory}
            description={description}
            setDescription={setDescription}
            aiOptions={aiOptions}
            setAiOptions={setAiOptions}
          />
        </div>
      </main>
    </div>
  );
}
