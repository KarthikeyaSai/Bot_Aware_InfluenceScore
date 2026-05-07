export type BadgeVariant = 'bot' | 'genuine' | 'uncertain' | 'neutral';

const styles: Record<BadgeVariant, string> = {
  bot:       'bg-red-muted text-red',
  genuine:   'bg-green-muted text-green',
  uncertain: 'bg-orange-muted text-orange',
  neutral:   'bg-bg-overlay text-text-secondary',
};

export function Badge({ variant, label }: { variant: BadgeVariant; label: string }) {
  return (
    <span
      className={`
        inline-flex items-center px-[10px] py-[3px]
        text-xs font-semibold rounded-full
        ${styles[variant]}
      `}
    >
      {label}
    </span>
  );
}
