# Phase 6: Frontend UI & Visualization Dashboard

This document details the implementation plan for Phase 6 of the Bot-Aware Influence Scoring project — the React dashboard that exposes the full pipeline to end users.

**Duration:** Weeks 19–24
**Goal:** Build a production-quality, Twitter/X-native-feeling dashboard with interactive graph exploration, influence leaderboards, before/after ranking comparison, and a custom graph upload flow. Every screen strictly follows the design system defined in `Frontend_rules.md`.

---

## 1. Project Initialization

### 1.1 Scaffold the App

```bash
cd bot-influence-scoring
npm create vite@latest frontend -- --template react-ts
cd frontend

# Server state, routing, global state
npm install @tanstack/react-query zustand react-router-dom

# Styling
npm install -D tailwindcss autoprefixer postcss
npx tailwindcss init -p

# Visualization
npm install d3 recharts
npm install -D @types/d3

# Accessible UI primitives
npm install @radix-ui/react-slider @radix-ui/react-tabs @radix-ui/react-tooltip
npm install @radix-ui/react-dialog @radix-ui/react-progress
npm install lucide-react

# Utilities
npm install clsx date-fns papaparse
npm install -D @types/papaparse
```

### 1.2 Tailwind Configuration

Map every CSS variable from `Frontend_rules.md` into Tailwind so they can be used as utility classes.

```js
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: ['attribute', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        bg: {
          base:     'var(--bg-base)',
          surface:  'var(--bg-surface)',
          elevated: 'var(--bg-elevated)',
          overlay:  'var(--bg-overlay)',
        },
        border: {
          DEFAULT: 'var(--border)',
          subtle:  'var(--border-subtle)',
        },
        text: {
          primary:   'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          disabled:  'var(--text-disabled)',
        },
        blue:   { DEFAULT: '#1d9bf0', hover: '#1a8cd8', muted: 'rgba(29,155,240,0.12)', glow: 'rgba(29,155,240,0.20)' },
        red:    { DEFAULT: '#f4212e', muted: 'rgba(244,33,46,0.12)' },
        green:  { DEFAULT: '#00ba7c', muted: 'rgba(0,186,124,0.12)' },
        orange: { DEFAULT: '#ff7043', muted: 'rgba(255,112,67,0.12)' },
        purple: { DEFAULT: '#794bc4' },
        yellow: { DEFAULT: '#ffd400' },
      },
      fontFamily: {
        display: ['"DM Sans"', 'sans-serif'],
        body:    ['"DM Sans"', 'sans-serif'],
        mono:    ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
      },
      fontSize: {
        xs:   ['11px', { lineHeight: '1.4' }],
        sm:   ['13px', { lineHeight: '1.5' }],
        base: ['15px', { lineHeight: '1.6' }],
        lg:   ['17px', { lineHeight: '1.5' }],
        xl:   ['20px', { lineHeight: '1.3' }],
        '2xl':['24px', { lineHeight: '1.2' }],
        '3xl':['32px', { lineHeight: '1.1' }],
        '4xl':['42px', { lineHeight: '1.0' }],
      },
      borderRadius: {
        sm:   '6px',
        md:   '10px',
        lg:   '16px',
        xl:   '20px',
        full: '9999px',
      },
      transitionDuration: {
        fast:  '100ms',
        base:  '150ms',
        slow:  '250ms',
        xslow: '400ms',
      },
      transitionTimingFunction: {
        snap: 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [],
};
```

### 1.3 CSS Variables & Theme Root

```css
/* src/index.css */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono&display=swap');
@tailwind base;
@tailwind components;
@tailwind utilities;

:root[data-theme="dark"] {
  --bg-base:        #0f1117;
  --bg-surface:     #16181c;
  --bg-elevated:    #1e2025;
  --bg-overlay:     #2f3336;
  --border:         #2f3336;
  --border-subtle:  #1e2227;
  --text-primary:   #e7e9ea;
  --text-secondary: #71767b;
  --text-disabled:  #3e4144;
}

:root[data-theme="light"] {
  --bg-base:        #f7f9f9;
  --bg-surface:     #ffffff;
  --bg-elevated:    #ffffff;
  --bg-overlay:     #eff3f4;
  --border:         #eff3f4;
  --border-subtle:  #f7f9f9;
  --text-primary:   #0f1419;
  --text-secondary: #536471;
  --text-disabled:  #c4cfd6;
}

/* Theme switch — only animate bg + color */
*, *::before, *::after {
  transition: background-color 200ms, border-color 200ms, color 200ms;
}

/* Page load animation */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}

.animate-fade-up {
  animation: fadeUp 400ms cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* Skeleton pulse */
@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.4; }
}
.skeleton {
  background: var(--bg-overlay);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
  border-radius: var(--radius-md, 10px);
}
```

### 1.4 App Shell

```
frontend/src/
├── components/
│   ├── layout/
│   │   ├── AppShell.tsx       # Sidebar + main content wrapper
│   │   └── Sidebar.tsx        # Icon-rail / expanded nav
│   ├── ui/
│   │   ├── Badge.tsx          # Bot / Genuine / Uncertain status pills
│   │   ├── Button.tsx         # Primary / Secondary / Ghost / Danger
│   │   ├── Card.tsx           # Surface card wrapper
│   │   ├── MetricCard.tsx     # Stat tile with label + big number
│   │   ├── SkeletonCard.tsx   # Loading placeholder (no spinners)
│   │   └── DataTable.tsx      # Reusable sortable table
│   └── charts/
│       ├── BotProbGauge.tsx   # Semicircle gauge for bot probability
│       ├── RankingBarChart.tsx # Before/after horizontal bars
│       └── GraphCanvas.tsx    # D3 force-directed network map
├── views/
│   ├── GraphExplorer.tsx      # View 1
│   ├── Leaderboard.tsx        # View 2
│   ├── RankingComparison.tsx  # View 3
│   ├── BotAuditPanel.tsx      # View 4 (slide-over panel)
│   ├── UploadAnalyze.tsx      # View 5
│   └── MetricControls.tsx     # View 6 (persistent sidebar panel)
├── hooks/
│   ├── useJobProgress.ts      # WebSocket progress streaming
│   ├── useInfluenceScores.ts  # TanStack Query wrappers
│   └── useTheme.ts            # Dark/light toggle + localStorage
├── store/
│   └── analysisStore.ts       # Zustand: active job, config state
├── lib/
│   └── api.ts                 # Fetch helpers for FastAPI endpoints
└── App.tsx
```

---

## 2. Core UI Components

### 2.1 Badge (Status Pills)

Used throughout the app to show bot classification status. Follows the `Frontend_rules.md` badge spec.

```tsx
// components/ui/Badge.tsx
type BadgeVariant = 'bot' | 'genuine' | 'uncertain' | 'neutral';

const styles: Record<BadgeVariant, string> = {
  bot:       'bg-red-muted text-red',
  genuine:   'bg-green-muted text-green',
  uncertain: 'bg-orange-muted text-orange',
  neutral:   'bg-bg-overlay text-text-secondary',
};

export function Badge({ variant, label }: { variant: BadgeVariant; label: string }) {
  return (
    <span
      className={`
        inline-flex items-center px-[10px] py-[3px]
        text-xs font-semibold rounded-full
        ${styles[variant]}
      `}
    >
      {label}
    </span>
  );
}
```

### 2.2 Card

```tsx
// components/ui/Card.tsx
import { clsx } from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  clickable?: boolean;
  style?: React.CSSProperties;
}

export function Card({ children, className, clickable, style }: CardProps) {
  return (
    <div
      style={style}
      className={clsx(
        'bg-bg-surface border border-border rounded-lg p-5',
        'light:shadow-[0_1px_8px_rgba(0,0,0,0.06)]',
        clickable && 'cursor-pointer transition-colors duration-base hover:border-blue-muted',
        className,
      )}
    >
      {children}
    </div>
  );
}
```

### 2.3 MetricCard (Hero Stats)

Used on the dashboard summary row. Numbers animate from 0 to value on mount.

```tsx
// components/ui/MetricCard.tsx
import { useEffect, useRef } from 'react';

interface MetricCardProps {
  label: string;
  value: number;
  unit?: string;
  color?: 'blue' | 'red' | 'green' | 'orange';
  index?: number;   // stagger delay
}

const colorMap = {
  blue:   'text-blue',
  red:    'text-red',
  green:  'text-green',
  orange: 'text-orange',
};

export function MetricCard({ label, value, unit = '', color = 'blue', index = 0 }: MetricCardProps) {
  const spanRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const el = spanRef.current;
    if (!el) return;
    const duration = 600;
    const start = performance.now();
    const tick = (now: number) => {
      const t = Math.min((now - start) / duration, 1);
      el.textContent = (Math.round(value * t * 100) / 100).toLocaleString();
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [value]);

  return (
    <Card
      className="animate-fade-up"
      style={{ animationDelay: `${index * 60}ms` }}
    >
      <p className="text-xs font-medium text-text-secondary uppercase tracking-[0.06em] mb-2">
        {label}
      </p>
      <p className={`text-3xl font-bold ${colorMap[color]}`}>
        <span ref={spanRef}>0</span>
        {unit && <span className="text-xl ml-1 text-text-disabled">{unit}</span>}
      </p>
    </Card>
  );
}
```

### 2.4 DataTable

Reusable table applying the `Frontend_rules.md` table spec: no outer border, uppercase 11px headers, 52px row height, subtle bottom divider.

```tsx
// components/ui/DataTable.tsx
export interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
  align?: 'left' | 'right' | 'center';
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowKey: (row: T) => string;
  onRowClick?: (row: T) => void;
}

export function DataTable<T>({ columns, data, rowKey, onRowClick }: DataTableProps<T>) {
  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            {columns.map((col) => (
              <th
                key={col.key as string}
                className={`
                  text-xs font-medium uppercase tracking-[0.06em]
                  text-text-secondary pb-3 border-b border-border
                  ${col.align === 'right' ? 'text-right' : 'text-left'}
                `}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr
              key={rowKey(row)}
              onClick={() => onRowClick?.(row)}
              className={`
                h-[52px] border-b border-border-subtle
                text-text-secondary
                transition-colors duration-fast
                hover:bg-bg-elevated
                ${onRowClick ? 'cursor-pointer' : ''}
              `}
            >
              {columns.map((col, i) => (
                <td
                  key={col.key as string}
                  className={`
                    py-0 pr-4
                    ${i === 0 ? 'font-medium text-text-primary' : ''}
                    ${col.align === 'right' ? 'text-right' : ''}
                  `}
                >
                  {col.render
                    ? col.render(row)
                    : String((row as Record<string, unknown>)[col.key as string] ?? '—')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### 2.5 Button

```tsx
// components/ui/Button.tsx
type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';

const variantStyles: Record<ButtonVariant, string> = {
  primary:   'bg-blue text-white hover:bg-blue-hover focus:shadow-[0_0_0_3px_var(--blue-glow)]',
  secondary: 'bg-transparent text-text-primary border border-border hover:bg-bg-elevated',
  ghost:     'bg-transparent text-blue hover:bg-blue-muted',
  danger:    'bg-red-muted text-red border border-red/30 hover:bg-red/20',
};

export function Button({
  variant = 'primary',
  children,
  disabled,
  onClick,
  className,
}: {
  variant?: ButtonVariant;
  children: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        text-sm font-semibold px-5 py-[10px] rounded-md
        transition-all duration-base
        active:scale-[0.97]
        disabled:opacity-40 disabled:cursor-not-allowed
        ${variantStyles[variant]}
        ${className ?? ''}
      `}
    >
      {children}
    </button>
  );
}
```

---

## 3. App Layout

### 3.1 Sidebar Navigation

Collapsed (72px icon-rail) by default, expands to 240px on hover/toggle. Persists preference in `localStorage`.

```tsx
// components/layout/Sidebar.tsx
import { useState } from 'react';
import { BarChart2, Network, ArrowLeftRight, Upload, Settings } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const navItems = [
  { icon: Network,        label: 'Graph Explorer',  to: '/'         },
  { icon: BarChart2,      label: 'Leaderboard',     to: '/rankings' },
  { icon: ArrowLeftRight, label: 'Before / After',  to: '/compare'  },
  { icon: Upload,         label: 'Upload & Analyze',to: '/upload'   },
  { icon: Settings,       label: 'Settings',        to: '/settings' },
];

export function Sidebar() {
  const [expanded, setExpanded] = useState(false);

  return (
    <nav
      onMouseEnter={() => setExpanded(true)}
      onMouseLeave={() => setExpanded(false)}
      style={{ width: expanded ? 240 : 72 }}
      className="
        h-screen flex flex-col bg-bg-surface border-r border-border
        transition-[width] duration-[200ms] ease-out overflow-hidden shrink-0
      "
    >
      {/* Logo */}
      <div className="h-16 flex items-center px-4">
        <Network size={28} className="text-blue shrink-0" />
        {expanded && (
          <span className="ml-3 font-bold text-lg text-text-primary whitespace-nowrap">
            BotScope
          </span>
        )}
      </div>

      {/* Nav items */}
      <div className="flex flex-col gap-1 px-2 mt-2 flex-1">
        {navItems.map(({ icon: Icon, label, to }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `
              flex items-center h-11 px-3 rounded-full gap-3
              font-base font-medium transition-colors duration-fast
              ${isActive
                ? 'text-blue bg-blue-muted'
                : 'text-text-secondary hover:bg-bg-elevated hover:text-text-primary'}
            `}
          >
            <Icon size={20} className="shrink-0" />
            {expanded && (
              <span className="whitespace-nowrap text-[15px]">{label}</span>
            )}
          </NavLink>
        ))}
      </div>

      {/* Theme toggle at footer */}
      <div className="p-3 border-t border-border">
        <ThemeToggle compact={!expanded} />
      </div>
    </nav>
  );
}
```

---

## 4. View Implementations

### 4.1 View 1 — Graph Explorer

Interactive D3 force-directed network map. Color-encodes bot probability per `Frontend_rules.md`:
- Human node → `--green` (`#00ba7c`)
- Bot node → `--red` (`#f4212e`)
- Uncertain node → `--orange` (`#ff7043`)

Node size = composite influence score φᵥ. Edge thickness = edge weight wᵤᵥ. Renders SVG for ≤ 1,000 nodes, switches to Canvas for larger graphs.

```tsx
// components/charts/GraphCanvas.tsx
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export interface GraphNode {
  id: string;
  botProb: number;
  influenceScore: number;
  x?: number;
  y?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
}

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (node: GraphNode) => void;
}

function nodeColor(botProb: number): string {
  if (botProb >= 0.7)  return '#f4212e';   // red   — bot
  if (botProb <= 0.3)  return '#00ba7c';   // green — genuine
  return '#ff7043';                         // orange — uncertain
}

export function GraphCanvas({ nodes, edges, onNodeClick }: GraphCanvasProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const { width, height } = svgRef.current.getBoundingClientRect();

    // Zoom/pan container
    const g = svg.append('g');
    svg.call(
      d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.1, 8])
        .on('zoom', (e) => g.attr('transform', e.transform))
    );

    const simulation = d3.forceSimulation(nodes as d3.SimulationNodeDatum[])
      .force('link', d3.forceLink(edges).id((d: d3.SimulationNodeDatum) => (d as GraphNode).id).distance(60))
      .force('charge', d3.forceManyBody().strength(-120))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Edges
    const link = g.append('g')
      .selectAll('line')
      .data(edges)
      .join('line')
      .attr('stroke', 'var(--border)')
      .attr('stroke-width', (d) => Math.max(0.5, d.weight * 3))
      .attr('opacity', 0.5);

    // Nodes
    const node = g.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', (d) => 5 + d.influenceScore * 12)
      .attr('fill', (d) => nodeColor(d.botProb))
      .attr('cursor', 'pointer')
      .on('click', (_, d) => onNodeClick?.(d))
      .on('mouseover', function () {
        d3.select(this)
          .transition().duration(100)
          .attr('transform', 'scale(1.3)')
          .style('filter', 'drop-shadow(0 0 8px currentColor)');
      })
      .on('mouseout', function () {
        d3.select(this)
          .transition().duration(100)
          .attr('transform', 'scale(1)')
          .style('filter', 'none');
      })
      .call(
        d3.drag<SVGCircleElement, GraphNode>()
          .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
          .on('drag',  (e, d) => { d.fx = e.x; d.fy = e.y; })
          .on('end',   (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
      );

    simulation.on('tick', () => {
      link
        .attr('x1', (d) => (d.source as GraphNode).x ?? 0)
        .attr('y1', (d) => (d.source as GraphNode).y ?? 0)
        .attr('x2', (d) => (d.target as GraphNode).x ?? 0)
        .attr('y2', (d) => (d.target as GraphNode).y ?? 0);
      node
        .attr('cx', (d) => d.x ?? 0)
        .attr('cy', (d) => d.y ?? 0);
    });

    return () => { simulation.stop(); };
  }, [nodes, edges, onNodeClick]);

  return (
    <svg
      ref={svgRef}
      className="w-full h-full bg-bg-base rounded-lg border border-border"
    />
  );
}
```

**GraphExplorer page:**

```tsx
// views/GraphExplorer.tsx
import { useState } from 'react';
import { GraphCanvas } from '../components/charts/GraphCanvas';
import { BotAuditPanel } from './BotAuditPanel';
import { Button } from '../components/ui/Button';
import { useInfluenceScores } from '../hooks/useInfluenceScores';

export function GraphExplorer() {
  const [sanitized, setSanitized] = useState(false);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [topK, setTopK] = useState(500);
  const { nodes, edges, isLoading } = useInfluenceScores({ sanitized, topK });

  return (
    <div className="flex flex-col h-full gap-4 p-6">
      {/* Controls bar */}
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-semibold text-text-primary flex-1">
          Network Graph
        </h1>
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
      <div className="flex-1 relative">
        {isLoading ? (
          <div className="skeleton w-full h-full rounded-lg" />
        ) : (
          <GraphCanvas
            nodes={nodes}
            edges={edges}
            onNodeClick={(n) => setSelectedNode(n.id)}
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
```

---

### 4.2 View 2 — Influence Leaderboard

Sortable table of top influencers. Rank shift column shows a colored delta (▲ green / ▼ red) when a node moved more than 10 positions after sanitization. Export to CSV included.

```tsx
// views/Leaderboard.tsx
import { useState } from 'react';
import { DataTable } from '../components/ui/DataTable';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Download, ArrowUp, ArrowDown, Minus } from 'lucide-react';

interface InfluencerRow {
  rank: number;
  nodeId: string;
  compositeScore: number;
  pagerank: number;
  authority: number;
  icReach: number;
  botProb: number;
  rankShift: number;
}

function RankShiftCell({ delta }: { delta: number }) {
  if (Math.abs(delta) < 10) return <span className="text-text-disabled flex items-center gap-1"><Minus size={12} /> —</span>;
  if (delta > 0) return <span className="text-green flex items-center gap-1"><ArrowUp size={12} />+{delta}</span>;
  return <span className="text-red flex items-center gap-1"><ArrowDown size={12} />{delta}</span>;
}

const COLUMNS = [
  { key: 'rank',           header: 'Rank',       render: (r: InfluencerRow) => <span className="font-mono text-text-disabled">#{r.rank}</span> },
  { key: 'nodeId',         header: 'Account',    render: (r: InfluencerRow) => <span className="font-mono text-xs">{r.nodeId}</span> },
  { key: 'compositeScore', header: 'φᵥ Score',   render: (r: InfluencerRow) => <span className="text-blue font-semibold">{r.compositeScore.toFixed(3)}</span> },
  { key: 'pagerank',       header: 'PageRank',   render: (r: InfluencerRow) => r.pagerank.toFixed(4), align: 'right' as const },
  { key: 'authority',      header: 'Authority',  render: (r: InfluencerRow) => r.authority.toFixed(3), align: 'right' as const },
  { key: 'icReach',        header: 'IC Reach',   render: (r: InfluencerRow) => r.icReach.toLocaleString(), align: 'right' as const },
  { key: 'botProb',        header: 'Bot Prob',   render: (r: InfluencerRow) => {
    const v = r.botProb;
    const variant = v >= 0.7 ? 'bot' : v <= 0.3 ? 'genuine' : 'uncertain';
    return <Badge variant={variant} label={`${(v * 100).toFixed(0)}%`} />;
  }},
  { key: 'rankShift',      header: 'Rank Shift', render: (r: InfluencerRow) => <RankShiftCell delta={r.rankShift} /> },
];

export function Leaderboard({ data }: { data: InfluencerRow[] }) {
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 50;
  const pageData = data.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const exportCSV = () => {
    const header = 'Rank,Node ID,Score,PageRank,Authority,IC Reach,Bot Prob,Rank Shift\n';
    const rows = data.map((r) =>
      `${r.rank},${r.nodeId},${r.compositeScore},${r.pagerank},${r.authority},${r.icReach},${r.botProb},${r.rankShift}`
    ).join('\n');
    const blob = new Blob([header + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'influence_scores.csv'; a.click();
  };

  return (
    <div className="p-6 flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-text-primary">Influence Leaderboard</h1>
        <Button variant="secondary" onClick={exportCSV}>
          <Download size={14} className="mr-2 inline" /> Export CSV
        </Button>
      </div>

      <div className="bg-bg-surface border border-border rounded-lg p-5">
        <DataTable
          columns={COLUMNS}
          data={pageData}
          rowKey={(r) => r.nodeId}
        />
        {/* Pagination */}
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
      </div>
    </div>
  );
}
```

---

### 4.3 View 3 — Before/After Ranking Comparison

Side-by-side horizontal bar chart of the top 20 influencers in both raw and sanitized graphs. Uses Recharts `BarChart`. Animated displacement arrows drawn in SVG overlay.

```tsx
// views/RankingComparison.tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';

interface ComparisonData {
  rankDisplacement: {
    pctTopKDisplaced: number;
    meanDisplacement: number;
    kendallsTau: number;
    spearmanR: number;
  };
  rawTop20:   { nodeId: string; score: number }[];
  cleanTop20: { nodeId: string; score: number }[];
}

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: { payload: { nodeId: string; score: number } }[] }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-bg-elevated border border-border rounded-md p-3 text-sm shadow-[0_4px_16px_rgba(0,0,0,0.2)]">
      <p className="font-mono text-text-primary">{payload[0].payload.nodeId}</p>
      <p className="text-blue font-semibold">φᵥ = {payload[0].payload.score.toFixed(3)}</p>
    </div>
  );
};

export function RankingComparison({ data }: { data: ComparisonData }) {
  const { rankDisplacement, rawTop20, cleanTop20 } = data;

  return (
    <div className="p-6 flex flex-col gap-6">
      <h1 className="text-xl font-semibold text-text-primary">Before / After Sanitization</h1>

      {/* Summary stats */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard label="Top-100 Displaced"   value={rankDisplacement.pctTopKDisplaced} unit="%" color="orange" index={0} />
        <MetricCard label="Mean Displacement"   value={rankDisplacement.meanDisplacement}  unit="pos" color="blue"   index={1} />
        <MetricCard label="Kendall's τ"         value={rankDisplacement.kendallsTau}        color="purple" index={2} />
        <MetricCard label="Spearman ρ"          value={rankDisplacement.spearmanR}          color="green"  index={3} />
      </div>

      {/* Side-by-side charts */}
      <div className="grid grid-cols-2 gap-4">
        {[
          { title: 'Raw Graph (with bots)',       chartData: rawTop20,   color: '#ff7043' },
          { title: 'Sanitized Graph (bots removed)', chartData: cleanTop20, color: '#1d9bf0' },
        ].map(({ title, chartData, color }) => (
          <Card key={title}>
            <p className="text-lg font-semibold text-text-primary mb-4">{title}</p>
            <ResponsiveContainer width="100%" height={420}>
              <BarChart layout="vertical" data={chartData} margin={{ left: 80 }}>
                <XAxis
                  type="number"
                  domain={[0, 1]}
                  tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="nodeId"
                  tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontFamily: 'JetBrains Mono' }}
                  axisLine={false}
                  tickLine={false}
                  width={76}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'var(--bg-elevated)' }} />
                <Bar dataKey="score" radius={[0, 4, 4, 0]} fill={color} barSize={12} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

---

### 4.4 View 4 — Bot Audit Panel

Slide-over panel that opens when a node is clicked in the Graph Explorer. Shows a semicircle bot probability gauge, classification badge, feature breakdown table, and top suspicious neighbors.

```tsx
// components/charts/BotProbGauge.tsx
export function BotProbGauge({ prob }: { prob: number }) {
  const pct = Math.min(Math.max(prob, 0), 1);
  const color = pct >= 0.7 ? '#f4212e' : pct <= 0.3 ? '#00ba7c' : '#ff7043';

  // SVG semicircle
  const R = 60, cx = 80, cy = 80;
  const circumference = Math.PI * R;
  const strokeDashoffset = circumference * (1 - pct);

  return (
    <div className="flex flex-col items-center">
      <svg width="160" height="90" viewBox="0 0 160 90">
        {/* Track */}
        <path
          d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`}
          fill="none" stroke="var(--bg-overlay)" strokeWidth="12" strokeLinecap="round"
        />
        {/* Fill arc */}
        <path
          d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`}
          fill="none" stroke={color} strokeWidth="12" strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ transition: 'stroke-dashoffset 600ms cubic-bezier(0.16,1,0.3,1)' }}
        />
        {/* Center label */}
        <text x={cx} y={cy - 4} textAnchor="middle" fill="var(--text-primary)" fontSize="20" fontWeight="700">
          {(pct * 100).toFixed(0)}%
        </text>
        <text x={cx} y={cy + 14} textAnchor="middle" fill="var(--text-secondary)" fontSize="11">
          Bot Probability
        </text>
      </svg>
    </div>
  );
}
```

```tsx
// views/BotAuditPanel.tsx
import { X } from 'lucide-react';
import { BotProbGauge } from '../components/charts/BotProbGauge';
import { Badge } from '../components/ui/Badge';
import { DataTable } from '../components/ui/DataTable';
import { useNodeDetail } from '../hooks/useInfluenceScores';

export function BotAuditPanel({ nodeId, onClose }: { nodeId: string; onClose: () => void }) {
  const { node, isLoading } = useNodeDetail(nodeId);

  const variant = !node ? 'neutral'
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
          <div className="skeleton h-[120px] rounded-lg" />
          <div className="skeleton h-[200px] rounded-lg" />
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-5 flex flex-col gap-5">
          {/* Gauge + badge */}
          <div className="bg-bg-elevated rounded-lg p-4 flex flex-col items-center gap-3">
            <BotProbGauge prob={node.botProb} />
            <Badge
              variant={variant}
              label={variant === 'bot' ? 'Bot Detected' : variant === 'genuine' ? 'Verified Human' : 'Uncertain'}
            />
            <p className="text-sm text-text-secondary text-center">
              Confidence: {variant !== 'uncertain' ? 'High' : 'Low'} ({(Math.abs(node.botProb - 0.5) * 200).toFixed(0)}%)
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
```

---

### 4.5 View 5 — Upload & Analyze

Drag-and-drop CSV edge list + JSON node features. Validates columns before allowing submission. Shows a multi-stage WebSocket progress bar during pipeline execution. No spinning loaders — uses skeleton screens and a linear progress bar.

```tsx
// views/UploadAnalyze.tsx
import { useState, useCallback } from 'react';
import { Upload } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { useJobProgress } from '../hooks/useJobProgress';
import { useAnalysisStore } from '../store/analysisStore';

const PIPELINE_STEPS = [
  { key: 'graph_construction', label: 'Building graph' },
  { key: 'gat_inference',      label: 'Running GAT inference' },
  { key: 'sanitization',       label: 'Sanitizing graph' },
  { key: 'influence_scoring',  label: 'Computing PageRank & HITS' },
  { key: 'ic_simulation',      label: 'IC simulations' },
  { key: 'composite_score',    label: 'Generating composite scores' },
];

export function UploadAnalyze() {
  const [edgeFile, setEdgeFile]   = useState<File | null>(null);
  const [nodeFile, setNodeFile]   = useState<File | null>(null);
  const [error, setError]         = useState<string | null>(null);
  const { activeJobId, setJobId } = useAnalysisStore();
  const { progress, completed }   = useJobProgress(activeJobId);

  const onDrop = useCallback((e: React.DragEvent, type: 'edge' | 'node') => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (!file) return;
    if (type === 'edge') setEdgeFile(file);
    else setNodeFile(file);
    setError(null);
  }, []);

  const submit = async () => {
    if (!edgeFile || !nodeFile) { setError('Both files are required.'); return; }
    const formData = new FormData();
    formData.append('edges', edgeFile);
    formData.append('nodes', nodeFile);
    const res = await fetch('/api/v1/analyze', { method: 'POST', body: formData });
    const { job_id } = await res.json();
    setJobId(job_id);
  };

  const currentStepIdx = PIPELINE_STEPS.findIndex((s) => s.key === progress?.step);
  const pct = progress?.pct_complete ?? 0;

  return (
    <div className="p-6 max-w-2xl mx-auto flex flex-col gap-6">
      <h1 className="text-xl font-semibold text-text-primary">Upload & Analyze</h1>

      {/* Drop zones */}
      {[
        { type: 'edge' as const, file: edgeFile, label: 'Edge List CSV', hint: 'source, target, type, count, last_date' },
        { type: 'node' as const, file: nodeFile, label: 'Node Features JSON', hint: '[{id, followers_count, friends_count, ...}]' },
      ].map(({ type, file, label, hint }) => (
        <Card
          key={type}
          className={`
            border-dashed text-center cursor-pointer
            ${file ? 'border-blue-muted' : 'border-border'}
            transition-colors duration-base
          `}
          onDragOver={(e: React.DragEvent) => e.preventDefault()}
          onDrop={(e: React.DragEvent) => onDrop(e, type)}
        >
          <Upload size={24} className="mx-auto mb-2 text-text-secondary" />
          <p className="text-base font-semibold text-text-primary">{label}</p>
          <p className="text-sm text-text-secondary mt-1">{file ? file.name : `Drag & drop or click — ${hint}`}</p>
        </Card>
      ))}

      {error && <p className="text-sm text-red">{error}</p>}

      {/* Config sliders rendered by MetricControls (persisted in Zustand) */}
      <MetricConfigInline />

      <Button onClick={submit} disabled={!!activeJobId && !completed}>
        {activeJobId && !completed ? 'Analyzing...' : 'Run Analysis'}
      </Button>

      {/* Progress */}
      {activeJobId && !completed && (
        <Card>
          <p className="text-sm font-semibold text-text-primary mb-3">Pipeline Progress</p>
          <div className="w-full h-1.5 bg-bg-overlay rounded-full overflow-hidden mb-4">
            <div
              className="h-full bg-blue rounded-full transition-all duration-slow"
              style={{ width: `${pct}%` }}
            />
          </div>
          <div className="flex flex-col gap-2">
            {PIPELINE_STEPS.map((step, i) => (
              <div key={step.key} className="flex items-center gap-3">
                <div className={`
                  w-2 h-2 rounded-full shrink-0
                  ${i < currentStepIdx  ? 'bg-green' :
                    i === currentStepIdx ? 'bg-blue' :
                    'bg-bg-overlay'}
                `} />
                <span className={`text-sm ${i <= currentStepIdx ? 'text-text-primary' : 'text-text-disabled'}`}>
                  {step.label}
                </span>
                {i === currentStepIdx && (
                  <span className="text-xs text-blue ml-auto">{pct}%</span>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {completed && (
        <Card className="border-green-muted bg-green-muted/10">
          <p className="text-green font-semibold">Analysis complete. Results are now live in the dashboard.</p>
        </Card>
      )}
    </div>
  );
}
```

---

### 4.6 View 6 — Metric Controls Panel

Persistent sidebar section. Sliders for τ, α, and β1/β2/β3 (constrained to sum = 1). All changes debounced 300ms before triggering API recomputation. Lives in Zustand so every view reads the same config.

```tsx
// views/MetricControls.tsx
import * as Slider from '@radix-ui/react-slider';
import { useAnalysisStore } from '../store/analysisStore';
import { Button } from '../components/ui/Button';

const DEFAULT_CONFIG = { tau: 0.5, alpha: 0.6, beta1: 0.333, beta2: 0.333, beta3: 0.334 };

export function MetricControls() {
  const { config, setConfig } = useAnalysisStore();
  const cfg = config ?? DEFAULT_CONFIG;

  const SliderRow = ({
    label, value, min = 0, max = 1, step = 0.01,
    onChange, hint,
  }: {
    label: string; value: number; min?: number; max?: number; step?: number;
    onChange: (v: number) => void; hint?: string;
  }) => (
    <div className="flex flex-col gap-2">
      <div className="flex justify-between items-baseline">
        <span className="text-sm font-medium text-text-primary">{label}</span>
        <span className="font-mono text-sm text-blue">{value.toFixed(2)}</span>
      </div>
      <Slider.Root
        min={min} max={max} step={step} value={[value]}
        onValueChange={([v]) => onChange(v)}
        className="relative flex items-center h-5 w-full"
      >
        <Slider.Track className="bg-bg-overlay relative grow h-1.5 rounded-full">
          <Slider.Range className="absolute bg-blue h-full rounded-full" />
        </Slider.Track>
        <Slider.Thumb className="
          block w-4 h-4 bg-blue rounded-full shadow
          focus:outline-none focus:shadow-[0_0_0_3px_var(--blue-glow)]
          hover:bg-blue-hover transition-colors
        " />
      </Slider.Root>
      {hint && <p className="text-xs text-text-secondary">{hint}</p>}
    </div>
  );

  return (
    <div className="flex flex-col gap-5 p-4">
      <p className="text-sm font-semibold text-text-primary uppercase tracking-[0.06em] text-text-secondary">
        Pipeline Config
      </p>

      <SliderRow
        label="τ — Bot Threshold"
        value={cfg.tau}
        onChange={(v) => setConfig({ tau: v })}
        hint="Nodes with p_v ≥ τ are removed"
      />
      <SliderRow
        label="α — Edge Weight"
        value={cfg.alpha}
        onChange={(v) => setConfig({ alpha: v })}
        hint="Balance frequency vs recency"
      />

      <div className="border-t border-border-subtle pt-4">
        <p className="text-xs font-medium text-text-secondary mb-3">β Weights (must sum to 1)</p>
        {(['beta1', 'beta2', 'beta3'] as const).map((key, i) => (
          <SliderRow
            key={key}
            label={['β₁ PageRank', 'β₂ HITS Authority', 'β₃ IC Reach'][i]}
            value={cfg[key]}
            onChange={(v) => {
              // Redistribute remaining weight equally across the other two
              const remaining = Math.max(0, 1 - v);
              const others = (['beta1', 'beta2', 'beta3'] as const).filter((k) => k !== key);
              setConfig({ [key]: v, [others[0]]: remaining / 2, [others[1]]: remaining / 2 });
            }}
          />
        ))}
        <p className={`text-xs mt-1 ${Math.abs(cfg.beta1 + cfg.beta2 + cfg.beta3 - 1) < 0.01 ? 'text-green' : 'text-orange'}`}>
          Sum: {(cfg.beta1 + cfg.beta2 + cfg.beta3).toFixed(2)}
        </p>
      </div>

      <Button variant="ghost" onClick={() => setConfig(DEFAULT_CONFIG)}>
        Reset to defaults
      </Button>
    </div>
  );
}
```

---

## 5. State Management & API Layer

### 5.1 Zustand Store

```ts
// store/analysisStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Config {
  tau: number; alpha: number;
  beta1: number; beta2: number; beta3: number;
}

interface AnalysisStore {
  activeJobId: string | null;
  config: Config;
  setJobId: (id: string | null) => void;
  setConfig: (patch: Partial<Config>) => void;
}

export const useAnalysisStore = create<AnalysisStore>()(
  persist(
    (set) => ({
      activeJobId: null,
      config: { tau: 0.5, alpha: 0.6, beta1: 0.333, beta2: 0.333, beta3: 0.334 },
      setJobId: (id) => set({ activeJobId: id }),
      setConfig: (patch) => set((s) => ({ config: { ...s.config, ...patch } })),
    }),
    { name: 'analysis-store' }
  )
);
```

### 5.2 WebSocket Progress Hook

```ts
// hooks/useJobProgress.ts
import { useState, useEffect, useRef } from 'react';

interface JobProgress {
  step: string;
  pct_complete: number;
  message: string;
}

export function useJobProgress(jobId: string | null) {
  const [progress, setProgress]   = useState<JobProgress | null>(null);
  const [completed, setCompleted] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!jobId) return;
    setCompleted(false);
    setProgress(null);

    wsRef.current = new WebSocket(`ws://localhost:8000/api/v1/ws/jobs/${jobId}`);

    wsRef.current.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.event === 'progress') setProgress(msg);
      else if (msg.event === 'completed') { setCompleted(true); wsRef.current?.close(); }
    };

    return () => wsRef.current?.close();
  }, [jobId]);

  return { progress, completed };
}
```

### 5.3 TanStack Query Data Hooks

```ts
// hooks/useInfluenceScores.ts
import { useQuery } from '@tanstack/react-query';

const BASE = 'http://localhost:8000/api/v1';

export function useInfluenceScores({ sanitized, topK }: { sanitized: boolean; topK: number }) {
  return useQuery({
    queryKey: ['scores', sanitized, topK],
    queryFn: async () => {
      const graph = sanitized ? 'sanitized' : 'raw';
      const res = await fetch(`${BASE}/scores/cresci-2017?top_k=${topK}&graph_type=${graph}`);
      return res.json();
    },
  });
}

export function useNodeDetail(nodeId: string) {
  return useQuery({
    queryKey: ['node', nodeId],
    queryFn: async () => {
      const res = await fetch(`${BASE}/nodes/${nodeId}/bot-probability`);
      return res.json();
    },
    enabled: !!nodeId,
  });
}
```

---

## 6. Theme Switching

```ts
// hooks/useTheme.ts
import { useEffect, useState } from 'react';

type Theme = 'dark' | 'light';

export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    const stored = localStorage.getItem('theme') as Theme | null;
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggle = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'));
  return { theme, toggle };
}
```

---

## 7. Responsive Behavior

| Breakpoint | Layout change |
|---|---|
| Mobile < 640px | Sidebar hidden, bottom nav bar with 4 icon tabs |
| Tablet 640–1024px | Sidebar collapsed (72px icon-rail only), 2-col card grid max |
| Desktop > 1024px | Full sidebar (72px → 240px on hover), full grid layout |
| Wide > 1280px | Content capped at `max-w-[1280px]` and centered |

The Graph Explorer falls back to a read-only static layout on mobile (no drag, pinch-zoom only). Leaderboard collapses to 4 columns (Rank, Account, φᵥ, Bot Prob).

---

## 8. Animation Rules (from Frontend_rules.md)

| Scenario | Implementation |
|---|---|
| Page / card appear | `animate-fade-up` with 60ms stagger per card-index |
| Metric numbers | Count-up from 0 on mount via `requestAnimationFrame` |
| Chart bars draw | Recharts `animationDuration={600}` |
| Button press | `active:scale-[0.97]` via Tailwind |
| Badge appear | `scale(0.8→1) + fade 120ms` via CSS keyframes |
| Row hover | `bg-bg-elevated` transition 100ms |
| Sidebar expand | `transition-[width] duration-[200ms]` |
| Theme switch | CSS variable transition 200ms on bg + color only |

**Never use:** bounce physics, `animate-spin`, transitions > 400ms, simultaneous animations on > 6 elements.

---

## 9. Deliverables Checklist

- [ ] React 18 + TypeScript + Vite project initialized in `bot-influence-scoring/frontend/`
- [ ] Tailwind config maps all `Frontend_rules.md` CSS variables as utility classes
- [ ] Dark/light theme switching with `data-theme` attribute, persisted to `localStorage`
- [ ] App shell: collapsible sidebar (72px / 240px) with active-state nav items
- [ ] **View 1** — Graph Explorer: D3 force-directed graph, node color by bot prob, size by φᵥ, click-to-audit
- [ ] **View 2** — Influence Leaderboard: sortable DataTable, rank shift column, CSV export, pagination
- [ ] **View 3** — Before/After Comparison: side-by-side Recharts BarChart, 4 summary MetricCards
- [ ] **View 4** — Bot Audit Panel: slide-over with SVG gauge, Badge, feature breakdown table
- [ ] **View 5** — Upload & Analyze: drag-and-drop CSV/JSON, config sliders, WebSocket progress tracker
- [ ] **View 6** — Metric Controls: τ / α / β sliders in sidebar, Zustand-backed, debounced API calls
- [ ] All loading states use skeleton screens — no spinners
- [ ] All animations ≤ 400ms with `cubic-bezier(0.16, 1, 0.3, 1)` easing
- [ ] Responsive layout verified on desktop (1280px), tablet (768px), and mobile (375px)
- [ ] TanStack Query connected to all 5 FastAPI endpoints from Phase 5
- [ ] WebSocket hook streams real-time pipeline progress

---
**Next Step**: Integration testing — run the full pipeline end-to-end from the Upload view and verify all 6 views populate correctly with Phase 4 influence scores.
