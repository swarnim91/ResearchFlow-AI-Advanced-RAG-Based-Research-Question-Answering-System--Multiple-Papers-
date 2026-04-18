import React from 'react';
import { BookOpen, User, Calendar } from 'lucide-react';

export default function CitedPapers({ papers }) {
  if (!papers || Object.keys(papers).length === 0) return null;

  return (
    <div className="cited-papers">
      <p className="cited-papers-title">
        <BookOpen size={14} />
        Referenced Papers
      </p>

      {Object.entries(papers).map(([filename, meta]) => (
        <div className="cited-card" key={filename}>
          <div className="cited-card-icon">
            <BookOpen size={18} />
          </div>
          <div className="cited-card-info">
            <div className="cited-card-title">
              {meta.title || filename}
            </div>
            <div className="cited-card-meta">
              <span>
                <User size={12} />
                {meta.authors || 'Unknown'}
              </span>
              <span>
                <Calendar size={12} />
                {meta.year || 'Unknown'}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
