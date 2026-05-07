export function BotProbGauge({ prob }: { prob: number }) {
  const pct   = Math.min(Math.max(prob, 0), 1);
  const color = pct >= 0.7 ? '#f4212e' : pct <= 0.3 ? '#00ba7c' : '#ff7043';

  const R = 60, cx = 80, cy = 80;
  const circumference     = Math.PI * R;
  const strokeDashoffset  = circumference * (1 - pct);

  return (
    <div className="flex flex-col items-center">
      <svg width="160" height="90" viewBox="0 0 160 90">
        {/* Track */}
        <path
          d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`}
          fill="none"
          stroke="var(--bg-overlay)"
          strokeWidth="12"
          strokeLinecap="round"
        />
        {/* Fill arc */}
        <path
          d={`M ${cx - R} ${cy} A ${R} ${R} 0 0 1 ${cx + R} ${cy}`}
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ transition: 'stroke-dashoffset 600ms cubic-bezier(0.16,1,0.3,1)' }}
        />
        {/* Percentage */}
        <text
          x={cx} y={cy - 4}
          textAnchor="middle"
          fill="var(--text-primary)"
          fontSize="20"
          fontWeight="700"
        >
          {(pct * 100).toFixed(0)}%
        </text>
        {/* Label */}
        <text
          x={cx} y={cy + 14}
          textAnchor="middle"
          fill="var(--text-secondary)"
          fontSize="11"
        >
          Bot Probability
        </text>
      </svg>
    </div>
  );
}
