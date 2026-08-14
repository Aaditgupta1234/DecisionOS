import React from 'react';
import { GitMerge, ArrowRight, Check, X } from 'lucide-react';
import { CausalGraphNode, RootCauseSummaryGroup } from '../../types';

interface CausalChainExplorerProps {
  summaries: RootCauseSummaryGroup[];
  nodes: CausalGraphNode[];
  activeChainNodeIds: string[];
  onSelectChain: (nodeIds: string[]) => void;
  onClearChain: () => void;
}

export const CausalChainExplorer: React.FC<CausalChainExplorerProps> = ({
  summaries,
  nodes,
  activeChainNodeIds,
  onSelectChain,
  onClearChain,
}) => {
  // Extract all unique multi-hop paths from summaries
  const nodeTitleMap = React.useMemo(() => {
    const map = new Map<string, string>();
    nodes.forEach((n) => map.set(n.id, n.title));
    return map;
  }, [nodes]);

  const allChains = React.useMemo(() => {
    const chains: string[][] = [];
    summaries.forEach((s) => {
      if (s.causal_chains && s.causal_chains.length > 0) {
        s.causal_chains.forEach((chain) => {
          if (chain.length > 1) {
            chains.push(chain);
          }
        });
      }
    });
    return chains;
  }, [summaries]);

  if (allChains.length === 0) return null;

  return (
    <div
      className="card"
      style={{
        marginBottom: '20px',
        backgroundColor: 'var(--bg-surface-elevated)',
        border: '1px solid var(--border-subtle)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <GitMerge size={16} color="var(--color-primary-light)" />
          <h4 style={{ fontSize: '0.95rem', color: '#ffffff' }}>
            Multi-Hop Causal Chains ({allChains.length})
          </h4>
        </div>

        {activeChainNodeIds.length > 0 && (
          <button
            onClick={onClearChain}
            className="btn btn-ghost btn-sm"
            style={{ fontSize: '0.75rem', color: 'var(--text-muted)', gap: '4px' }}
          >
            <X size={12} />
            <span>Clear Highlight</span>
          </button>
        )}
      </div>

      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
        Select a causal path below to highlight the propagation trajectory across the DAG:
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {allChains.map((chain, cIdx) => {
          const isSelected =
            activeChainNodeIds.length === chain.length &&
            activeChainNodeIds.every((id, idx) => id === chain[idx]);

          return (
            <button
              key={cIdx}
              onClick={() => onSelectChain(isSelected ? [] : chain)}
              style={{
                display: 'flex',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '8px',
                padding: '8px 12px',
                backgroundColor: isSelected ? 'var(--color-primary-subtle)' : 'var(--bg-app)',
                border: `1px solid ${isSelected ? 'var(--color-primary-light)' : 'var(--border-subtle)'}`,
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                textAlign: 'left',
                width: '100%',
                transition: 'all var(--transition-fast)',
              }}
            >
              <span className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>
                Path #{cIdx + 1}
              </span>

              <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '6px', flex: 1 }}>
                {chain.map((nodeId, idx) => {
                  const title = nodeTitleMap.get(nodeId) || nodeId;
                  const isFirst = idx === 0;
                  const isLast = idx === chain.length - 1;

                  return (
                    <React.Fragment key={idx}>
                      <span
                        style={{
                          fontSize: '0.8rem',
                          fontWeight: isFirst || isLast ? 600 : 400,
                          color: isFirst
                            ? 'var(--color-warning)'
                            : isLast
                            ? 'var(--color-danger)'
                            : 'var(--text-main)',
                        }}
                      >
                        {title}
                      </span>
                      {idx < chain.length - 1 && (
                        <ArrowRight size={12} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                      )}
                    </React.Fragment>
                  );
                })}
              </div>

              {isSelected && <Check size={14} color="var(--color-primary-light)" />}
            </button>
          );
        })}
      </div>
    </div>
  );
};
