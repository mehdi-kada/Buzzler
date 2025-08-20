"use client";

import React, { useState } from 'react';

type ProjectSettingsProps = {
  projectName: string;
  setProjectName: (name: string) => void;
  category: string;
  setCategory: (category: string) => void;
  description: string;
  setDescription: (description: string) => void;
  aiOptions: {
    autoClips: boolean;
    socialCaptions: boolean;
    hashtags: boolean;
  };
  setAiOptions: (options: {
    autoClips: boolean;
    socialCaptions: boolean;
    hashtags: boolean;
  }) => void;
};

export default function ProjectSettings({
  projectName,
  setProjectName,
  category,
  setCategory,
  description,
  setDescription,
  aiOptions,
  setAiOptions
}: ProjectSettingsProps) {
  const handleAiOptionChange = (option: keyof typeof aiOptions) => {
    setAiOptions({
      ...aiOptions,
      [option]: !aiOptions[option]
    });
  };

  return (
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
  );
}