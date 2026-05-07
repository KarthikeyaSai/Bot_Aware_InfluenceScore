import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export interface GraphNode extends d3.SimulationNodeDatum {
  id: string;
  botProb: number;
  influenceScore: number;
}

export interface GraphEdge {
  source: string | GraphNode;
  target: string | GraphNode;
  weight: number;
}

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  onNodeClick?: (node: GraphNode) => void;
}

function nodeColor(botProb: number): string {
  if (botProb >= 0.7) return '#f4212e';
  if (botProb <= 0.3) return '#00ba7c';
  return '#ff7043';
}

export function GraphCanvas({ nodes, edges, onNodeClick }: GraphCanvasProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  // Keep onNodeClick in a ref so it never causes the simulation to restart
  const onNodeClickRef = useRef(onNodeClick);
  useEffect(() => { onNodeClickRef.current = onNodeClick; }, [onNodeClick]);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const { width, height } = svgRef.current.getBoundingClientRect();

    const g = svg.append('g');

    // zoom is set up now but its handler is updated after node is created
    // so the handler can access the node selection via closure
    const zoom = d3.zoom<SVGSVGElement, unknown>().scaleExtent([0.1, 8]);
    svg.call(zoom);

    // Copy both nodes and edges — d3 forceLink mutates edge objects in-place
    // (replaces string source/target IDs with node references). Without a copy,
    // those mutations persist into the next effect run and break link resolution.
    const nodesCopy = nodes.map((n) => ({ ...n }));
    const edgesCopy = edges.map((e) => ({ ...e, source: e.source as string, target: e.target as string }));

    const simulation = d3
      .forceSimulation<GraphNode>(nodesCopy)
      .force(
        'link',
        d3
          .forceLink<GraphNode, GraphEdge>(edgesCopy)
          .id((d) => d.id)
          .distance(60),
      )
      .force('charge', d3.forceManyBody<GraphNode>().strength(-120))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = g
      .append('g')
      .selectAll<SVGLineElement, GraphEdge>('line')
      .data(edgesCopy)
      .join('line')
      .attr('stroke', 'var(--graph-edge)')
      .attr('stroke-width', 1)
      .attr('opacity', 0.5);

    const node = g
      .append('g')
      .selectAll<SVGCircleElement, GraphNode>('circle')
      .data(nodesCopy)
      .join('circle')
      .attr('r', (d) => 5 + (d.influenceScore ?? 0) * 12)
      .attr('fill', (d) => nodeColor(d.botProb))
      .attr('cursor', 'pointer')
      .on('click', (_, d) => onNodeClickRef.current?.(d))
      .on('mouseover', function (_, d) {
        const k = d3.zoomTransform(svgRef.current!).k;
        d3.select(this)
          .transition().duration(100)
          .attr('r', (5 + (d.influenceScore ?? 0) * 12) / k * 1.4)
          .style('filter', 'drop-shadow(0 0 8px currentColor)');
      })
      .on('mouseout', function (_, d) {
        const k = d3.zoomTransform(svgRef.current!).k;
        d3.select(this)
          .transition().duration(100)
          .attr('r', (5 + (d.influenceScore ?? 0) * 12) / k)
          .style('filter', 'none');
      })
      .call(
        d3.drag<SVGCircleElement, GraphNode>()
          .on('start', (e, d) => {
            if (!e.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x; d.fy = d.y;
          })
          .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
          .on('end', (e, d) => {
            if (!e.active) simulation.alphaTarget(0);
            d.fx = null; d.fy = null;
          }),
      );

    // Now that node exists, attach the zoom handler with access to it
    zoom.on('zoom', (e) => {
      g.attr('transform', e.transform);
      const k = e.transform.k;
      node.attr('r', (d) => (5 + (d.influenceScore ?? 0) * 12) / k);
    });

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
  }, [nodes, edges]); // onNodeClick intentionally excluded — handled via ref above

  return (
    <svg
      ref={svgRef}
      className="w-full h-full bg-bg-base rounded-lg border border-border"
    />
  );
}
