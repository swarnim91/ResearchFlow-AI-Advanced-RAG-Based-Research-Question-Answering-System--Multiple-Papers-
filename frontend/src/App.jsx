import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import UploadZone from './components/UploadZone';
import ChatPanel from './components/ChatPanel';

const API_BASE = '';

export default function App() {
  const [files, setFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [indexed, setIndexed] = useState(false);
  const [paperCount, setPaperCount] = useState(0);
  const [toast, setToast] = useState(null);

  // Check status on mount
  const checkStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/status`);
      if (res.ok) {
        const data = await res.json();
        setIndexed(data.indexed);
        setPaperCount(data.paper_count);
      }
    } catch {
      // Backend not running yet — that's OK
    }
  }, []);

  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  // Show toast
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Upload and process papers
  const handleProcess = async () => {
    if (files.length === 0) return;
    setProcessing(true);

    try {
      const formData = new FormData();
      files.forEach((file) => formData.append('files', file));

      const res = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Upload failed');
      }

      const data = await res.json();
      showToast(`${data.count} paper${data.count !== 1 ? 's' : ''} indexed successfully!`);
      setIndexed(true);
      setPaperCount(data.count);
      setFiles([]);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="app-layout">
      <Header indexed={indexed} paperCount={paperCount} />

      <main className="app-main">
        <UploadZone
          files={files}
          setFiles={setFiles}
          onProcess={handleProcess}
          processing={processing}
          indexed={indexed}
        />
        <ChatPanel indexed={indexed} />
      </main>

      {/* Toast */}
      {toast && (
        <div className={`toast ${toast.type}`}>
          {toast.type === 'success' ? '✓' : '⚠'}
          {toast.message}
        </div>
      )}

      {/* Footer */}
      <footer className="app-footer">
        Designed by <span className="footer-name">Swarnim Sugandh</span> &copy; {new Date().getFullYear()}
      </footer>
    </div>
  );
}
