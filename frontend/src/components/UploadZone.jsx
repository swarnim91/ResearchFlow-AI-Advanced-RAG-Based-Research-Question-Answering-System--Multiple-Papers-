import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileText, X, Upload } from 'lucide-react';

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export default function UploadZone({
  files,
  setFiles,
  onProcess,
  processing,
  indexed,
  mobileHidden,
}) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      // Avoid duplicates
      setFiles((prev) => {
        const existing = new Set(prev.map((f) => f.name));
        const newFiles = acceptedFiles.filter((f) => !existing.has(f.name));
        return [...prev, ...newFiles];
      });
    },
    [setFiles]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: true,
  });

  const removeFile = (name) => {
    setFiles((prev) => prev.filter((f) => f.name !== name));
  };

  return (
    <div className={`sidebar ${mobileHidden ? 'mobile-hidden' : ''}`}>
      {/* Section title */}
      <p className="sidebar-section-title">Upload Papers</p>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`upload-zone ${isDragActive ? 'drag-active' : ''}`}
        id="upload-drop-zone"
      >
        <input {...getInputProps()} />
        <div className="upload-zone-icon">
          <Upload size={40} strokeWidth={1.5} color="var(--accent-primary)" />
        </div>
        <p className="upload-zone-text">
          <strong>Drop PDFs here</strong> or click to browse
        </p>
        <p className="upload-zone-hint">Supports multiple PDF files</p>
      </div>

      {/* File list */}
      {files.length > 0 && (
        <>
          <p className="sidebar-section-title">
            Selected Files ({files.length})
          </p>
          <div className="file-list">
            {files.map((file, i) => (
              <div
                className="file-item"
                key={file.name}
                style={{ animationDelay: `${i * 60}ms` }}
              >
                <div className="file-item-icon">
                  <FileText size={18} />
                </div>
                <div className="file-item-info">
                  <div className="file-item-name">{file.name}</div>
                  <div className="file-item-size">{formatBytes(file.size)}</div>
                </div>
                <button
                  className="file-item-remove"
                  onClick={() => removeFile(file.name)}
                  title="Remove file"
                >
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>

          {/* Process button */}
          <button
            className={`btn btn-primary btn-full ${processing ? 'btn-loading' : ''}`}
            onClick={onProcess}
            disabled={processing || files.length === 0}
            id="process-papers-btn"
          >
            {processing ? (
              <>
                <span className="spinner" />
                Processing…
              </>
            ) : (
              <>
                <Upload size={16} />
                Process {files.length} Paper{files.length !== 1 ? 's' : ''}
              </>
            )}
          </button>
        </>
      )}

      {/* Status when indexed */}
      {indexed && (
        <div className="status-badge success">
          <span style={{ fontSize: '0.9rem' }}>✓</span>
          Papers indexed &amp; ready
        </div>
      )}
    </div>
  );
}
