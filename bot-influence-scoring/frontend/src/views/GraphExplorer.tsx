import { useState } from 'react';
import { GraphCanvas } from '../components/charts/GraphCanvas';
import type { GraphNode } from '../components/charts/GraphCanvas';
import { BotAuditPanel } from './BotAuditPanel';
import { useInfluenceScores } from '../hooks/useInfluenceScores';

export function GraphExplorer() {
  const [sanitized, setSanitized]       = useState(false);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [topK, setTopK]                 = useState(500);
  const { nodes, edges, isLoading }     = useInfluenceScores({ sanitized, topK });

  return (
    <div className="flex flex-col h-full gap-4 p-6">
      {/* Controls bar */}
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-semibold text-text-primary flex-1">Network Graph</h1>

        <select
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          className="
            bg-bg-elevated border border-border rounded-md
            text-sm text-text-primary px-3 py-2 outline-none
            focus:border-blue focus:shadow-[0_0_0_2px_var(--blue-glow)]
          "
        >
          {[100, 500, 1000].map((k) => (
            <option key={k} value={k}>Top {k.toLocaleString()} nodes</option>
          ))}
        </select>

        <div className="flex rounded-md border border-border overflow-hidden">
          {(['Raw', 'Sanitized'] as const).map((label) => (
            <button
              key={label}
              onClick={() => setSanitized(label === 'Sanitized')}
              className={`
                px-4 py-2 text-sm font-semibold transition-colors duration-fast
                ${(label === 'Sanitized') === sanitized
                  ? 'bg-blue text-white'
                  : 'bg-bg-surface text-text-secondary hover:bg-bg-elevated'}
              `}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Graph area */}
      <div className="flex-1 relative min-h-0">
        {isLoading ? (
          <div className="skeleton w-full h-full rounded-lg" />
        ) : nodes.length === 0 ? (
          <div className="w-full h-full flex items-center justify-center bg-bg-surface rounded-lg border border-border">
            <div className="text-center">
              <p className="text-text-secondary text-base">No graph data available.</p>
              <p className="text-text-disabled text-sm mt-1">Start the backend API to load data.</p>
            </div>
          </div>
        ) : (
          <GraphCanvas
            nodes={nodes}
            edges={edges}
            onNodeClick={(n: GraphNode) => setSelectedNode(n.id)}
          />
        )}
      </div>

      {/* Bot Audit slide-over */}
      {selectedNode && (
        <BotAuditPanel
          nodeId={selectedNode}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </div>
  );
}
