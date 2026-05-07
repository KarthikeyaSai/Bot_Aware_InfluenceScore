interface SkeletonCardProps {
  height?: string;
  className?: string;
}

export function SkeletonCard({ height = 'h-32', className = '' }: SkeletonCardProps) {
  return (
    <div className={`skeleton rounded-lg ${height} ${className}`} />
  );
}
