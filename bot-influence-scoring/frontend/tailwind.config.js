/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: ['attribute', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        bg: {
          base:     'var(--bg-base)',
          surface:  'var(--bg-surface)',
          elevated: 'var(--bg-elevated)',
          overlay:  'var(--bg-overlay)',
        },
        border: {
          DEFAULT: 'var(--border)',
          subtle:  'var(--border-subtle)',
        },
        text: {
          primary:   'var(--text-primary)',
          secondary: 'var(--text-secondary)',
          disabled:  'var(--text-disabled)',
        },
        blue:   { DEFAULT: '#1d9bf0', hover: '#1a8cd8', muted: 'rgba(29,155,240,0.12)', glow: 'rgba(29,155,240,0.20)' },
        red:    { DEFAULT: '#f4212e', muted: 'rgba(244,33,46,0.12)' },
        green:  { DEFAULT: '#00ba7c', muted: 'rgba(0,186,124,0.12)' },
        orange: { DEFAULT: '#ff7043', muted: 'rgba(255,112,67,0.12)' },
        purple: { DEFAULT: '#794bc4' },
        yellow: { DEFAULT: '#ffd400' },
      },
      fontFamily: {
        display: ['"DM Sans"', 'sans-serif'],
        body:    ['"DM Sans"', 'sans-serif'],
        mono:    ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
      },
      fontSize: {
        xs:    ['11px', { lineHeight: '1.4' }],
        sm:    ['13px', { lineHeight: '1.5' }],
        base:  ['15px', { lineHeight: '1.6' }],
        lg:    ['17px', { lineHeight: '1.5' }],
        xl:    ['20px', { lineHeight: '1.3' }],
        '2xl': ['24px', { lineHeight: '1.2' }],
        '3xl': ['32px', { lineHeight: '1.1' }],
        '4xl': ['42px', { lineHeight: '1.0' }],
      },
      borderRadius: {
        sm:   '6px',
        md:   '10px',
        lg:   '16px',
        xl:   '20px',
        full: '9999px',
      },
      transitionDuration: {
        fast:  '100ms',
        base:  '150ms',
        slow:  '250ms',
        xslow: '400ms',
      },
      transitionTimingFunction: {
        snap: 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [],
};
