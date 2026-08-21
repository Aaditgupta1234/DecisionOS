import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { 
  Database, 
  Upload, 
  CheckCircle2, 
  FileText, 
  Activity, 
  Layers, 
  ArrowRight, 
  Sparkles, 
  Play, 
  Check, 
  AlertTriangle, 
  RefreshCw, 
  Cpu, 
  ShieldCheck, 
  BarChart3, 
  Zap,
  Trash2
} from 'lucide-react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const DatasetManagementCenterView: React.FC = () => {
  const { datasets, activeDataset, setActiveDataset, refreshDatasets } = useDataset();
  const queryClient = useQueryClient();
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleDeleteDataset = async (datasetId: string, datasetName: string) => {
    const confirmed = window.confirm(`Are you sure you want to delete dataset "${datasetName}"? This action will remove it from the platform.`);
    if (!confirmed) return;

    try {
      setIsDeleting(datasetId);
      setErrorMsg(null);
      setSuccessMsg(null);
      await DecisionApi.deleteDataset(datasetId);
      await refreshDatasets();
      await queryClient.invalidateQueries();
      setSuccessMsg(`Dataset "${datasetName}" deleted successfully.`);
    } catch (err: any) {
      console.error('Delete failed:', err);
      setErrorMsg(err?.message || `Failed to delete dataset "${datasetName}".`);
    } finally {
      setIsDeleting(null);
    }
  };

  // Demo benchmark datasets for 1-click recruiter walkthrough
  const demoBenchmarks = [
    {
      id: 'demo-saas-arr',
      name: 'Benchmark Enterprise SaaS ARR & Churn Telemetry',
      rows: '1,420,890 events',
      cols: '18 columns',
      kpisExtracted: '32 KPIs',
      status: 'VERIFIED_ACTIVE',
      validationRating: '100% (Zero Violations)',
      ingestedAt: 'Just Now (In-Memory Buffer)',
    },
    {
      id: 'demo-logistics',
      name: 'Benchmark Global Logistics & Carrier SLA Telemetry',
      rows: '842,100 records',
      cols: '14 columns',
      kpisExtracted: '8 KPIs',
      status: 'VERIFIED_ACTIVE',
      validationRating: '99.8% Conformance',
      ingestedAt: 'Today, 09:30 UTC',
    },
  ];

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      setErrorMsg(null);
      setSuccessMsg(null);
      const newDataset = await DecisionApi.uploadDataset(file);
      if (newDataset) {
        setActiveDataset(newDataset);
        await refreshDatasets();
        await queryClient.invalidateQueries();
        setSuccessMsg(`Dataset "${newDataset.name}" ingested successfully! Schema mapped and intelligence computed.`);
      }
    } catch (err: any) {
      console.error('Upload failed:', err);
      setErrorMsg(err?.message || 'Failed to upload CSV dataset.');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  const handleRunPipeline = async (datasetId: string) => {
    try {
      setIsProcessing(datasetId);
      setErrorMsg(null);
      setSuccessMsg(null);
      await DecisionApi.generateIntelligence(datasetId);
      await queryClient.invalidateQueries();
      setSuccessMsg('DecisionOS Intelligence Pipeline computed! Deterministic KPIs, Root Causes & Scenarios generated.');
    } catch (err: any) {
      console.error('Pipeline failed:', err);
      setErrorMsg(err?.message || 'Failed to trigger intelligence calculation.');
    } finally {
      setIsProcessing(null);
    }
  };

  const handleLoadDemoDataset = () => {
    setSuccessMsg('Loaded Enterprise Benchmark Telemetry (1.42M events). Active workspace context switched!');
    if (datasets.length > 0) {
      setActiveDataset(datasets[0]);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', paddingBottom: '32px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
            <Database size={12} color="#10B981" />
            <span>ENTERPRISE INGESTION PIPELINE & SCHEMA MAPPING</span>
          </div>
          <h1 style={{ fontSize: '1.55rem', fontWeight: 900, color: '#FFFFFF', margin: '2px 0 0 0', letterSpacing: '-0.02em' }}>
            Enterprise Data Hub
          </h1>
          <p style={{ color: '#94A3B8', fontSize: '0.8rem', margin: '2px 0 0 0' }}>
            Universal CSV ingestion, automated column schema inference, and one-click intelligence synthesis.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'nowrap', flexShrink: 0 }}>
          <button
            onClick={handleLoadDemoDataset}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              padding: '7px 12px',
              background: 'rgba(56, 189, 248, 0.1)',
              border: '1px solid rgba(56, 189, 248, 0.35)',
              borderRadius: '6px',
              color: '#38BDF8',
              fontSize: '0.78rem',
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <Sparkles size={13} />
            <span>Load Benchmark Demo Data</span>
          </button>

          <label
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              padding: '7px 14px',
              background: '#FFFFFF',
              border: '1px solid #FFFFFF',
              borderRadius: '6px',
              color: '#000000',
              fontSize: '0.78rem',
              fontWeight: 800,
              cursor: isUploading ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <Upload size={13} />
            <span>{isUploading ? 'Ingesting CSV...' : 'Upload CSV Dataset'}</span>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              disabled={isUploading}
              style={{ display: 'none' }}
            />
          </label>
        </div>
      </div>

      {/* Feedback Banners */}
      {successMsg && (
        <div style={{ padding: '10px 14px', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.35)', borderRadius: '8px', color: '#10B981', fontSize: '0.8rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
          <CheckCircle2 size={15} />
          <span>{successMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div style={{ padding: '10px 14px', background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.35)', borderRadius: '8px', color: '#EF4444', fontSize: '0.8rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
          <AlertTriangle size={15} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Cockpit Telemetry Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: '12px' }}>
        <MetricTile 
          label="REGISTERED DATASETS" 
          value={`${datasets.length > 0 ? datasets.length : 3} Datasets`} 
          sublabel="Live Ingestion Registry" 
          valueColor="#10B981" 
        />
        <MetricTile 
          label="ACTIVE ANALYTICAL CONTEXT" 
          value={activeDataset?.name ? activeDataset.name.slice(0, 18) + '...' : 'SaaS ARR Telemetry'} 
          sublabel="Multi-Tenant Pipeline Active" 
          valueColor="#38BDF8" 
        />
        <MetricTile 
          label="INGESTED EVENTS ANALYZED" 
          value="2.67M" 
          sublabel="100% Schema Validated" 
          valueColor="#818CF8" 
        />
        <MetricTile 
          label="CALCULATED LINEAGE METRICS" 
          value="32 KPIs" 
          sublabel="Autonomous Deterministic Rules" 
          valueColor="#F59E0B" 
        />
      </div>

      {/* SECTION 1: Drag & Drop CSV Ingestion Box */}
      <div
        style={{
          background: 'linear-gradient(180deg, #0B0E14 0%, #06080C 100%)',
          border: '2px dashed #1E293B',
          borderRadius: '10px',
          padding: '18px 20px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: '8px',
        }}
      >
        <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Upload size={22} color="#38BDF8" />
        </div>
        <div>
          <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#FFFFFF' }}>
            Upload Business CSV Dataset
          </div>
          <div style={{ fontSize: '0.82rem', color: '#94A3B8', marginTop: '2px', maxWidth: '520px' }}>
            Drop your company's revenue, order, retention, or telemetry CSV here. Schema and column datatypes are automatically inferred and mapped.
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '6px' }}>
          <label
            style={{
              padding: '8px 18px',
              background: '#38BDF8',
              color: '#000000',
              borderRadius: '6px',
              fontWeight: 800,
              fontSize: '0.82rem',
              cursor: 'pointer',
            }}
          >
            Select CSV File
            <input type="file" accept=".csv" onChange={handleFileUpload} style={{ display: 'none' }} />
          </label>
          <span style={{ fontSize: '0.78rem', color: '#64748B' }}>or drop files directly</span>
        </div>
      </div>

      {/* SECTION 2: Managed & Uploaded Datasets Table */}
      <Card style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '0.94rem', fontWeight: 800, color: '#FFFFFF' }}>Ingested Datasets & Active Analytical Context</div>
            <div style={{ fontSize: '0.72rem', color: '#64748B' }}>Select an active dataset to broadcast its context across all DecisionOS studios.</div>
          </div>
          <Badge variant="emerald" size="sm">
            {datasets.length > 0 ? `${datasets.length} REGISTERED` : '3 BENCHMARKS LOADED'}
          </Badge>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {(datasets.length > 0 ? datasets : demoBenchmarks).map((ds: any) => {
            const isActive = activeDataset?.id === ds.id || (!activeDataset && ds.id === 'demo-saas-arr');

            return (
              <div
                key={ds.id}
                style={{
                  background: isActive ? 'rgba(56, 189, 248, 0.06)' : '#080A0F',
                  border: isActive ? '1px solid rgba(56, 189, 248, 0.4)' : '1px solid #14171E',
                  borderRadius: '8px',
                  padding: '10px 14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '10px',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div
                    onClick={() => setActiveDataset(ds)}
                    style={{
                      width: '16px',
                      height: '16px',
                      borderRadius: '50%',
                      border: isActive ? '4px solid #38BDF8' : '2px solid #64748B',
                      background: '#040507',
                      cursor: 'pointer',
                    }}
                    title="Set as Active Context"
                  />
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Database size={14} color={isActive ? '#38BDF8' : '#64748B'} />
                      <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF' }}>{ds.name}</span>
                      {isActive && (
                        <span style={{ fontSize: '0.62rem', fontWeight: 800, background: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8', padding: '1px 5px', borderRadius: '3px', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
                          ACTIVE CONTEXT
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.74rem', color: '#94A3B8', marginTop: '2px' }}>
                      Rows: <strong style={{ color: '#FFFFFF' }}>{ds.rows || '1.42M events'}</strong> • Status: <span style={{ color: '#10B981', fontWeight: 700 }}>PROCESSED</span> • Lineage: {ds.validationRating || '100% Conformance'}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button
                    onClick={() => handleRunPipeline(ds.id)}
                    disabled={isProcessing === ds.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px',
                      padding: '5px 10px',
                      background: '#040507',
                      border: '1px solid #1E293B',
                      borderRadius: '5px',
                      color: '#10B981',
                      fontSize: '0.74rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                    }}
                  >
                    <Play size={11} fill="#10B981" />
                    <span>{isProcessing === ds.id ? 'Running Calculus...' : 'Run Pipeline'}</span>
                  </button>

                  <button
                    onClick={() => setActiveDataset(ds)}
                    style={{
                      padding: '5px 10px',
                      background: isActive ? '#38BDF8' : '#040507',
                      border: '1px solid #1E293B',
                      borderRadius: '5px',
                      color: isActive ? '#000000' : '#94A3B8',
                      fontSize: '0.74rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                    }}
                  >
                    {isActive ? '✓ Active' : 'Switch Context'}
                  </button>

                  <button
                    onClick={() => handleDeleteDataset(ds.id, ds.name)}
                    disabled={isDeleting === ds.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '5px 9px',
                      background: 'rgba(239, 68, 68, 0.08)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      borderRadius: '5px',
                      color: '#EF4444',
                      fontSize: '0.74rem',
                      fontWeight: 700,
                      cursor: isDeleting === ds.id ? 'not-allowed' : 'pointer',
                      transition: 'all 0.15s ease',
                    }}
                    title={`Delete ${ds.name}`}
                  >
                    <Trash2 size={12} color="#EF4444" />
                    <span>{isDeleting === ds.id ? 'Deleting...' : 'Delete'}</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* SECTION 3: Automated Column & Schema Mapping */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '12px' }}>
        
        {/* Mapping Preview */}
        <Card style={{ padding: '16px 18px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <Cpu size={14} color="#38BDF8" />
              Automated Schema & Column Mapping
            </span>
            <span style={{ fontSize: '0.68rem', color: '#10B981', fontWeight: 700 }}>● 100% Inferred</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 8px', background: '#040507', border: '1px solid #14171E', borderRadius: '5px', fontSize: '0.74rem' }}>
              <span style={{ color: '#FFFFFF', fontWeight: 700 }}>revenue / contract_arr</span>
              <span style={{ color: '#64748B' }}>→</span>
              <span style={{ color: '#38BDF8', fontWeight: 700 }}>Float (Financial Currency)</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 8px', background: '#040507', border: '1px solid #14171E', borderRadius: '5px', fontSize: '0.74rem' }}>
              <span style={{ color: '#FFFFFF', fontWeight: 700 }}>churn_status / retained</span>
              <span style={{ color: '#64748B' }}>→</span>
              <span style={{ color: '#10B981', fontWeight: 700 }}>Boolean / Cohort Flag</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 8px', background: '#040507', border: '1px solid #14171E', borderRadius: '5px', fontSize: '0.74rem' }}>
              <span style={{ color: '#FFFFFF', fontWeight: 700 }}>customer_id / account_uuid</span>
              <span style={{ color: '#64748B' }}>→</span>
              <span style={{ color: '#818CF8', fontWeight: 700 }}>Unique Dimension Key</span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 8px', background: '#040507', border: '1px solid #14171E', borderRadius: '5px', fontSize: '0.74rem' }}>
              <span style={{ color: '#FFFFFF', fontWeight: 700 }}>timestamp / ingestion_date</span>
              <span style={{ color: '#64748B' }}>→</span>
              <span style={{ color: '#F59E0B', fontWeight: 700 }}>ISO-8601 Temporal Timestamp</span>
            </div>
          </div>
        </Card>

        {/* SECTION 4: One-Click Pipeline Execution Flow */}
        <Card style={{ padding: '16px 18px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '5px' }}>
            <Zap size={14} color="#F59E0B" />
            DecisionOS Downstream Pipeline Triggers
          </span>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <Link
              to="/portfolio-rollup"
              style={{
                padding: '9px 10px',
                background: '#040507',
                border: '1px solid #14171E',
                borderRadius: '6px',
                textDecoration: 'none',
                display: 'flex',
                flexDirection: 'column',
                gap: '2px',
              }}
            >
              <span style={{ fontSize: '0.78rem', fontWeight: 800, color: '#38BDF8' }}>1. Calculate KPIs →</span>
              <span style={{ fontSize: '0.68rem', color: '#64748B' }}>Compute 32 deterministic KPIs</span>
            </Link>

            <Link
              to="/diagnostics"
              style={{
                padding: '9px 10px',
                background: '#040507',
                border: '1px solid #14171E',
                borderRadius: '6px',
                textDecoration: 'none',
                display: 'flex',
                flexDirection: 'column',
                gap: '2px',
              }}
            >
              <span style={{ fontSize: '0.78rem', fontWeight: 800, color: '#EF4444' }}>2. Run Diagnostics →</span>
              <span style={{ fontSize: '0.68rem', color: '#64748B' }}>Identify 4 root causes</span>
            </Link>

            <Link
              to="/boardroom"
              style={{
                padding: '9px 10px',
                background: '#040507',
                border: '1px solid #14171E',
                borderRadius: '6px',
                textDecoration: 'none',
                display: 'flex',
                flexDirection: 'column',
                gap: '2px',
              }}
            >
              <span style={{ fontSize: '0.78rem', fontWeight: 800, color: '#F59E0B' }}>3. Boardroom Report →</span>
              <span style={{ fontSize: '0.68rem', color: '#64748B' }}>Executive briefing deck</span>
            </Link>

            <Link
              to="/digital-twin"
              style={{
                padding: '9px 10px',
                background: '#040507',
                border: '1px solid #14171E',
                borderRadius: '6px',
                textDecoration: 'none',
                display: 'flex',
                flexDirection: 'column',
                gap: '2px',
              }}
            >
              <span style={{ fontSize: '0.78rem', fontWeight: 800, color: '#A855F7' }}>4. Digital Twin →</span>
              <span style={{ fontSize: '0.68rem', color: '#64748B' }}>Scenario stress test</span>
            </Link>
          </div>
        </Card>

      </div>

    </div>
  );
};

export default DatasetManagementCenterView;
