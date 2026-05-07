type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';

const variantStyles: Record<ButtonVariant, string> = {
  primary:   'bg-blue text-white hover:bg-blue-hover focus:shadow-[0_0_0_3px_var(--blue-glow)]',
  secondary: 'bg-transparent text-text-primary border border-border hover:bg-bg-elevated',
  ghost:     'bg-transparent text-blue hover:bg-blue-muted',
  danger:    'bg-red-muted text-red border border-red/30 hover:bg-red/20',
};

export function Button({
  variant = 'primary',
  children,
  disabled,
  onClick,
  className,
  type = 'button',
}: {
  variant?: ButtonVariant;
  children: React.ReactNode;
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        text-sm font-semibold px-5 py-[10px] rounded-md
        transition-all duration-base
        active:scale-[0.97]
        disabled:opacity-40 disabled:cursor-not-allowed
        ${variantStyles[variant]}
        ${className ?? ''}
      `}
    >
      {children}
    </button>
  );
}
