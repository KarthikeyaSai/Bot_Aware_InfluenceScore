import { useState } from 'react';
import { Download, ArrowUp, ArrowDown, Minus } from 'lucide-react';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { useLeaderboard, type InfluencerRow } from '../hooks/useInfluenceScores';

function RankShiftCell({ delta }: { delta: number }) {
  if (Math.abs(delta) < 10) return <span className="text-text-disabled flex items-center gap-1"><Minus size={12} /> —</span>;
  if (delta > 0) return <span className="text-green flex items-center gap-1"><ArrowUp size={12} />+{delta}</span>;
  return <span className="text-red flex items-center gap-1"><ArrowDown size={12} />{delta}</span>;
}

const COLUMNS = [
  { key: 'rank',           header: 'Rank',      render: (r: InfluencerRow) => <span className="font-mono text-text-disabled">#{r.rank}</span> },
  { key: 'nodeId',         header: 'Account',   render: (r: InfluencerRow) => <span className="font-mono text-xs">{r.nodeId}</span> },
  { key: 'compositeScore', header: 'φᵥ Score',  render: (r: InfluencerRow) => <span className="text-blue font-semibold">{r.compositeScore.toFixed(3)}</span> },
  { key: 'pagerank',       header: 'PageRank',  render: (r: InfluencerRow) => r.pagerank.toFixed(4), align: 'right' as const },
  { key: 'authority',      header: 'Authority', render: (r: InfluencerRow) => r.authority.toFixed(3), align: 'right' as const },
  { key: 'icReach',        header: 'IC Reach',  render: (r: InfluencerRow) => r.icReach.toLocaleString(), align: 'right' as const },
  { key: 'botProb',        header: 'Bot Prob',  render: (r: InfluencerRow) => {
    const v = r.botProb;
    const variant = v >= 0.7 ? 'bot' : v <= 0.3 ? 'genuine' : 'uncertain';
    return <Badge variant={variant} label={`${(v * 100).toFixed(0)}%`} />;
  }},
  { key: 'rankShift',      header: 'Rank Shift', render: (r: InfluencerRow) => <RankShiftCell delta={r.rankShift} /> },
];

export function Leaderboard() {
  const [sanitized, setSanitized] = useState(false);
  const [page, setPage]           = useState(0);
  const PAGE_SIZE = 50;

  const { data = [], isLoading } = useLeaderboard({ sanitized });
  const pageData = data.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const exportCSV = () => {
    const header = 'Rank,Node ID,Score,PageRank,Authority,IC Reach,Bot Prob,Rank Shift\n';
    const rows = data.map((r) =>
      `${r.rank},${r.nodeId},${r.compositeScore},${r.pagerank},${r.authority},${r.icReach},${r.botProb},${r.rankShift}`
    ).join('\n');
    const blob = new Blob([header + rows], { type: 'text/csv' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = 'influence_scores.csv'; a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6 flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-text-primary">Influence Leaderboard</h1>
        <div className="flex items-center gap-3">
          {/* Raw / Sanitized toggle */}
          <div className="flex rounded-md border border-border overflow-hidden">
            {(['Raw', 'Sanitized'] as const).map((label) => (
              <button
                key={label}
                onClick={() => { setSanitized(label === 'Sanitized'); setPage(0); }}
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
          <Button variant="secondary" onClick={exportCSV}>
            <Download size={14} className="mr-2 inline" /> Export CSV
          </Button>
        </div>
      </div>

      <div className="bg-bg-surface border border-border rounded-lg p-5">
        {isLoading ? (
          <div className="skeleton h-64 rounded-lg" />
        ) : data.length === 0 ? (
          <p className="text-text-secondary text-center py-12">No data. Start the backend API.</p>
        ) : (
          <>
            <DataTable columns={COLUMNS} data={pageData} rowKey={(r) => r.nodeId} />
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-border-subtle">
              <span className="text-sm text-text-secondary">
                Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, data.length)} of {data.length.toLocaleString()}
              </span>
              <div className="flex gap-2">
                <Button variant="secondary" onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0}>
                  Previous
                </Button>
                <Button variant="secondary" onClick={() => setPage((p) => p + 1)} disabled={(page + 1) * PAGE_SIZE >= data.length}>
                  Next
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
