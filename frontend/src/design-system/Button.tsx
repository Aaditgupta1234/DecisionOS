import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  style,
  disabled,
  ...props
}) => {
  const getStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: '#38BDF8',
          color: '#090D14',
          border: 'none',
          fontWeight: 800,
        };
      case 'secondary':
        return {
          backgroundColor: 'rgba(56, 189, 248, 0.1)',
          color: '#38BDF8',
          border: '1px solid rgba(56, 189, 248, 0.3)',
          fontWeight: 700,
        };
      case 'danger':
        return {
          backgroundColor: 'rgba(239, 68, 68, 0.15)',
          color: '#EF4444',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          fontWeight: 700,
        };
      case 'ghost':
      default:
        return {
          backgroundColor: 'transparent',
          color: '#94A3B8',
          border: '1px solid #1E293B',
          fontWeight: 600,
        };
    }
  };

  const getPadding = () => {
    switch (size) {
      case 'sm':
        return '6px 12px';
      case 'lg':
        return '12px 24px';
      case 'md':
      default:
        return '8px 16px';
    }
  };

  return (
    <button
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '6px',
        borderRadius: '8px',
        fontSize: size === 'sm' ? '0.75rem' : size === 'lg' ? '0.95rem' : '0.82rem',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        transition: 'all 0.15s ease',
        padding: getPadding(),
        ...getStyles(),
        ...style,
      }}
      disabled={disabled}
      {...props}
    >
      {icon && <span style={{ display: 'flex', alignItems: 'center' }}>{icon}</span>}
      {children}
    </button>
  );
};
