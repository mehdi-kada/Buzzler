import React from "react";
import UploadArea from "./UploadArea";

export type UploadFormProps = {
  /**
   * Optional title displayed above the upload area.
   * Defaults to "Upload video".
   */
  title?: string;

  /**
   * Optional subtitle / helper text displayed under the title.
   */
  subtitle?: string;

  /**
   * Additional className to apply to the outer container.
   */
  className?: string;
};

/**
 * UploadForm
 *
 * A lightweight wrapper around the upload area that keeps the public API
 * stable and provides a place to add consistent title/subtitle or future
 * behaviour (e.g. callbacks, analytics) without changing the area itself.
 *
 * The visual appearance is intentionally minimal and inline so it integrates
 * easily into existing layouts.
 */
export default function UploadForm({
  title = "Upload video",
  subtitle = "Drag & drop a video file or click to select. Supported: MP4, MOV, WEBM.",
  className,
}: UploadFormProps) {
  return (
    <div
      className={className}
      style={{
        width: "100%",
        maxWidth: 920,
        margin: "0 auto",
        boxSizing: "border-box",
      }}
    >
      <div style={{ marginBottom: 12 }}>
        <h2
          style={{
            margin: 0,
            fontSize: 20,
            fontWeight: 700,
            color: "#0f172a",
          }}
        >
          {title}
        </h2>
        {subtitle && (
          <div
            style={{
              marginTop: 6,
              color: "#475569",
              fontSize: 13,
            }}
          >
            {subtitle}
          </div>
        )}
      </div>

      <UploadArea />
    </div>
  );
}
