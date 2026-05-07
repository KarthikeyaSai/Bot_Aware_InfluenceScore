import { useState } from 'react';
import { BarChart2, Network, ArrowLeftRight, Upload, Settings, Sun, Moon } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { useTheme } from '../../hooks/useTheme';

const navItems = [
  { icon: Network,        label: 'Graph Explorer',   to: '/'         },
  { icon: BarChart2,      label: 'Leaderboard',      to: '/rankings' },
  { icon: ArrowLeftRight, label: 'Before / After',   to: '/compare'  },
  { icon: Upload,         label: 'Upload & Analyze', to: '/upload'   },
  { icon: Settings,       label: 'Settings',         to: '/settings' },
];

function ThemeToggle({ compact }: { compact: boolean }) {
  const { theme, toggle } = useTheme();
  return (
    <button
      onClick={toggle}
      className="
        flex items-center gap-3 h-11 px-3 rounded-full w-full
        text-text-secondary hover:bg-bg-elevated hover:text-text-primary
        transition-colors duration-fast
      "
    >
      {theme === 'dark'
        ? <Sun size={20} className="shrink-0" />
        : <Moon size={20} className="shrink-0" />}
      {!compact && (
        <span className="whitespace-nowrap text-[15px]">
          {theme === 'dark' ? 'Light mode' : 'Dark mode'}
        </span>
      )}
    </button>
  );
}

export function Sidebar() {
  const [expanded, setExpanded] = useState(false);

  return (
    <nav
      onMouseEnter={() => setExpanded(true)}
      onMouseLeave={() => setExpanded(false)}
      style={{ width: expanded ? 240 : 72 }}
      className="
        h-screen flex flex-col bg-bg-surface border-r border-border
        transition-[width] duration-[200ms] ease-out overflow-hidden shrink-0 z-10
      "
    >
      {/* Logo */}
      <div className="h-16 flex items-center px-4">
        <Network size={28} className="text-blue shrink-0" />
        {expanded && (
          <span className="ml-3 font-bold text-lg text-text-primary whitespace-nowrap">
            BotScope
          </span>
        )}
      </div>

      {/* Nav items */}
      <div className="flex flex-col gap-1 px-2 mt-2 flex-1">
        {navItems.map(({ icon: Icon, label, to }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `
              flex items-center h-11 px-3 rounded-full gap-3
              font-medium transition-colors duration-fast
              ${isActive
                ? 'text-blue bg-blue-muted'
                : 'text-text-secondary hover:bg-bg-elevated hover:text-text-primary'}
            `}
          >
            <Icon size={20} className="shrink-0" />
            {expanded && (
              <span className="whitespace-nowrap text-[15px]">{label}</span>
            )}
          </NavLink>
        ))}
      </div>

      {/* Theme toggle */}
      <div className="p-3 border-t border-border">
        <ThemeToggle compact={!expanded} />
      </div>
    </nav>
  );
}
