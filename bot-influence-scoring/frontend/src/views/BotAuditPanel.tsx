import { X } from 'lucide-react';
import { BotProbGauge } from '../components/charts/BotProbGauge';
import { Badge } from '../components/ui/Badge';
import { DataTable } from '../components/ui/DataTable';
import { useNodeDetail } from '../hooks/useInfluenceScores';
import type { BadgeVariant } from '../components/ui/Badge';

export function BotAuditPanel({ nodeId, onClose }: { nodeId: string; onClose: () => void }) {
  const { node, isLoading } = useNodeDetail(nodeId);

  const variant: BadgeVariant = !node
    ? 'neutral'
    : node.botProb >= 0.7 ? 'bot'
    : node.botProb <= 0.3 ? 'genuine'
    : 'uncertain';

  return (
    <div className="
      fixed right-0 top-0 h-full w-[400px] z-50
      bg-bg-surface border-l border-border
      flex flex-col
      animate-fade-up
      shadow-[-8px_0_32px_rgba(0,0,0,0.3)]
    ">
      {/* Header */}
      <div className="flex items-center justify-between p-5 border-b border-border">
        <div>
          <p className="text-xs text-text-secondary font-mono">{nodeId}</p>
          <p className="text-lg font-semibold text-text-primary">Account Audit</p>
        </div>
        <button onClick={onClose} className="text-text-secondary hover:text-text-primary transition-colors">
          <X size={20} />
        </button>
      </div>

      {isLoading || !node ? (
        <div className="p-5 flex flex-col gap-4">
          <div className="skeleton h-[140px] rounded-lg" />
          <div className="skeleton h-[200px] rounded-lg" />
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-5">
          {/* Gauge + badge */}
          <div className="bg-bg-elevated rounded-lg p-4 flex flex-col items-center gap-3">
            <BotProbGauge prob={node.botProb} />
            <Badge
              variant={variant}
              label={
                variant === 'bot'     ? 'Bot Detected'  :
                variant === 'genuine' ? 'Verified Human' :
                'Uncertain'
              }
            />
            <p className="text-sm text-text-secondary text-center">
              Confidence: {variant !== 'uncertain' ? 'High' : 'Low'}{' '}
              ({(Math.abs(node.botProb - 0.5) * 200).toFixed(0)}%)
            </p>
          </div>

          {/* Feature breakdown */}
          <div>
            <p className="text-sm font-semibold text-text-primary mb-3">Feature Breakdown</p>
            <DataTable
              columns={[
                { key: 'feature', header: 'Feature' },
                { key: 'value',   header: 'Value', align: 'right' },
              ]}
              data={node.featureBreakdown}
              rowKey={(r) => r.feature}
            />
          </div>

          {/* Top suspicious neighbors */}
          {node.suspiciousNeighbors.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-text-primary mb-3">Top Suspicious Neighbors</p>
              <div className="flex flex-col gap-2">
                {node.suspiciousNeighbors.map((n) => (
                  <div key={n.id} className="flex items-center justify-between py-2 border-b border-border-subtle">
                    <span className="font-mono text-xs text-text-primary">{n.id}</span>
                    <Badge
                      variant={n.botProb >= 0.7 ? 'bot' : 'uncertain'}
                      label={`${(n.botProb * 100).toFixed(0)}%`}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
