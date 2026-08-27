import React from 'react';
import { ShimmerBase } from './ShimmerBase';

export const KPICardSkeleton: React.FC = () => {
  return (
    <div
      style={{
        background: '#080A0E',
        border: '1px solid #1A1E26',
        borderRadius: '10px',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <ShimmerBase width="90px" height="12px" />
        <ShimmerBase width="36px" height="16px" borderRadius="10px" />
      </div>

      <ShimmerBase width="130px" height="26px" />

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <ShimmerBase width="55px" height="12px" />
        <ShimmerBase width="80px" height="12px" />
      </div>
    </div>
  );
};

export const ChartSkeleton: React.FC<{ height?: number }> = ({ height = 220 }) => {
  return (
    <div
      style={{
        background: '#080A0E',
        border: '1px solid #1A1E26',
        borderRadius: '12px',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <ShimmerBase width="140px" height="16px" />
          <ShimmerBase width="200px" height="11px" />
        </div>
        <ShimmerBase width="70px" height="24px" borderRadius="6px" />
      </div>

      <div style={{ height, display: 'flex', alignItems: 'flex-end', gap: '12px', paddingTop: '20px' }}>
        <ShimmerBase width="10%" height="45%" borderRadius="4px" />
        <ShimmerBase width="10%" height="70%" borderRadius="4px" />
        <ShimmerBase width="10%" height="55%" borderRadius="4px" />
        <ShimmerBase width="10%" height="90%" borderRadius="4px" />
        <ShimmerBase width="10%" height="60%" borderRadius="4px" />
        <ShimmerBase width="10%" height="80%" borderRadius="4px" />
        <ShimmerBase width="10%" height="40%" borderRadius="4px" />
        <ShimmerBase width="10%" height="75%" borderRadius="4px" />
        <ShimmerBase width="10%" height="95%" borderRadius="4px" />
        <ShimmerBase width="10%" height="65%" borderRadius="4px" />
      </div>
    </div>
  );
};

export const FindingsSkeleton: React.FC = () => {
  return (
    <div
      style={{
        background: '#080A0E',
        border: '1px solid #1A1E26',
        borderRadius: '12px',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
        <ShimmerBase width="160px" height="16px" />
        <ShimmerBase width="80px" height="16px" borderRadius="12px" />
      </div>

      {[1, 2, 3].map((i) => (
        <div
          key={i}
          style={{
            padding: '12px',
            background: '#0C0F15',
            border: '1px solid #161A22',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', width: '70%' }}>
            <ShimmerBase width="16px" height="16px" borderRadius="50%" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', width: '100%' }}>
              <ShimmerBase width="60%" height="13px" />
              <ShimmerBase width="90%" height="10px" />
            </div>
          </div>
          <ShimmerBase width="70px" height="20px" borderRadius="4px" />
        </div>
      ))}
    </div>
  );
};

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 4 }) => {
  return (
    <div
      style={{
        background: '#07090C',
        border: '1px solid #161A22',
        borderRadius: '12px',
        overflow: 'hidden',
      }}
    >
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr 1fr 1fr', padding: '14px 20px', background: '#0A0D12', borderBottom: '1px solid #1A1F29', gap: '12px' }}>
        <ShimmerBase width="80px" height="12px" />
        <ShimmerBase width="60px" height="12px" />
        <ShimmerBase width="60px" height="12px" />
        <ShimmerBase width="60px" height="12px" />
      </div>

      {Array.from({ length: rows }).map((_, idx) => (
        <div
          key={idx}
          style={{
            display: 'grid',
            gridTemplateColumns: '1.5fr 1fr 1fr 1fr',
            padding: '16px 20px',
            borderBottom: idx === rows - 1 ? 'none' : '1px solid #12151C',
            gap: '12px',
            alignItems: 'center',
          }}
        >
          <ShimmerBase width="75%" height="14px" />
          <ShimmerBase width="60%" height="12px" />
          <ShimmerBase width="60%" height="12px" />
          <ShimmerBase width="70%" height="14px" />
        </div>
      ))}
    </div>
  );
};

export const ChatSkeleton: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '16px 0' }}>
      <div style={{ display: 'flex', gap: '12px', alignSelf: 'flex-start', maxWidth: '75%' }}>
        <ShimmerBase width="28px" height="28px" borderRadius="50%" style={{ flexShrink: 0 }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <ShimmerBase width="180px" height="12px" />
          <ShimmerBase width="320px" height="14px" />
          <ShimmerBase width="260px" height="14px" />
        </div>
      </div>
    </div>
  );
};
