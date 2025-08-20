"use client";

import React, { useState } from 'react';
import UploadArea from '@/components/upload/UploadArea';
import { UploadFormProps } from '@/components/upload/UploadForm';

export default function NewUploadVideoPage() {
  const [activeTab, setActiveTab] = useState<'file' | 'url'>('file');
  const [projectName, setProjectName] = useState('');
  const [category, setCategory] = useState('Podcast');
  const [description, setDescription] = useState('');
  const [aiOptions, setAiOptions] = useState({
    autoClips: true,
    socialCaptions: true,
    hashtags: true
  });

  const handleAiOptionChange = (option: keyof typeof aiOptions) => {
    setAiOptions(prev => ({
      ...prev,
      [option]: !prev[option]
    }));
  };

  return (
    <div className="min-h-screen bg-black text-white relative overflow-x-hidden">
      {/* Background */}
      <div className="fixed inset-0 gradient-bg"></div>
      
      {/* Animated Background Elements */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-pink-600 rounded-full opacity-60 animate-pulse"></div>
        <div className="absolute top-3/4 right-1/4 w-1 h-1 bg-orange-500 rounded-full opacity-40 animate-pulse" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-3/4 w-1.5 h-1.5 bg-pink-400 rounded-full opacity-50 animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>
      
      <main className="relative z-10 pt-8 pb-16 px-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-4">
              Upload Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-orange-500 glow-effect">Video</span>
            </h1>
            <p className="text-xl text-gray-300">Upload a file or import from URL to start creating viral clips</p>
          </div>
          
          {/* Upload Methods Tabs */}
          <div className="flex justify-center mb-8">
            <div className="flex bg-gray-800/50 rounded-lg p-1">
              <button 
                className={`px-6 py-2 rounded-md ${activeTab === 'file' ? 'bg-gradient-to-r from-pink-600 to-orange-500 text-white' : 'text-gray-300 hover:text-white transition-colors'}`}
                onClick={() => setActiveTab('file')}
              >
                File Upload
              </button>
              <button 
                className={`px-6 py-2 rounded-md ${activeTab === 'url' ? 'bg-gradient-to-r from-pink-600 to-orange-500 text-white' : 'text-gray-300 hover:text-white transition-colors'}`}
                onClick={() => setActiveTab('url')}
              >
                URL Import
              </button>
            </div>
          </div>
          
          {/* File Upload Section */}
          <div className={`mb-8 ${activeTab !== 'file' ? 'hidden' : ''}`}>
            <div className="upload-area p-12 rounded-2xl text-center">
              <UploadArea />
            </div>
          </div>
          
          {/* URL Import Section */}
          <div className={`mb-8 ${activeTab !== 'url' ? 'hidden' : ''}`}>
            <div className="form-input p-6 rounded-2xl">
              <h3 className="text-xl font-semibold mb-4">Import from URL</h3>
              <div className="mb-6">
                <input 
                  type="url" 
                  className="form-input w-full px-4 py-3 rounded-lg" 
                  placeholder="https://youtube.com/watch?v=..."
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
              
              <button className="btn-primary px-6 py-3 rounded-lg font-semibold">
                Import Video
              </button>
            </div>
          </div>
          
          {/* Project Settings */}
          <div className="form-input p-6 rounded-2xl">
            <h3 className="text-xl font-semibold mb-4">Project Settings</h3>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Project Name</label>
                <input 
                  type="text" 
                  className="form-input w-full px-4 py-3 rounded-lg" 
                  placeholder="My Awesome Video"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
                <select 
                  className="form-input w-full px-4 py-3 rounded-lg text-white"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  <option>Podcast</option>
                  <option>Tutorial</option>
                  <option>Interview</option>
                  <option>Presentation</option>
                  <option>Other</option>
                </select>
              </div>
            </div>
            
            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
              <textarea 
                rows={3} 
                className="form-input w-full px-4 py-3 rounded-lg" 
                placeholder="Brief description of your video content..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              ></textarea>
            </div>
            
            <div className="mt-6">
              <h4 className="font-medium mb-3">AI Processing Options</h4>
              <div className="space-y-3">
                <label className="flex items-center space-x-3">
                  <input 
                    type="checkbox" 
                    className="w-4 h-4 text-pink-600 bg-gray-800 border-gray-600 rounded focus:ring-pink-500" 
                    checked={aiOptions.autoClips}
                    onChange={() => handleAiOptionChange('autoClips')}
                  />
                  <span className="text-sm text-gray-300">Generate automatic clips (recommended)</span>
                </label>
                <label className="flex items-center space-x-3">
                  <input 
                    type="checkbox" 
                    className="w-4 h-4 text-pink-600 bg-gray-800 border-gray-600 rounded focus:ring-pink-500" 
                    checked={aiOptions.socialCaptions}
                    onChange={() => handleAiOptionChange('socialCaptions')}
                  />
                  <span className="text-sm text-gray-300">Create social media captions</span>
                </label>
                <label className="flex items-center space-x-3">
                  <input 
                    type="checkbox" 
                    className="w-4 h-4 text-pink-600 bg-gray-800 border-gray-600 rounded focus:ring-pink-500" 
                    checked={aiOptions.hashtags}
                    onChange={() => handleAiOptionChange('hashtags')}
                  />
                  <span className="text-sm text-gray-300">Generate hashtag suggestions</span>
                </label>
              </div>
            </div>
            
            <div className="flex space-x-4 mt-8">
              <button className="btn-primary px-8 py-3 rounded-lg font-semibold">
                Start Processing
              </button>
              <button className="btn-secondary px-8 py-3 rounded-lg font-semibold">
                Save as Draft
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}