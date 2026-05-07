import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Label,
} from 'recharts';
import { Card } from '../ui/Card';

interface RankingBarChartProps {
  title: string;
  data: { nodeId: string; score: number }[];
  color: string;
}

const CustomTooltip = ({
  active, payload,
}: {
  active?: boolean;
  payload?: { payload: { nodeId: string; score: number } }[];
}) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-bg-elevated border border-border rounded-md p-3 text-sm shadow-[0_4px_16px_rgba(0,0,0,0.2)]">
      <p className="font-mono text-text-primary">{payload[0].payload.nodeId}</p>
      <p className="text-blue font-semibold">φᵥ = {payload[0].payload.score.toFixed(3)}</p>
    </div>
  );
};

export function RankingBarChart({ title, data, color }: RankingBarChartProps) {
  return (
    <Card>
      <p className="text-lg font-semibold text-text-primary mb-4">{title}</p>
      <ResponsiveContainer width="100%" height={420}>
        <BarChart layout="vertical" data={data} margin={{ left: 80, right: 16, bottom: 20 }}>
          <XAxis
            type="number"
            domain={[0, 1]}
            tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          >
            <Label value="Composite Influence Score (φᵥ)" position="insideBottom" offset={-4} style={{ fill: 'var(--text-secondary)', fontSize: 11 }} />
          </XAxis>
          <YAxis
            type="category"
            dataKey="nodeId"
            width={76}
            tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontFamily: 'JetBrains Mono' }}
            axisLine={false}
            tickLine={false}
          >
            <Label value="Node ID" angle={-90} position="insideLeft" offset={16} style={{ fill: 'var(--text-secondary)', fontSize: 11 }} />
          </YAxis>
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'var(--bg-elevated)' }} />
          <Bar dataKey="score" radius={[0, 4, 4, 0]} fill={color} barSize={12} animationDuration={600} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
