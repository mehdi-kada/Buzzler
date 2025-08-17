import React from "react";
import { useUploadStore } from "../../lib/store/uploadStore";

type ProgressBarProps = {
  // optional callback when user cancels the upload
  onCancel?: () => void;
  // whether to show the component even when not uploading (defaults to false)
  persist?: boolean;
};

const containerStyle: React.CSSProperties = {
  width: "100%",
  maxWidth: 720,
  margin: "8px 0",
  padding: 12,
  borderRadius: 8,
  background: "#f5f7fb",
  boxShadow: "inset 0 0 0 1px rgba(16,24,40,0.04)",
  display: "flex",
  alignItems: "center",
  gap: 12,
  boxSizing: "border-box",
};

const barOuterStyle: React.CSSProperties = {
  flex: 1,
  height: 12,
  borderRadius: 999,
  background: "#e6eef8",
  overflow: "hidden",
};

const barInnerStyle = (percent: number): React.CSSProperties => ({
  width: `${percent}%`,
  height: "100%",
  background: "linear-gradient(90deg,#2563eb,#06b6d4)",
  transition: "width 200ms linear",
});

const metaStyle: React.CSSProperties = {
  minWidth: 180,
  maxWidth: 260,
  display: "flex",
  flexDirection: "column",
  gap: 4,
  fontSize: 13,
  color: "#102240",
  overflow: "hidden",
  textOverflow: "ellipsis",
  whiteSpace: "nowrap",
};

const rightColStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 8,
};

const percentTextStyle: React.CSSProperties = {
  fontSize: 13,
  minWidth: 48,
  textAlign: "right",
  color: "#0f172a",
};

const cancelButtonStyle: React.CSSProperties = {
  border: "none",
  background: "transparent",
  color: "#ef4444",
  cursor: "pointer",
  fontSize: 13,
  padding: "6px 8px",
  borderRadius: 6,
};

export default function ProgressBar({
  onCancel,
  persist = false,
}: ProgressBarProps) {
  const { progress, isUploading, fileName, setUploading } = useUploadStore(
    (state) => ({
      progress: state.progress,
      isUploading: state.isUploading,
      fileName: state.fileName,
      setUploading: state.setUploading,
    }),
  );

  // If not uploading and not persisting, render nothing
  if (!isUploading && !persist) {
    return null;
  }

  const handleCancel = () => {
    // signal to store that upload has stopped; this will also reset progress & file info
    setUploading(false);
    if (onCancel) {
      try {
        onCancel();
      } catch {
        // swallow errors from callback
      }
    }
  };

  const displayName = fileName || "Uploading file";

  return (
    <div style={containerStyle} role="status" aria-live="polite">
      <div style={metaStyle}>
        <div
          style={{
            fontWeight: 600,
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {displayName}
        </div>
        <div style={{ fontSize: 12, color: "#475569" }}>
          {isUploading ? "Uploading…" : "Upload paused"}
        </div>
      </div>

      <div style={barOuterStyle} aria-hidden>
        <div
          style={barInnerStyle(progress)}
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.max(0, Math.min(100, Math.round(progress)))}
          aria-label="File upload progress"
        />
      </div>

      <div style={rightColStyle}>
        <div style={percentTextStyle}>
          {Math.max(0, Math.min(100, Math.round(progress)))}%
        </div>
        <button
          type="button"
          onClick={handleCancel}
          title="Cancel upload"
          style={cancelButtonStyle}
          aria-label="Cancel upload"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
