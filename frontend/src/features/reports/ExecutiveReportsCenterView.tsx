import React, { useState } from 'react';
import {
  FileText,
  Download,
  ShieldCheck,
  Presentation,
  GitCompare,
  Network,
  History,
  CheckCircle2,
  Sparkles,
  Eye,
  FileCheck,
  Zap,
} from 'lucide-react';
import { PresentationDeckViewerModal } from './PresentationDeckViewerModal';
import { ReportLineageGraphModal } from './ReportLineageGraphModal';
import { ReportVersionDiffModal } from './ReportVersionDiffModal';
import { BoardDirectivesPanel } from './BoardDirectivesPanel';
import { ReportAuditTrailModal } from './ReportAuditTrailModal';
import { ReportSignOffModal } from './ReportSignOffModal';

export const ExecutiveReportsCenterView: React.FC = () => {
  const [selectedPersona, setSelectedPersona] = useState('ALL');
  const [selectedFormat, setSelectedFormat] = useState<'PDF' | 'PPTX' | 'JSON' | 'CSV'>('PDF');
  const [isExporting, setIsExporting] = useState(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  // Modals state
  const [isDeckOpen, setIsDeckOpen] = useState(false);
  const [isLineageOpen, setIsLineageOpen] = useState(false);
  const [isDiffOpen, setIsDiffOpen] = useState(false);
  const [isAuditOpen, setIsAuditOpen] = useState(false);
  const [isSignOffOpen, setIsSignOffOpen] = useState(false);
  const [activeReportTitle, setActiveReportTitle] = useState('DecisionOS Q4 Comprehensive Boardroom Governance Report');

  const reports = [
    {
      id: 'REP-001',
      title: 'DecisionOS Q4 Comprehensive Boardroom Governance Report',
      persona: 'BOARD',
      type: 'BOARD_REPORT',
      desc: 'Full multi-section fiduciary deck covering portfolio health lift (85.0), rolling forecast accuracy (88.4%), and ratified directives.',
      qualityScore: 96.8,
      citationCoverage: 100.0,
      generationTime: '340ms',
      snapshot: 'Snapshot V3',
      status: 'PUBLISHED',
      updated: 'Today at 2:45 PM',
    },
    {
      id: 'REP-002',
      title: 'CEO Strategic State & ARR Trajectory Briefing',
      persona: 'CEO',
      type: 'EXECUTIVE_BRIEFING',
      desc: 'One-page strategic overview detailing +$124K ARR recovery velocity and 91.4% brand trust index.',
      qualityScore: 95.5,
      citationCoverage: 98.4,
      generationTime: '280ms',
      snapshot: 'Snapshot V3',
      status: 'APPROVED',
      updated: 'Today at 2:15 PM',
    },
    {
      id: 'REP-003',
      title: 'COO Operational Logistics & Courier SLA Briefing',
      persona: 'COO',
      type: 'EXECUTIVE_BRIEFING',
      desc: 'Operational summary on Secondary Hub dispatch bottlenecks and 91.2% courier SLA compliance.',
      qualityScore: 97.1,
      citationCoverage: 100.0,
      generationTime: '310ms',
      snapshot: 'Snapshot V3',
      status: 'APPROVED',
      updated: 'Today at 1:30 PM',
    },
    {
      id: 'REP-004',
      title: 'CFO Financial Recovery & Capital Efficiency Summary',
      persona: 'CFO',
      type: 'EXECUTIVE_BRIEFING',
      desc: 'Financial recovery breakdown: +$124K realized ARR on $25,800 cost (4.8x ROI multiplier).',
      qualityScore: 96.4,
      citationCoverage: 100.0,
      generationTime: '290ms',
      snapshot: 'Snapshot V3',
      status: 'PUBLISHED',
      updated: 'Yesterday at 4:00 PM',
    },
    {
      id: 'REP-005',
      title: '30/60/90/180-Day Autonomous Recovery Roadmap',
      persona: 'BOARD',
      type: 'RECOVERY_PLAN',
      desc: 'Phased strategic timeline recovering $480,000 in annualized ARR across four distinct execution horizons.',
      qualityScore: 98.0,
      citationCoverage: 100.0,
      generationTime: '410ms',
      snapshot: 'Snapshot V3',
      status: 'PUBLISHED',
      updated: '2 days ago',
    },
  ];

  const filteredReports = selectedPersona === 'ALL'
    ? reports
    : reports.filter((r) => r.persona === selectedPersona);

  const handleExport = (reportTitle: string) => {
    setIsExporting(true);
    setExportMessage(null);
    setTimeout(() => {
      setIsExporting(false);
      setExportMessage(`Successfully compiled and exported "${reportTitle}" as ${selectedFormat}.`);
    }, 800);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#06B6D4', fontWeight: 800 }}>
            Boardroom Governance & Fiduciary Communication Layer
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Executive Reporting & Boardroom Communication
          </h1>
        </div>

        {/* Multi-Format Export Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>Export Format:</span>
          <div style={{ display: 'flex', gap: '4px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', padding: '4px', borderRadius: '8px' }}>
            {(['PDF', 'PPTX', 'JSON', 'CSV'] as const).map((fmt) => (
              <button
                key={fmt}
                onClick={() => setSelectedFormat(fmt)}
                style={{
                  padding: '5px 12px',
                  borderRadius: '6px',
                  border: 'none',
                  background: selectedFormat === fmt ? '#0284C7' : 'transparent',
                  color: selectedFormat === fmt ? '#FFFFFF' : '#94A3B8',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                {fmt}
              </button>
            ))}
          </div>
        </div>
      </div>

      {exportMessage && (
        <div style={{ padding: '12px 16px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', color: '#10B981', fontSize: '0.85rem', fontWeight: 600 }}>
          ✓ {exportMessage}
        </div>
      )}

      {/* 4-Factor Narrative Confidence Bar */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '18px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={16} color="#A855F7" />
          <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            4-Factor Executive Narrative Confidence:
          </span>
        </div>

        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          <div>
            <span style={{ fontSize: '0.72rem', color: '#64748B' }}>Telemetry: </span>
            <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#10B981' }}>95%</span>
          </div>
          <div>
            <span style={{ fontSize: '0.72rem', color: '#64748B' }}>Graph Topology: </span>
            <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#38BDF8' }}>92%</span>
          </div>
          <div>
            <span style={{ fontSize: '0.72rem', color: '#64748B' }}>Causal Lineage: </span>
            <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#A855F7' }}>87%</span>
          </div>
          <div>
            <span style={{ fontSize: '0.72rem', color: '#64748B' }}>Outcome Validation: </span>
            <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#F59E0B' }}>89%</span>
          </div>
          <div style={{ borderLeft: '1px solid #1E293B', paddingLeft: '16px' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B' }}>Composite: </span>
            <span style={{ fontSize: '0.85rem', fontWeight: 900, color: '#38BDF8' }}>91.0%</span>
          </div>
        </div>
      </div>

      {/* Persona Filter Tabs */}
      <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', padding: '6px', borderRadius: '8px' }}>
        {[
          { key: 'ALL', label: 'All Reports & Briefings' },
          { key: 'BOARD', label: 'Board Governance Decks' },
          { key: 'CEO', label: 'CEO Strategic Briefings' },
          { key: 'COO', label: 'COO Operational Summaries' },
          { key: 'CFO', label: 'CFO Financial Summaries' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setSelectedPersona(tab.key)}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              border: 'none',
              background: selectedPersona === tab.key ? '#0284C7' : 'transparent',
              color: selectedPersona === tab.key ? '#FFFFFF' : '#94A3B8',
              fontSize: '0.78rem',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Reports Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '18px' }}>
        {filteredReports.map((rep) => (
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
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.68rem', fontWeight: 800, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', padding: '2px 8px', borderRadius: '4px', textTransform: 'uppercase' }}>
                  {rep.persona} • {rep.type}
                </span>
                <span style={{ fontSize: '0.68rem', color: '#10B981', fontWeight: 700 }}>
                  ★ {rep.qualityScore} Quality
                </span>
              </div>
              <span
                style={{
                  fontSize: '0.7rem',
                  fontWeight: 800,
                  padding: '3px 8px',
                  borderRadius: '12px',
                  background: rep.status === 'PUBLISHED' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(56, 189, 248, 0.15)',
                  color: rep.status === 'PUBLISHED' ? '#10B981' : '#38BDF8',
                }}
              >
                {rep.status}
              </span>
            </div>

            <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#FFFFFF' }}>{rep.title}</div>
            <div style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: 1.5 }}>{rep.desc}</div>

            {/* Quality & Telemetry Badges */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '10px', borderRadius: '6px' }}>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>EVIDENCE COVERAGE</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>{rep.citationCoverage}%</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>COMPILATION</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>{rep.generationTime}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>PINNED SNAPSHOT</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#A855F7', marginTop: '2px' }}>{rep.snapshot}</div>
              </div>
            </div>

            {/* Quick Actions Row */}
            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', paddingTop: '4px' }}>
              <button
                onClick={() => {
                  setActiveReportTitle(rep.title);
                  setIsDeckOpen(true);
                }}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '5px 10px',
                  background: 'rgba(56, 189, 248, 0.12)',
                  border: '1px solid rgba(56, 189, 248, 0.3)',
                  borderRadius: '6px',
                  color: '#38BDF8',
                  fontSize: '0.74rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                <Presentation size={12} />
                <span>8-Slide Deck</span>
              </button>

              <button
                onClick={() => {
                  setActiveReportTitle(rep.title);
                  setIsLineageOpen(true);
                }}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '5px 10px',
                  background: 'rgba(16, 185, 129, 0.12)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  borderRadius: '6px',
                  color: '#10B981',
                  fontSize: '0.74rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                <Network size={12} />
                <span>Lineage DAG</span>
              </button>

              <button
                onClick={() => {
                  setActiveReportTitle(rep.title);
                  setIsDiffOpen(true);
                }}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '5px 10px',
                  background: 'rgba(245, 158, 11, 0.12)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  borderRadius: '6px',
                  color: '#F59E0B',
                  fontSize: '0.74rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                <GitCompare size={12} />
                <span>Version Diff</span>
              </button>

              <button
                onClick={() => {
                  setActiveReportTitle(rep.title);
                  setIsAuditOpen(true);
                }}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '5px 10px',
                  background: 'rgba(168, 85, 247, 0.12)',
                  border: '1px solid rgba(168, 85, 247, 0.3)',
                  borderRadius: '6px',
                  color: '#A855F7',
                  fontSize: '0.74rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                <History size={12} />
                <span>Audit Trail</span>
              </button>
            </div>

            {/* Export & Sign-Off Buttons */}
            <div style={{ marginTop: 'auto', borderTop: '1px solid #1E293B', paddingTop: '14px', display: 'flex', gap: '10px' }}>
              <button
                onClick={() => handleExport(rep.title)}
                disabled={isExporting}
                style={{
                  flex: 1,
                  padding: '9px 14px',
                  background: '#0284C7',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#FFFFFF',
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  cursor: isExporting ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                }}
              >
                <Download size={13} />
                <span>{isExporting ? 'Exporting...' : `Export ${selectedFormat}`}</span>
              </button>

              <button
                onClick={() => {
                  setActiveReportTitle(rep.title);
                  setIsSignOffOpen(true);
                }}
                style={{
                  padding: '9px 14px',
                  background: 'rgba(30, 41, 59, 0.8)',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: '#F1F5F9',
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <FileCheck size={13} />
                <span>Sign Off</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Board Action Tracker Component */}
      <BoardDirectivesPanel />

      {/* Presentation Deck Viewer Modal */}
      <PresentationDeckViewerModal
        isOpen={isDeckOpen}
        onClose={() => setIsDeckOpen(false)}
        reportTitle={activeReportTitle}
      />

      {/* Lineage Graph Modal */}
      <ReportLineageGraphModal
        isOpen={isLineageOpen}
        onClose={() => setIsLineageOpen(false)}
        reportTitle={activeReportTitle}
      />

      {/* Version Diff Modal */}
      <ReportVersionDiffModal
        isOpen={isDiffOpen}
        onClose={() => setIsDiffOpen(false)}
        reportTitle={activeReportTitle}
      />

      {/* Audit Trail Modal */}
      <ReportAuditTrailModal
        isOpen={isAuditOpen}
        onClose={() => setIsAuditOpen(false)}
        reportTitle={activeReportTitle}
      />

      {/* Sign-Off Modal */}
      <ReportSignOffModal
        isOpen={isSignOffOpen}
        onClose={() => setIsSignOffOpen(false)}
        onSignOffSuccess={() => setExportMessage('Executive sign-off recorded and cryptographically sealed with SHA-256.')}
        reportTitle={activeReportTitle}
      />
    </div>
  );
};
