import { clsx } from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  clickable?: boolean;
  style?: React.CSSProperties;
  onDragOver?: (e: React.DragEvent) => void;
  onDrop?: (e: React.DragEvent) => void;
}

export function Card({ children, className, clickable, style, onDragOver, onDrop }: CardProps) {
  return (
    <div
      style={style}
      onDragOver={onDragOver}
      onDrop={onDrop}
      className={clsx(
        'bg-bg-surface border border-border rounded-lg p-5',
        '[data-theme="light"]:shadow-[0_1px_8px_rgba(0,0,0,0.06)]',
        clickable && 'cursor-pointer transition-colors duration-base hover:border-blue-muted',
        className,
      )}
    >
      {children}
    </div>
  );
}
