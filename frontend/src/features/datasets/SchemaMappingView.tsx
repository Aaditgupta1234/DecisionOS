import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import {
  Table,
  CheckCircle2,
  AlertCircle,
  ArrowLeft,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  RefreshCw,
} from 'lucide-react';

interface ColumnMapping {
  column_name: string;
  inferred_type: string;
  semantic_role: string;
  confidence: number;
  sample_values: string[];
}

export const SchemaMappingView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [mappings, setMappings] = useState<Record<string, string>>({
    order_id: 'order_id',
    customer_id: 'customer_id',
    order_purchase_timestamp: 'timestamp',
    payment_value: 'revenue',
    order_status: 'status',
    product_category_name: 'category',
    delivery_estimated_date: 'delivery_date',
  });

  const [approving, setApproving] = useState(false);
  const [success, setSuccess] = useState(false);

  // Fetch dataset info
  const { data: dataset, isLoading } = useQuery({
    queryKey: queryKeys.datasets.detail(id || ''),
    queryFn: () => DecisionApi.getDataset(id!),
    enabled: !!id,
  });

  const sampleColumns: ColumnMapping[] = [
    {
      column_name: 'order_id',
      inferred_type: 'string',
      semantic_role: 'order_id',
      confidence: 0.99,
      sample_values: ['e481f51cbdc54678b7cc', '53cdb2fc8bc7dce0b6a4'],
    },
    {
      column_name: 'customer_id',
      inferred_type: 'string',
      semantic_role: 'customer_id',
      confidence: 0.97,
      sample_values: ['9ef432eb6251297304e76', 'b0830fb4747a6c6d20eed'],
    },
    {
      column_name: 'order_purchase_timestamp',
      inferred_type: 'datetime',
      semantic_role: 'timestamp',
      confidence: 0.98,
      sample_values: ['2023-10-02 10:56:33', '2023-10-04 15:42:00'],
    },
    {
      column_name: 'payment_value',
      inferred_type: 'float',
      semantic_role: 'revenue',
      confidence: 0.95,
      sample_values: ['141.46', '271.79', '86.40'],
    },
    {
      column_name: 'order_status',
      inferred_type: 'string',
      semantic_role: 'status',
      confidence: 0.94,
      sample_values: ['delivered', 'shipped', 'canceled'],
    },
    {
      column_name: 'product_category_name',
      inferred_type: 'string',
      semantic_role: 'category',
      confidence: 0.92,
      sample_values: ['health_beauty', 'watches_gifts', 'telephony'],
    },
  ];

  const handleRoleChange = (colName: string, newRole: string) => {
    setMappings(prev => ({ ...prev, [colName]: newRole }));
  };

  const handleApprove = async () => {
    setApproving(true);
    try {
      // In a live backend environment, invoke mapping approval API
      if (id) {
        try {
          await DecisionApi.generateIntelligence(id);
        } catch {
          // Continue to dashboard
        }
      }
      setSuccess(true);
      setTimeout(() => {
        navigate('/dashboard');
      }, 800);
    } finally {
      setApproving(false);
    }
  };

  const semanticRoles = [
    { value: 'order_id', label: 'Order ID (Identifier)' },
    { value: 'customer_id', label: 'Customer ID (Identifier)' },
    { value: 'timestamp', label: 'Timestamp (Temporal Dimension)' },
    { value: 'revenue', label: 'Revenue / Monetary (Metric Target)' },
    { value: 'status', label: 'Order Status (Fulfillment Dimension)' },
    { value: 'category', label: 'Category (Segment Dimension)' },
    { value: 'delivery_date', label: 'Delivery Timestamp (Operational)' },
    { value: 'ignore', label: 'Ignore / Exclude from Analysis' },
  ];

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1200px', margin: '0 auto' }}>
      
      {/* Back Link & Header */}
      <div style={{ marginBottom: '24px' }}>
        <Link
          to="/datasets"
          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '12.5px', color: '#94A3B8', textDecoration: 'none', marginBottom: '12px' }}
        >
          <ArrowLeft size={14} />
          <span>Back to Datasets</span>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#10B981', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Schema Alignment Engine
              </span>
              <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
              <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{dataset?.name || 'Dataset Ingestion'}</span>
            </div>
            <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.02em' }}>
              Schema Mapping & Semantic Review
            </h1>
            <p style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
              DecisionOS AI has inferred canonical roles for your dataset columns. Review confidence scores and approve to trigger the intelligence pipeline.
            </p>
          </div>

          <button
            onClick={handleApprove}
            disabled={approving}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              background: '#1D4ED8',
              border: '1px solid #3B82F6',
              color: '#FFFFFF',
              padding: '10px 22px',
              borderRadius: '7px',
              fontSize: '13px',
              fontWeight: 700,
              cursor: approving ? 'not-allowed' : 'pointer',
              boxShadow: '0 0 16px rgba(59, 130, 246, 0.35)',
            }}
          >
            {success ? (
              <>
                <CheckCircle2 size={15} color="#10B981" />
                <span>Mapping Approved! Redirecting...</span>
              </>
            ) : approving ? (
              <>
                <RefreshCw size={14} className="animate-spin" />
                <span>Triggering Pipeline...</span>
              </>
            ) : (
              <>
                <span>Approve & Run Intelligence</span>
                <ArrowRight size={14} />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Column Schema Mapping Table */}
      <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '12px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #141A24', color: '#64748B', textAlign: 'left', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              <th style={{ padding: '14px 20px' }}>Source CSV Column</th>
              <th style={{ padding: '14px 16px' }}>Inferred Type</th>
              <th style={{ padding: '14px 16px' }}>AI Confidence</th>
              <th style={{ padding: '14px 16px' }}>Sample Data</th>
              <th style={{ padding: '14px 20px' }}>Semantic Mapping</th>
            </tr>
          </thead>
          <tbody>
            {sampleColumns.map((col) => {
              const currentRole = mappings[col.column_name] || col.semantic_role;
              const confidencePct = Math.round(col.confidence * 100);

              return (
                <tr key={col.column_name} style={{ borderBottom: '1px solid #111620' }}>
                  <td style={{ padding: '14px 20px', fontWeight: 700, color: '#FFFFFF', fontFamily: 'monospace' }}>
                    {col.column_name}
                  </td>

                  <td style={{ padding: '14px 16px', color: '#94A3B8' }}>
                    <span style={{ background: '#111622', border: '1px solid #1E2738', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontFamily: 'monospace' }}>
                      {col.inferred_type}
                    </span>
                  </td>

                  <td style={{ padding: '14px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ fontSize: '11.5px', fontWeight: 700, color: confidencePct >= 95 ? '#10B981' : '#38BDF8' }}>
                        {confidencePct}%
                      </span>
                      <ShieldCheck size={13} color={confidencePct >= 95 ? '#10B981' : '#38BDF8'} />
                    </div>
                  </td>

                  <td style={{ padding: '14px 16px', color: '#64748B', fontSize: '11.5px', fontFamily: 'monospace' }}>
                    {col.sample_values.slice(0, 2).join(', ')}
                  </td>

                  <td style={{ padding: '14px 20px' }}>
                    <select
                      value={currentRole}
                      onChange={(e) => handleRoleChange(col.column_name, e.target.value)}
                      style={{
                        background: '#04060A',
                        border: '1px solid #1E293B',
                        borderRadius: '6px',
                        padding: '6px 10px',
                        color: '#FFFFFF',
                        fontSize: '12px',
                        fontWeight: 600,
                        outline: 'none',
                        cursor: 'pointer',
                        width: '100%',
                        maxWidth: '240px',
                      }}
                    >
                      {semanticRoles.map((role) => (
                        <option key={role.value} value={role.value}>
                          {role.label}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

    </div>
  );
};

export default SchemaMappingView;
