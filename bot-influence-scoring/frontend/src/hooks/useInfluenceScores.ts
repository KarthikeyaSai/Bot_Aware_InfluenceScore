import { useQuery } from '@tanstack/react-query';
import type { GraphEdge, GraphNode } from '../components/charts/GraphCanvas';

const BASE = 'http://localhost:8000/api/v1';
const DATASET = 'cresci-2017';

interface ScoresResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export function useInfluenceScores({ sanitized, topK }: { sanitized: boolean; topK: number }) {
  const query = useQuery<ScoresResponse>({
    queryKey: ['scores', sanitized, topK],
    queryFn: async () => {
      const graph = sanitized ? 'sanitized' : 'raw';
      const res = await fetch(`${BASE}/scores/graph?top_k=${topK}&graph_type=${graph}&dataset=${DATASET}`);
      if (!res.ok) throw new Error('Failed to fetch scores');
      return res.json();
    },
  });

  return {
    nodes: query.data?.nodes ?? [],
    edges: query.data?.edges ?? [],
    isLoading: query.isLoading,
    error: query.error,
  };
}

export interface NodeDetail {
  id: string;
  botProb: number;
  featureBreakdown: { feature: string; value: string }[];
  suspiciousNeighbors: { id: string; botProb: number }[];
}

export function useNodeDetail(nodeId: string) {
  const query = useQuery<NodeDetail>({
    queryKey: ['node', nodeId],
    queryFn: async () => {
      const res = await fetch(`${BASE}/nodes/${nodeId}/bot-probability`);
      if (!res.ok) throw new Error('Failed to fetch node detail');
      return res.json();
    },
    enabled: !!nodeId,
  });

  return {
    node: query.data,
    isLoading: query.isLoading,
    error: query.error,
  };
}

export interface InfluencerRow {
  rank: number;
  nodeId: string;
  compositeScore: number;
  pagerank: number;
  authority: number;
  icReach: number;
  botProb: number;
  rankShift: number;
}

export function useLeaderboard({ sanitized }: { sanitized: boolean }) {
  return useQuery<InfluencerRow[]>({
    queryKey: ['leaderboard', sanitized],
    queryFn: async () => {
      const graph = sanitized ? 'sanitized' : 'raw';
      const res = await fetch(`${BASE}/scores/leaderboard?top_k=500&graph_type=${graph}&dataset=${DATASET}`);
      if (!res.ok) throw new Error('Failed to fetch leaderboard');
      const data = await res.json();
      return data.rows ?? [];
    },
  });
}

export interface ComparisonData {
  rankDisplacement: {
    pctTopKDisplaced: number;
    meanDisplacement: number;
    kendallsTau: number;
    spearmanR: number;
  };
  rawTop20:   { nodeId: string; score: number }[];
  cleanTop20: { nodeId: string; score: number }[];
}

export function useRankingComparison() {
  return useQuery<ComparisonData>({
    queryKey: ['comparison'],
    queryFn: async () => {
      const res = await fetch(`${BASE}/comparison/${DATASET}`);
      if (!res.ok) throw new Error('Failed to fetch comparison');
      return res.json();
    },
  });
}

