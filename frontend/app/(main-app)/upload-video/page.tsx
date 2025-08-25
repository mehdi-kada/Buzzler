"use client";

import React, { useState } from "react";
import UploadArea from "@/components/upload/UploadArea";
import VideoImport from "@/components/upload/VideoImport";
import ProjectSettings from "@/components/upload/ProjectSettings";
import { useVideoImport } from "@/hooks/useVideoImport";
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
  
  const { 
    importVideo, 
    uploading, 
    progressData, 
    errData, 
    reset 
  } = useVideoImport();
  
  const handleImportStart = () => {
    // Reset any previous errors
    if (errData) {
      reset();
    }
  };
  
  const handleImportSuccess = (videoData: any) => {
    toast.success("Video import started successfully!");
    // You can add additional logic here when import starts
  };
  
  const handleImportError = (error: string) => {
    toast.error(error);
  };
  
  // We'll create a new component for the progress display
  const VideoImportProgress = ({ progress }: { progress: VideoProgressUpdate }) => {
    const getStatusText = () => {
      switch (progress.status) {
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
    const progressPercentage = progress.progressPercentage || 0;
    
    return (
      <div className="form-input p-6 rounded-2xl">
        <h3 className="text-xl font-semibold mb-4">Import Progress</h3>
        
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-1">
            <span>{statusText}</span>
            <span>{progressPercentage}%</span>
          </div>
          <div className="progress-bar h-2 rounded-full overflow-hidden">
            <div 
              className="progress-fill h-full" 
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>
        
        {progress.message && (
          <div className="text-sm text-gray-300 mb-4">
            {progress.message}
          </div>
        )}
        
        {progress.status === "failed" && errData && (
          <div className="text-sm text-red-400 mb-4">
            {errData}
          </div>
        )}
        
        <button
          className="btn-secondary px-4 py-2 rounded-lg font-medium"
          onClick={reset}
        >
          Import Another Video
        </button>
      </div>
    );
  };
  
  // Create a wrapper component that uses the hook
  const VideoImportWithHook = () => {
    const [url, setUrl] = useState("");
    
    const handleImport = async () => {
      if (!url.trim()) {
        toast.error("Please enter a valid URL");
        return;
      }
      
      try {
        new URL(url);
      } catch {
        toast.error("Please enter a valid URL");
        return;
      }
      
      handleImportStart();
      await importVideo(url);
    };
    
    const handleKeyPress = (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !uploading) {
        handleImport();
      }
    };
    
    // Show progress if we're uploading
    if (uploading && progressData) {
      return <VideoImportProgress progress={progressData} />;
    }
    
    // Show error if there was one
    if (errData && !uploading) {
      return (
        <div className="form-input p-6 rounded-2xl">
          <h3 className="text-xl font-semibold mb-4">Import from URL</h3>
          
          <div className="mb-6">
            <input
              type="url"
              className="form-input w-full px-4 py-3 rounded-lg"
              placeholder="https://youtube.com/watch?v=..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={uploading}
            />
          </div>
          
          {/* Supported Platforms */}
          <div className="mb-6">
            <p className="text-sm text-gray-300 mb-3">Supported platforms:</p>
            <div className="grid grid-cols-4 gap-3">
              <div className="platform-icon p-3 rounded-lg text-center">
                <span className="text-red-500 text-2xl">📺</span>
                <p className="text-xs mt-1">YouTube</p>
              </div>
              <div className="platform-icon p-3 rounded-lg text-center">
                <span className="text-blue-500 text-2xl">🎵</span>
                <p className="text-xs mt-1">Vimeo</p>
              </div>
              <div className="platform-icon p-3 rounded-lg text-center">
                <span className="text-purple-500 text-2xl">🎮</span>
                <p className="text-xs mt-1">Twitch</p>
              </div>
              <div className="platform-icon p-3 rounded-lg text-center">
                <span className="text-blue-600 text-2xl">👥</span>
                <p className="text-xs mt-1">Facebook</p>
              </div>
            </div>
          </div>
          
          <div className="text-sm text-red-400 mb-4">
            {typeof errData === 'string' ? errData : JSON.stringify(errData)}
          </div>
          
          <button
            className={`btn-primary px-6 py-3 rounded-lg font-semibold ${
              uploading || !url.trim() ? "opacity-60 cursor-not-allowed" : ""
            }`}
            onClick={handleImport}
            disabled={uploading || !url.trim()}
          >
            {uploading ? "Importing..." : "Import Video"}
          </button>
        </div>
      );
    }
    
    // Show the regular import form
    return (
      <div className="form-input p-6 rounded-2xl">
        <h3 className="text-xl font-semibold mb-4">Import from URL</h3>
        
        <div className="mb-6">
          <input
            type="url"
            className="form-input w-full px-4 py-3 rounded-lg"
            placeholder="https://youtube.com/watch?v=..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={uploading}
          />
        </div>
        
        {/* Supported Platforms */}
        <div className="mb-6">
          <p className="text-sm text-gray-300 mb-3">Supported platforms:</p>
          <div className="grid grid-cols-4 gap-3">
            <div className="platform-icon p-3 rounded-lg text-center">
              <span className="text-red-500 text-2xl">📺</span>
              <p className="text-xs mt-1">YouTube</p>
            </div>
            <div className="platform-icon p-3 rounded-lg text-center">
              <span className="text-blue-500 text-2xl">🎵</span>
              <p className="text-xs mt-1">Vimeo</p>
            </div>
            <div className="platform-icon p-3 rounded-lg text-center">
              <span className="text-purple-500 text-2xl">🎮</span>
              <p className="text-xs mt-1">Twitch</p>
            </div>
            <div className="platform-icon p-3 rounded-lg text-center">
              <span className="text-blue-600 text-2xl">👥</span>
              <p className="text-xs mt-1">Facebook</p>
            </div>
          </div>
        </div>
        
        <button
          className={`btn-primary px-6 py-3 rounded-lg font-semibold ${
            uploading || !url.trim() ? "opacity-60 cursor-not-allowed" : ""
          }`}
          onClick={handleImport}
          disabled={uploading || !url.trim()}
        >
          {uploading ? "Importing..." : "Import Video"}
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
            <VideoImportWithHook />
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
