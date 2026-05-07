import { useState, useCallback } from 'react';
import { Upload } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { MetricControls } from './MetricControls';
import { useJobProgress } from '../hooks/useJobProgress';
import { useAnalysisStore } from '../store/analysisStore';
import { postAnalyze } from '../lib/api';

const PIPELINE_STEPS = [
  { key: 'graph_construction', label: 'Building graph' },
  { key: 'gat_inference',      label: 'Running GAT inference' },
  { key: 'sanitization',       label: 'Sanitizing graph' },
  { key: 'influence_scoring',  label: 'Computing PageRank & HITS' },
  { key: 'ic_simulation',      label: 'IC simulations' },
  { key: 'composite_score',    label: 'Generating composite scores' },
];

export function UploadAnalyze() {
  const [edgeFile, setEdgeFile] = useState<File | null>(null);
  const [nodeFile, setNodeFile] = useState<File | null>(null);
  const [error, setError]       = useState<string | null>(null);

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
    try {
      setError(null);
      const { job_id } = await postAnalyze(edgeFile, nodeFile);
      setJobId(job_id);
    } catch {
      setError('Failed to submit analysis. Is the backend running?');
    }
  };

  const currentStepIdx = PIPELINE_STEPS.findIndex((s) => s.key === progress?.step);
  const pct = progress?.pct_complete ?? 0;

  return (
    <div className="p-6 max-w-2xl mx-auto flex flex-col gap-6">
      <h1 className="text-xl font-semibold text-text-primary">Upload & Analyze</h1>

      {/* Drop zones */}
      {[
        { type: 'edge' as const, file: edgeFile, label: 'Edge List CSV',       hint: 'source, target, type, count, last_date' },
        { type: 'node' as const, file: nodeFile, label: 'Node Features JSON',  hint: '[{id, followers_count, friends_count, …}]' },
      ].map(({ type, file, label, hint }) => (
        <Card
          key={type}
          className={`border-dashed text-center cursor-pointer ${file ? 'border-blue' : ''}`}
          onDragOver={(e: React.DragEvent) => e.preventDefault()}
          onDrop={(e: React.DragEvent) => onDrop(e, type)}
        >
          <Upload size={24} className="mx-auto mb-2 text-text-secondary" />
          <p className="text-base font-semibold text-text-primary">{label}</p>
          <p className="text-sm text-text-secondary mt-1">
            {file ? file.name : `Drag & drop or click — ${hint}`}
          </p>
          {file && (
            <p className="text-xs text-text-disabled mt-1">{(file.size / 1024).toFixed(1)} KB</p>
          )}
        </Card>
      ))}

      {error && <p className="text-sm text-red">{error}</p>}

      {/* Config sliders */}
      <Card>
        <MetricControls />
      </Card>

      <Button onClick={submit} disabled={!!activeJobId && !completed}>
        {activeJobId && !completed ? 'Analyzing…' : 'Run Analysis'}
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
                  ${i < currentStepIdx   ? 'bg-green'   :
                    i === currentStepIdx ? 'bg-blue'    :
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
        <Card className="border-green bg-green-muted/10">
          <p className="text-green font-semibold">Analysis complete. Results are now live in the dashboard.</p>
        </Card>
      )}
    </div>
  );
}
