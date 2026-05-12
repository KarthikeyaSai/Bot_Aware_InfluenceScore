const BASE = 'http://localhost:8000/api/v1';

export async function postAnalyze(edgeFile: File, nodeFile: File): Promise<{ job_id: string }> {
  const formData = new FormData();
  formData.append('edges', edgeFile);
  formData.append('nodes', nodeFile);
  const res = await fetch(`${BASE}/analyze`, { method: 'POST', body: formData });
  if (!res.ok) throw new Error('Failed to submit analysis job');
  return res.json();
}

export async function getDatasetSummary(dataset: string) {
  const res = await fetch(`${BASE}/datasets/${dataset}/summary`);
  if (!res.ok) throw new Error('Failed to fetch dataset summary');
  return res.json();
}
