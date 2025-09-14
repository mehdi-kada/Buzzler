"use client";

import React, { useState } from "react";
import { toast } from "sonner";


type VideoImportProps = {
  onImportStart?: (url: string) => void;
  isImporting?: boolean;
};

export default function VideoImport({
  onImportStart,
  isImporting,
}: VideoImportProps) {
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
    onImportStart?.(url);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleImport();
    }
  };

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
          disabled={isImporting}
        />
      </div>

      <button
        className={`btn-primary px-6 py-3 rounded-lg font-semibold ${
          isImporting || !url.trim() ? "opacity-60 cursor-not-allowed" : ""
        }`}
        onClick={handleImport}
        disabled={isImporting || !url.trim()}
      >
        {isImporting ? "Importing..." : "Import Video"}
      </button>
    </div>
  );
}
