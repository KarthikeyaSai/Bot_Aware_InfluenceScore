import { useEffect, useRef } from 'react';
import { Card } from './Card';

interface MetricCardProps {
  label: string;
  value: number;
  unit?: string;
  color?: 'blue' | 'red' | 'green' | 'orange' | 'purple';
  index?: number;
}

const colorMap: Record<string, string> = {
  blue:   'text-blue',
  red:    'text-red',
  green:  'text-green',
  orange: 'text-orange',
  purple: 'text-purple',
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
      const current = Math.round(value * t * 100) / 100;
      el.textContent = current.toLocaleString(undefined, { maximumFractionDigits: 2 });
      if (t < 1) requestAnimationFrame(tick);
      else el.textContent = value.toLocaleString(undefined, { maximumFractionDigits: 2 });
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
