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
        backgroundColor: '#090D14',
        border: '1px solid #1E293B',
        borderRadius: '14px',
        padding: '20px',
        transition: 'border-color 0.2s ease, transform 0.2s ease',
        cursor: onClick ? 'pointer' : 'default',
        ...style,
      }}
    >
      {children}
    </div>
  );
};
