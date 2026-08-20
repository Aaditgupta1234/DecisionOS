import React from 'react';

interface CardProps {
  children: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, style, className, onClick, hoverable }) => {
  return (
    <div
      onClick={onClick}
      className={className}
      style={{
        backgroundColor: '#080A0F',
        border: '1px solid #14171E',
        borderRadius: '14px',
        padding: '20px',
        transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)',
        cursor: onClick ? 'pointer' : 'default',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.45)',
        ...style,
      }}
    >
      {children}
    </div>
  );
};
