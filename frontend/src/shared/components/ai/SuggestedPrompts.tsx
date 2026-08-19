import React from 'react';
import { MessageSquare, Sparkles } from 'lucide-react';

interface Props {
  onSelectPrompt: (prompt: string) => void;
}

export const SuggestedPrompts: React.FC<Props> = ({ onSelectPrompt }) => {
  const prompts = [
    'Why did customer retention decline in Southeastern logistics routes?',
    'What is our largest business risk and financial exposure?',
    'Which recommendation delivers the highest ROI and recovery ARR?',
    'Summarize our overall business health in 30 seconds.',
    'What caused the delivery time increase across secondary hubs?',
    'What initiatives are currently pending in the action matrix?',
  ];

  return (
    <div style={{ padding: '24px 0', textAlign: 'center' }}>
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '8px', color: '#38BDF8', fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        <Sparkles size={14} />
        <span>Executive Intelligence Prompt Starters</span>
      </div>

      <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#FFFFFF', margin: '0 0 16px' }}>
        Ask any strategic, operational, or diagnostic question
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', maxWidth: '800px', margin: '0 auto', textAlign: 'left' }}>
        {prompts.map((p, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSelectPrompt(p)}
            style={{
              background: '#090D14',
              border: '1px solid #1A2230',
              borderRadius: '8px',
              padding: '12px 14px',
              color: '#CBD5E1',
              fontSize: '12px',
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              textAlign: 'left',
              transition: 'all 0.15s ease',
            }}
          >
            <MessageSquare size={13} color="#38BDF8" style={{ flexShrink: 0 }} />
            <span>{p}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
