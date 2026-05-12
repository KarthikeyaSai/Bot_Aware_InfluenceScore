import { useQuery } from '@tanstack/react-query';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend, Label, ReferenceLine, CartesianGrid,
  AreaChart, Area,
} from 'recharts';
import { Card } from '../components/ui/Card';

const BASE = 'http://localhost:8000/api/v1';

function useMetrics() {
  return useQuery({
    queryKey: ['metrics'],
    queryFn: async () => {
      const res = await fetch(`${BASE}/metrics/?dataset=cresci-2017`);
      if (!res.ok) throw new Error('Failed to fetch metrics');
      return res.json();
    },
  });
}

function useTimeline() {
  return useQuery({
    queryKey: ['metrics-timeline'],
    queryFn: async () => {
      const res = await fetch(`${BASE}/metrics/timeline`);
      if (!res.ok) throw new Error('Failed to fetch timeline');
      return res.json() as Promise<{ month: string; genuine: number; bots: number }[]>;
    },
  });
}

function SummaryCard({ label, value, unit = '', color = 'text-blue' }: { label: string; value: number; unit?: string; color?: string }) {
  return (
    <Card>
      <p className="text-xs font-medium text-text-secondary uppercase tracking-[0.06em] mb-2">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}{unit}</p>
    </Card>
  );
}

function ConfusionMatrix({ tn, fp, fn, tp }: { tn: number; fp: number; fn: number; tp: number }) {
  const total = tn + fp + fn + tp;
  const cells = [
    { label: 'True Negative', sublabel: 'Genuine → Genuine', value: tn, pct: (tn / total * 100).toFixed(1), color: 'bg-green/20 text-green border-green/30' },
    { label: 'False Positive', sublabel: 'Genuine → Bot', value: fp, pct: (fp / total * 100).toFixed(1), color: 'bg-red/10 text-red border-red/30' },
    { label: 'False Negative', sublabel: 'Bot → Genuine', value: fn, pct: (fn / total * 100).toFixed(1), color: 'bg-orange/10 text-orange border-orange/30' },
    { label: 'True Positive', sublabel: 'Bot → Bot', value: tp, pct: (tp / total * 100).toFixed(1), color: 'bg-blue/10 text-blue border-blue/30' },
  ];

  return (
    <Card>
      <p className="text-base font-semibold text-text-primary mb-1">Confusion Matrix</p>
      <p className="text-xs text-text-secondary mb-4">Predicted →  |  Actual ↓</p>
      <div className="grid grid-cols-2 gap-3">
        {cells.map((c) => (
          <div key={c.label} className={`rounded-lg border p-4 ${c.color}`}>
            <p className="text-xs font-medium uppercase tracking-wide opacity-70">{c.label}</p>
            <p className="text-xs opacity-60 mb-2">{c.sublabel}</p>
            <p className="text-3xl font-bold font-mono">{c.value.toLocaleString()}</p>
            <p className="text-xs opacity-60 mt-1">{c.pct}% of total</p>
          </div>
        ))}
      </div>
    </Card>
  );
}

const chartTextStyle = { fill: 'var(--text-secondary)', fontSize: 11 };

function AccountTimeline() {
  const { data, isLoading } = useTimeline();

  if (isLoading || !data) return (
    <Card><p className="text-sm text-text-secondary">Loading timeline…</p></Card>
  );

  // Show one tick label every 12 months to avoid crowding
  const tickFormatter = (month: string, idx: number) =>
    idx % 12 === 0 ? month.slice(0, 7) : '';

  return (
    <Card>
      <p className="text-base font-semibold text-text-primary mb-1">
        Account Creation Timeline
      </p>
      <p className="text-xs text-text-secondary mb-4">
        Monthly new account registrations — genuine vs. bot (Cresci-2017, 2007–2015).
        Bot campaigns appear as sudden spikes; genuine users grow organically.
      </p>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ left: 8, right: 16, bottom: 28, top: 8 }}>
          <defs>
            <linearGradient id="colGenuine" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#00ba7c" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#00ba7c" stopOpacity={0.05} />
            </linearGradient>
            <linearGradient id="colBot" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#f4212e" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#f4212e" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis
            dataKey="month"
            tick={chartTextStyle}
            axisLine={false}
            tickLine={false}
            tickFormatter={tickFormatter}
            interval={0}
          >
            <Label value="Month" position="insideBottom" offset={-16} style={chartTextStyle} />
          </XAxis>
          <YAxis tick={chartTextStyle} axisLine={false} tickLine={false}>
            <Label value="New Accounts" angle={-90} position="insideLeft" offset={16} style={chartTextStyle} />
          </YAxis>
          <Tooltip
            contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
            labelFormatter={(l) => `Month: ${l}`}
          />
          <Legend verticalAlign="top" height={28} wrapperStyle={{ fontSize: 12 }} />
          <Area type="monotone" dataKey="genuine" name="Genuine" stroke="#00ba7c" fill="url(#colGenuine)" strokeWidth={2} dot={false} />
          <Area type="monotone" dataKey="bots"    name="Bots"    stroke="#f4212e" fill="url(#colBot)"     strokeWidth={2} dot={false} />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
}

export function ModelMetrics() {
  const { data, isLoading } = useMetrics();

  if (isLoading) {
    return (
      <div className="p-6 flex flex-col gap-6">
        <h1 className="text-xl font-semibold text-text-primary">Model Metrics</h1>
        <div className="grid grid-cols-3 gap-4">{[0,1,2,3,4,5].map(i => <div key={i} className="skeleton h-24 rounded-lg" />)}</div>
        <div className="grid grid-cols-2 gap-4">{[0,1,2,3].map(i => <div key={i} className="skeleton h-72 rounded-lg" />)}</div>
      </div>
    );
  }

  if (!data) return (
    <div className="p-6 flex items-center justify-center h-full">
      <p className="text-text-secondary">No metrics data. Start the backend API.</p>
    </div>
  );

  const { summary, confusionMatrix, rocCurve, prCurve, scoreDist, featureImportance } = data;

  return (
    <div className="p-6 flex flex-col gap-6 overflow-y-auto">
      <div className="flex items-baseline gap-3">
        <h1 className="text-xl font-semibold text-text-primary">Model Metrics</h1>
        <span className="text-sm text-text-secondary font-mono">cresci-2017</span>
      </div>

      {/* Summary row */}
      <div className="grid grid-cols-3 gap-4 lg:grid-cols-6">
        <SummaryCard label="Accuracy"  value={summary.accuracy}  unit="%" color="text-green" />
        <SummaryCard label="Precision" value={summary.precision} unit="%" color="text-blue" />
        <SummaryCard label="Recall"    value={summary.recall}    unit="%" color="text-blue" />
        <SummaryCard label="F1 Score"  value={summary.f1}        unit="%" color="text-purple" />
        <SummaryCard label="ROC-AUC"   value={summary.rocAuc}    color="text-orange" />
        <SummaryCard label="PR-AUC"    value={summary.prAuc}     color="text-orange" />
      </div>

      {/* Confusion matrix + Score distribution */}
      <div className="grid grid-cols-2 gap-4">
        <ConfusionMatrix {...confusionMatrix} />

        <Card>
          <p className="text-base font-semibold text-text-primary mb-4">Score Distribution</p>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={scoreDist} margin={{ left: 8, right: 8, bottom: 24 }} barCategoryGap="10%">
              <XAxis dataKey="bin" tick={chartTextStyle} axisLine={false} tickLine={false} tickFormatter={(v) => v.toFixed(1)}>
                <Label value="Bot Probability Score" position="insideBottom" offset={-12} style={chartTextStyle} />
              </XAxis>
              <YAxis tick={chartTextStyle} axisLine={false} tickLine={false}>
                <Label value="Node Count" angle={-90} position="insideLeft" offset={16} style={chartTextStyle} />
              </YAxis>
              <Tooltip
                contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
                labelFormatter={(v) => `Score ≈ ${Number(v).toFixed(2)}`}
              />
              <Legend wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
              <Bar dataKey="genuine" fill="#00ba7c" name="Genuine" stackId="a" />
              <Bar dataKey="bot"     fill="#f4212e" name="Bot"     stackId="a" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* ROC + PR curves */}
      <div className="grid grid-cols-2 gap-4">
        <Card>
          <p className="text-base font-semibold text-text-primary mb-1">ROC Curve</p>
          <p className="text-xs text-text-secondary mb-4">AUC = {summary.rocAuc}</p>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={rocCurve} margin={{ left: 8, right: 8, bottom: 24 }}>
              <XAxis dataKey="fpr" type="number" domain={[0,1]} tick={chartTextStyle} axisLine={false} tickLine={false}>
                <Label value="False Positive Rate" position="insideBottom" offset={-12} style={chartTextStyle} />
              </XAxis>
              <YAxis domain={[0,1]} tick={chartTextStyle} axisLine={false} tickLine={false}>
                <Label value="True Positive Rate" angle={-90} position="insideLeft" offset={16} style={chartTextStyle} />
              </YAxis>
              <Tooltip
                contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
                formatter={(v: unknown) => (v as number).toFixed(3)}
              />
              <ReferenceLine stroke="var(--border)" segment={[{ x: 0, y: 0 }, { x: 1, y: 1 }]} strokeDasharray="4 4" />
              <Line dataKey="tpr" stroke="#1d9bf0" dot={false} strokeWidth={2} name="TPR" />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <p className="text-base font-semibold text-text-primary mb-1">Precision-Recall Curve</p>
          <p className="text-xs text-text-secondary mb-4">AUC = {summary.prAuc}</p>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={prCurve} margin={{ left: 8, right: 8, bottom: 24 }}>
              <XAxis dataKey="recall" type="number" domain={[0,1]} tick={chartTextStyle} axisLine={false} tickLine={false}>
                <Label value="Recall" position="insideBottom" offset={-12} style={chartTextStyle} />
              </XAxis>
              <YAxis domain={[0,1]} tick={chartTextStyle} axisLine={false} tickLine={false}>
                <Label value="Precision" angle={-90} position="insideLeft" offset={16} style={chartTextStyle} />
              </YAxis>
              <Tooltip
                contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
                formatter={(v: unknown) => (v as number).toFixed(3)}
              />
              <Line dataKey="precision" stroke="#7856ff" dot={false} strokeWidth={2} name="Precision" />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Account creation timeline */}
      <AccountTimeline />

      {/* Feature importance */}
      <Card>
        <p className="text-base font-semibold text-text-primary mb-1">Feature Importance</p>
        <p className="text-xs text-text-secondary mb-4">Point-biserial correlation with bot label — higher = more predictive</p>
        <ResponsiveContainer width="100%" height={340}>
          <BarChart
            layout="vertical"
            data={featureImportance}
            margin={{ left: 160, right: 48, bottom: 20 }}
          >
            <XAxis type="number" domain={[0, 1]} tick={chartTextStyle} axisLine={false} tickLine={false}>
              <Label value="Absolute Correlation with Bot Label" position="insideBottom" offset={-12} style={chartTextStyle} />
            </XAxis>
            <YAxis type="category" dataKey="feature" width={156} tick={chartTextStyle} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              formatter={(v: any, _: any, p: any) => [
                (v as number).toFixed(4), p.payload.direction === 'bot' ? 'Correlates → Bot' : 'Correlates → Genuine'
              ] as any}
            />
            <Bar
              dataKey="correlation"
              radius={[0, 4, 4, 0]}
              barSize={14}
              fill="#1d9bf0"
              name="Correlation"
            />
          </BarChart>
        </ResponsiveContainer>
      </Card>
    </div>
  );
}
