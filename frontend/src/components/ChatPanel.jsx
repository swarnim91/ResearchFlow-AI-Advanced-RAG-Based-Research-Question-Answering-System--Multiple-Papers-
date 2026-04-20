import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Search, BookOpen, Lightbulb } from 'lucide-react';
import CitedPapers from './CitedPapers';

const API_BASE = import.meta.env.VITE_API_URL || '';

const SUGGESTIONS = [
  'What are the key findings?',
  'Summarize the methodology',
  'What limitations are discussed?',
  'Compare the approaches used',
];

export default function ChatPanel({ indexed }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const sendQuestion = async (question) => {
    const q = question || input.trim();
    if (!q || loading) return;

    // Add user message
    setMessages((prev) => [...prev, { role: 'user', content: q }]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      });

      let data;
      try {
        if (!res.ok) {
          let errorMsg = `Error (Status: ${res.status})`;
          try {
            const text = await res.text();
            try {
              const json = JSON.parse(text);
              if (json.detail) errorMsg = json.detail;
            } catch {
              if (text.includes('<html')) {
                errorMsg = `Server Error (${res.status}): The backend might be overloaded.`;
              } else if (text) {
                errorMsg = text;
              }
            }
          } catch (e) {}
          throw new Error(errorMsg);
        }

        const textData = await res.text();
        try {
          data = JSON.parse(textData);
        } catch (e) {
          throw new Error(`Invalid response from server: ${textData.substring(0, 50)}...`);
        }
      } catch (err) {
        throw new Error(err.message || 'Something went wrong');
      }

      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content: data.answer,
          cited_papers: data.cited_papers,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'ai',
          content: `⚠️ ${err.message}`,
          cited_papers: {},
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendQuestion();
    }
  };

  // Format answer text into paragraphs
  const formatAnswer = (text) => {
    return text
      .split('\n')
      .filter((line) => line.trim())
      .map((para, i) => <p key={i}>{para}</p>);
  };

  return (
    <div className="chat-panel">
      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 && !loading && (
          <div className="chat-empty">
            <div className="chat-empty-icon">
              <Sparkles size={56} strokeWidth={1.2} color="var(--accent-primary)" />
            </div>
            <h1 className="chat-empty-title">Ask your research papers</h1>
            <p className="chat-empty-text">
              {indexed
                ? 'Your papers are indexed and ready. Ask any research question and get AI-synthesized answers with citations.'
                : 'Upload and process your research papers first, then ask questions across all of them.'}
            </p>
            {indexed && (
              <div className="chat-empty-suggestions">
                {SUGGESTIONS.map((s) => (
                  <button
                    className="chat-suggestion"
                    key={s}
                    onClick={() => sendQuestion(s)}
                  >
                    <Lightbulb size={12} style={{ marginRight: 4 }} />
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {messages.map((msg, i) =>
          msg.role === 'user' ? (
            <div className="message message-user" key={i}>
              <div className="message-bubble">{msg.content}</div>
            </div>
          ) : (
            <div className="message message-ai" key={i}>
              <div className="message-ai-label">
                <span className="message-ai-dot">✦</span>
                ResearchFlow AI
              </div>
              <div className="message-bubble">{formatAnswer(msg.content)}</div>
              {msg.cited_papers && <CitedPapers papers={msg.cited_papers} />}
            </div>
          )
        )}

        {loading && (
          <div className="message message-ai animate-fade-in">
            <div className="message-ai-label">
              <span className="message-ai-dot">✦</span>
              ResearchFlow AI
            </div>
            <div className="message-bubble">
              <div className="typing-indicator">
                <span />
                <span />
                <span />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div className="chat-input-bar">
        <div className="chat-input-wrapper">
          <input
            ref={inputRef}
            className="chat-input"
            type="text"
            placeholder={
              indexed
                ? 'Ask a research question…'
                : 'Upload and process papers first…'
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!indexed || loading}
            id="question-input"
          />
          <button
            className="chat-send-btn"
            onClick={() => sendQuestion()}
            disabled={!indexed || loading || !input.trim()}
            id="send-question-btn"
            title="Send question"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
