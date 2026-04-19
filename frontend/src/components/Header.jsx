import React from 'react';
import logoImg from '../assets/logo.png';

export default function Header({ indexed, paperCount }) {
  return (
    <header className="header">
      <div className="header-inner">
        <div className="header-brand">
          <img
            src={logoImg}
            alt="ResearchFlow AI Logo"
            className="header-logo-img"
          />
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
