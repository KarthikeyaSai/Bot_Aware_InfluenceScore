import { MetricCard } from '../components/ui/MetricCard';
import { RankingBarChart } from '../components/charts/RankingBarChart';
import { useRankingComparison } from '../hooks/useInfluenceScores';

export function RankingComparison() {
  const { data, isLoading } = useRankingComparison();

  if (isLoading) {
    return (
      <div className="p-6 flex flex-col gap-6">
        <h1 className="text-xl font-semibold text-text-primary">Before / After Sanitization</h1>
        <div className="grid grid-cols-4 gap-4">
          {[0, 1, 2, 3].map((i) => <div key={i} className="skeleton h-24 rounded-lg" />)}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="skeleton h-[480px] rounded-lg" />
          <div className="skeleton h-[480px] rounded-lg" />
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-6 flex items-center justify-center h-full">
        <p className="text-text-secondary">No comparison data. Start the backend API.</p>
      </div>
    );
  }

  const { rankDisplacement, rawTop20, cleanTop20 } = data;

  return (
    <div className="p-6 flex flex-col gap-6">
      <h1 className="text-xl font-semibold text-text-primary">Before / After Sanitization</h1>

      {/* Summary stats */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard label="Top-100 Displaced"  value={rankDisplacement.pctTopKDisplaced}  unit="%" color="orange" index={0} />
        <MetricCard label="Mean Displacement"  value={rankDisplacement.meanDisplacement}   unit="pos" color="blue" index={1} />
        <MetricCard label="Kendall's τ"        value={rankDisplacement.kendallsTau}         color="purple" index={2} />
        <MetricCard label="Spearman ρ"         value={rankDisplacement.spearmanR}           color="green"  index={3} />
      </div>

      {/* Side-by-side charts */}
      <div className="grid grid-cols-2 gap-4">
        <RankingBarChart
          title="Raw Graph (with bots)"
          data={rawTop20}
          color="#ff7043"
        />
        <RankingBarChart
          title="Sanitized Graph (bots removed)"
          data={cleanTop20}
          color="#1d9bf0"
        />
      </div>
    </div>
  );
}
