import React, { useState } from 'react';
import { FileText, Download, ShieldCheck, CheckCircle2, FileSpreadsheet, Presentation, FileCode } from 'lucide-react';

export const ExecutiveReportsCenterView: React.FC = () => {
  const [selectedFormat, setSelectedFormat] = useState<'PDF' | 'PPTX' | 'JSON' | 'CSV'>('PDF');
  const [isExporting, setIsExporting] = useState(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  const reports = [
    {
      id: 'REP-001',
      title: 'Q4 Executive Briefing',
      type: 'EXECUTIVE_BRIEFING',
      desc: 'One-page C-suite summary of portfolio health, top risks, and immediate remedial directives.',
      updated: 'Today at 2:00 PM',
    },
    {
      id: 'REP-002',
      title: 'Comprehensive Boardroom Report',
      type: 'BOARD_REPORT',
      desc: 'Full multi-section governance deck covering forecast reliability, digital twin simulations, and AI recommendations.',
      updated: 'Yesterday at 5:30 PM',
    },
    {
      id: 'REP-003',
      title: '30/60/90/180-Day Autonomous Recovery Plan',
      type: 'RECOVERY_PLAN',
      desc: 'Phased timeline of initiatives, milestone dependencies, and ARR recovery milestones.',
      updated: '2 days ago',
    },
  ];

  const handleExport = (reportTitle: string) => {
    setIsExporting(true);
    setExportMessage(null);
    setTimeout(() => {
      setIsExporting(false);
      setExportMessage(`Successfully compiled and downloaded "${reportTitle}" as ${selectedFormat}.`);
    }, 800);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#06B6D4', fontWeight: 800 }}>
            Boardroom Governance & Presentation Generation
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Executive Reporting Center
          </h1>
        </div>

        {/* Format Selector Pills */}
        <div style={{ display: 'flex', gap: '6px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', padding: '4px', borderRadius: '8px' }}>
          {(['PDF', 'PPTX', 'JSON', 'CSV'] as const).map((fmt) => (
            <button
              key={fmt}
              onClick={() => setSelectedFormat(fmt)}
              style={{
                padding: '6px 12px',
                borderRadius: '6px',
                border: 'none',
                background: selectedFormat === fmt ? '#0284C7' : 'transparent',
                color: selectedFormat === fmt ? '#FFFFFF' : '#94A3B8',
                fontSize: '0.78rem',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              {fmt}
            </button>
          ))}
        </div>
      </div>

      {exportMessage && (
        <div style={{ padding: '12px 16px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', color: '#10B981', fontSize: '0.85rem', fontWeight: 600 }}>
          ✓ {exportMessage}
        </div>
      )}

      {/* Reports Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
        {reports.map((rep) => (
          <div
            key={rep.id}
            style={{
              background: '#090D14',
              border: '1px solid #1E293B',
              borderRadius: '12px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.7rem', color: '#38BDF8', fontWeight: 800, textTransform: 'uppercase' }}>
                {rep.type}
              </span>
              <span style={{ fontSize: '0.72rem', color: '#64748B' }}>{rep.updated}</span>
            </div>

            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFFFFF' }}>{rep.title}</div>
            <div style={{ fontSize: '0.85rem', color: '#94A3B8', lineHeight: 1.5 }}>{rep.desc}</div>

            <div style={{ marginTop: 'auto', borderTop: '1px solid #1E293B', paddingTop: '16px', display: 'flex', gap: '10px' }}>
              <button
                onClick={() => handleExport(rep.title)}
                disabled={isExporting}
                style={{
                  flex: 1,
                  padding: '10px 16px',
                  background: '#0284C7',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#FFFFFF',
                  fontSize: '0.82rem',
                  fontWeight: 700,
                  cursor: isExporting ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                }}
              >
                <Download size={14} />
                <span>{isExporting ? 'Generating...' : `Export as ${selectedFormat}`}</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
