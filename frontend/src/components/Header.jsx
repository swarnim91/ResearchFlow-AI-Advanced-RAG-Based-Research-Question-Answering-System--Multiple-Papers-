import React from 'react';

export default function Header({ indexed, paperCount }) {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="header-brand">
          <div className="header-logo">🔬</div>
          <div>
            <div className="header-title">ResearchFlow AI</div>
            <div className="header-subtitle">Intelligent Research Paper Analysis</div>
          </div>
        </div>

        <div className="header-status">
          <span
            className={`header-status-dot ${indexed ? 'active' : ''}`}
          />
          {indexed
            ? `${paperCount} paper${paperCount !== 1 ? 's' : ''} indexed`
            : 'No papers indexed'}
        </div>
      </div>
    </header>
  );
}
