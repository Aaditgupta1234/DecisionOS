import React from 'react';
import { MessageSquare, ArrowRight } from 'lucide-react';

interface Props {
  suggestions?: string[];
  onSelect?: (prompt: string) => void;
}

export const SuggestedFollowUps: React.FC<Props> = ({
  suggestions = [
    'Show impacted customer segments in Southeastern hubs',
    'Explain secondary warehouse logistics bottlenecks',
    'Model revenue recovery with Win-Back initiative',
    'Recommend top 3 actions for executive leadership',
  ],
  onSelect,
}) => {
  return (
    <div style={{ marginTop: '12px' }}>
      <div style={{ fontSize: '10.5px', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '5px' }}>
        <MessageSquare size={12} color="#38BDF8" />
        <span>Suggested Strategic Follow-Ups:</span>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
        {suggestions.map((s, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSelect && onSelect(s)}
            style={{
              background: '#0B0F17',
              border: '1px solid #1A2230',
              borderRadius: '6px',
              padding: '5px 10px',
              color: '#CBD5E1',
              fontSize: '11.5px',
              fontWeight: 500,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              transition: 'border-color 0.15s ease',
            }}
          >
            <span>• {s}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
