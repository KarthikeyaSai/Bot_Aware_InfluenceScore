import { Card } from '../components/ui/Card';
import { MetricControls } from './MetricControls';
import { useTheme } from '../hooks/useTheme';
import { Button } from '../components/ui/Button';

export function Settings() {
  const { theme, toggle } = useTheme();

  return (
    <div className="p-6 flex flex-col gap-6 max-w-2xl">
      <h1 className="text-xl font-semibold text-text-primary">Settings</h1>

      {/* Appearance */}
      <Card>
        <p className="text-lg font-semibold text-text-primary mb-4">Appearance</p>
        <div className="flex items-center justify-between py-3 border-b border-border-subtle">
          <div>
            <p className="text-base text-text-primary">Theme</p>
            <p className="text-sm text-text-secondary">Currently {theme} mode</p>
          </div>
          <Button variant="secondary" onClick={toggle}>
            Switch to {theme === 'dark' ? 'Light' : 'Dark'} mode
          </Button>
        </div>
      </Card>

      {/* Pipeline config */}
      <Card>
        <p className="text-lg font-semibold text-text-primary mb-2">Pipeline Parameters</p>
        <MetricControls />
      </Card>

      {/* API connection */}
      <Card>
        <p className="text-lg font-semibold text-text-primary mb-4">API</p>
        <div className="flex items-center justify-between py-3">
          <div>
            <p className="text-base text-text-primary">Backend endpoint</p>
            <p className="text-sm font-mono text-text-secondary">http://localhost:8000/api/v1</p>
          </div>
          <span className="inline-flex items-center gap-1.5 text-xs font-semibold bg-green-muted text-green px-3 py-1 rounded-full">
            <span className="w-1.5 h-1.5 rounded-full bg-green" />
            Configured
          </span>
        </div>
      </Card>
    </div>
  );
}
