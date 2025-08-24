"use client";

import React, { useState } from "react";
import UploadArea from "@/components/upload/UploadArea";
import VideoImport from "@/components/upload/VideoImport";
import ProjectSettings from "@/components/upload/ProjectSettings";

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
            <VideoImport
              onImportStart={() => {
                // Handle import start if needed
              }}
              onImportSuccess={(videoData) => {
                // Handle successful import
                console.log("Video imported:", videoData);
              }}
              onImportError={(error) => {
                // Handle import error
                console.error("Import error:", error);
              }}
            />
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
