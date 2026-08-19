import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'emerald' | 'sky' | 'amber' | 'rose' | 'purple' | 'slate';
  size?: 'sm' | 'md';
  style?: React.CSSProperties;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'slate', size = 'md', style }) => {
  const getColors = () => {
    switch (variant) {
      case 'emerald':
        return { bg: 'rgba(16, 185, 129, 0.15)', color: '#10B981', border: 'rgba(16, 185, 129, 0.3)' };
      case 'sky':
        return { bg: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8', border: 'rgba(56, 189, 248, 0.3)' };
      case 'amber':
        return { bg: 'rgba(245, 158, 11, 0.15)', color: '#F59E0B', border: 'rgba(245, 158, 11, 0.3)' };
      case 'rose':
        return { bg: 'rgba(239, 68, 68, 0.15)', color: '#EF4444', border: 'rgba(239, 68, 68, 0.3)' };
      case 'purple':
        return { bg: 'rgba(168, 85, 247, 0.15)', color: '#A855F7', border: 'rgba(168, 85, 247, 0.3)' };
      case 'slate':
      default:
        return { bg: 'rgba(100, 116, 139, 0.15)', color: '#94A3B8', border: '#334155' };
    }
  };

  const colors = getColors();

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: size === 'sm' ? '2px 6px' : '3px 8px',
        borderRadius: '5px',
        fontSize: size === 'sm' ? '0.68rem' : '0.74rem',
        fontWeight: 800,
        textTransform: 'uppercase',
        letterSpacing: '0.04em',
        backgroundColor: colors.bg,
        color: colors.color,
        border: `1px solid ${colors.border}`,
        ...style,
      }}
    >
      {children}
    </span>
  );
};
