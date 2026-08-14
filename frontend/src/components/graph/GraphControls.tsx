import React from 'react';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Filter, Eye } from 'lucide-react';

interface GraphControlsProps {
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitView: () => void;
  onReset: () => void;
  selectedCategory: string;
  onSelectCategory: (cat: string) => void;
  selectedSeverity: string;
  onSelectSeverity: (sev: string) => void;
  categories: string[];
  highlightRootsOnly: boolean;
  onToggleRootsOnly: () => void;
}

export const GraphControls: React.FC<GraphControlsProps> = ({
  zoom,
  onZoomIn,
  onZoomOut,
  onFitView,
  onReset,
  selectedCategory,
  onSelectCategory,
  selectedSeverity,
  onSelectSeverity,
  categories,
  highlightRootsOnly,
  onToggleRootsOnly,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '12px',
        padding: '10px 16px',
        backgroundColor: 'var(--bg-surface-elevated)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-md)',
        marginBottom: '16px',
      }}
    >
      {/* Zoom & Canvas Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <button
          onClick={onZoomIn}
          className="btn btn-secondary btn-sm"
          title="Zoom In"
          aria-label="Zoom In"
        >
          <ZoomIn size={14} />
        </button>
        <button
          onClick={onZoomOut}
          className="btn btn-secondary btn-sm"
          title="Zoom Out"
          aria-label="Zoom Out"
        >
          <ZoomOut size={14} />
        </button>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', minWidth: '42px', textAlign: 'center' }}>
          {Math.round(zoom * 100)}%
        </span>
        <button
          onClick={onFitView}
          className="btn btn-secondary btn-sm"
          title="Fit Graph to View"
          aria-label="Fit Graph to View"
        >
          <Maximize2 size={14} />
          <span>Fit</span>
        </button>
        <button
          onClick={onReset}
          className="btn btn-ghost btn-sm"
          title="Reset Zoom & Pan"
          aria-label="Reset Zoom and Pan"
        >
          <RotateCcw size={14} />
        </button>
      </div>

      {/* Filter Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        {/* Severity Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Severity:</span>
          <select
            value={selectedSeverity}
            onChange={(e) => onSelectSeverity(e.target.value)}
            className="select"
            style={{ padding: '4px 8px', fontSize: '0.75rem', height: '28px' }}
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>

        {/* Category Filter */}
        {categories.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Domain:</span>
            <select
              value={selectedCategory}
              onChange={(e) => onSelectCategory(e.target.value)}
              className="select"
              style={{ padding: '4px 8px', fontSize: '0.75rem', height: '28px' }}
            >
              <option value="ALL">All Domains</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Highlight Root Origins Toggle */}
        <button
          onClick={onToggleRootsOnly}
          className={`btn btn-sm ${highlightRootsOnly ? 'btn-primary' : 'btn-secondary'}`}
          style={{ height: '28px', fontSize: '0.75rem', gap: '4px' }}
        >
          <Eye size={12} />
          <span>Root Causes Only</span>
        </button>
      </div>
    </div>
  );
};
