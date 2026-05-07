import * as Slider from '@radix-ui/react-slider';
import { useAnalysisStore } from '../store/analysisStore';
import { Button } from '../components/ui/Button';

const DEFAULT_CONFIG = { tau: 0.5, alpha: 0.6, beta1: 0.333, beta2: 0.333, beta3: 0.334 };

interface SliderRowProps {
  label: string;
  value: number;
  min?: number;
  max?: number;
  step?: number;
  onChange: (v: number) => void;
  hint?: string;
}

function SliderRow({ label, value, min = 0, max = 1, step = 0.01, onChange, hint }: SliderRowProps) {
  return (
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
}

export function MetricControls() {
  const { config, setConfig } = useAnalysisStore();
  const cfg = config ?? DEFAULT_CONFIG;

  return (
    <div className="flex flex-col gap-5 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.06em] text-text-secondary">
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

      <div className="border-t border-border-subtle pt-4 flex flex-col gap-4">
        <p className="text-xs font-medium text-text-secondary">β Weights (must sum to 1)</p>
        {(['beta1', 'beta2', 'beta3'] as const).map((key, i) => (
          <SliderRow
            key={key}
            label={['β₁ PageRank', 'β₂ HITS Authority', 'β₃ IC Reach'][i]}
            value={cfg[key]}
            onChange={(v) => {
              const remaining = Math.max(0, 1 - v);
              const others = (['beta1', 'beta2', 'beta3'] as const).filter((k) => k !== key);
              setConfig({ [key]: v, [others[0]]: remaining / 2, [others[1]]: remaining / 2 });
            }}
          />
        ))}
        <p className={`text-xs ${Math.abs(cfg.beta1 + cfg.beta2 + cfg.beta3 - 1) < 0.01 ? 'text-green' : 'text-orange'}`}>
          Sum: {(cfg.beta1 + cfg.beta2 + cfg.beta3).toFixed(2)}
        </p>
      </div>

      <Button variant="ghost" onClick={() => setConfig(DEFAULT_CONFIG)}>
        Reset to defaults
      </Button>
    </div>
  );
}
