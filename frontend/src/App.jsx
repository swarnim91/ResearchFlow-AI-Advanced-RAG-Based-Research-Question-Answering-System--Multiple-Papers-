import React, { useState, useEffect, useCallback, useRef } from 'react';
import Header from './components/Header';
import UploadZone from './components/UploadZone';
import ChatPanel from './components/ChatPanel';
import { ChevronDown } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [files, setFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [indexed, setIndexed] = useState(false);
  const [paperCount, setPaperCount] = useState(0);
  const [toast, setToast] = useState(null);
  const [backendConnected, setBackendConnected] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const statusRetryRef = useRef(null);
  const isMobileRef = useRef(false);

  // Detect mobile
  useEffect(() => {
    const checkMobile = () => {
      isMobileRef.current = window.innerWidth <= 900;
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Robust fetch wrapper with timeout and retry
  const fetchWithTimeout = useCallback(async (url, options = {}, timeoutMs = 30000) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        throw new Error('Request timed out. The server may be starting up — please try again in a moment.');
      }
      throw new Error('Network error: Unable to connect to the server. Please check your connection and try again.');
    }
  }, []);

  // Check status on mount with retry
  const checkStatus = useCallback(async (retryCount = 0) => {
    try {
      const res = await fetchWithTimeout(`${API_BASE}/api/status`, {}, 15000);
      if (res.ok) {
        const data = await res.json();
        setIndexed(data.indexed);
        setPaperCount(data.paper_count);
        setBackendConnected(true);
        return true;
      }
      setBackendConnected(false);
      return false;
    } catch {
      setBackendConnected(false);
      // Auto-retry up to 3 times with exponential backoff
      if (retryCount < 3) {
        const delay = Math.min(2000 * Math.pow(2, retryCount), 10000);
        statusRetryRef.current = setTimeout(() => checkStatus(retryCount + 1), delay);
      }
      return false;
    }
  }, [fetchWithTimeout]);

  useEffect(() => {
    checkStatus();
    return () => {
      if (statusRetryRef.current) clearTimeout(statusRetryRef.current);
    };
  }, [checkStatus]);

  // Show toast
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 5000);
  };

  // Manual retry for connection
  const retryConnection = async () => {
    showToast('Reconnecting to server…', 'success');
    await checkStatus();
    if (!backendConnected) {
      showToast('Still unable to connect. The server may be sleeping — try again in 30 seconds.', 'error');
    }
  };

  // Upload and process papers
  const handleProcess = async () => {
    if (files.length === 0) return;
    setProcessing(true);

    try {
      const formData = new FormData();
      files.forEach((file) => formData.append('files', file));

      // Use longer timeout for upload (5 minutes for large PDFs + processing)
      const res = await fetchWithTimeout(
        `${API_BASE}/api/upload`,
        {
          method: 'POST',
          body: formData,
        },
        300000 // 5 minute timeout for processing
      );

      let data;
      if (!res.ok) {
        let errorMsg = `Upload failed (Status: ${res.status})`;
        try {
          const text = await res.text();
          try {
            const json = JSON.parse(text);
            if (json.detail) errorMsg = json.detail;
          } catch {
            if (text.includes('<html') || text.includes('<HTML')) {
              errorMsg = `Server Error (${res.status}): The backend might be overloaded or timed out. Try with fewer/smaller files.`;
            } else if (text) {
              errorMsg = text.substring(0, 200);
            }
          }
        } catch {
          // Couldn't read response body
        }
        throw new Error(errorMsg);
      }

      const textData = await res.text();
      try {
        data = JSON.parse(textData);
      } catch {
        throw new Error(`Invalid JSON response from server. The server may be under heavy load.`);
      }

      showToast(`${data.count} paper${data.count !== 1 ? 's' : ''} indexed successfully!`);
      setIndexed(true);
      setPaperCount(data.count);
      setFiles([]);
      setBackendConnected(true);

      // Auto-close sidebar on mobile after successful processing
      if (isMobileRef.current) {
        setSidebarOpen(false);
      }
    } catch (err) {
      showToast(err.message, 'error');
      // If it's a network error, mark backend as disconnected
      if (err.message.includes('Network error') || err.message.includes('timed out')) {
        setBackendConnected(false);
      }
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="app-layout">
      <Header indexed={indexed} paperCount={paperCount} />

      {/* Connection warning banner */}
      {!backendConnected && (
        <div className="connection-banner">
          ⚠️ Unable to reach the server.
          <button onClick={retryConnection}>Retry</button>
        </div>
      )}

      {/* Mobile toggle for upload panel */}
      <button
        className="mobile-upload-toggle"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        📄 Upload Papers
        <span className={`mobile-upload-toggle-icon ${sidebarOpen ? 'open' : ''}`}>
          <ChevronDown size={18} />
        </span>
      </button>

      <main className="app-main">
        <UploadZone
          files={files}
          setFiles={setFiles}
          onProcess={handleProcess}
          processing={processing}
          indexed={indexed}
          mobileHidden={!sidebarOpen}
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
