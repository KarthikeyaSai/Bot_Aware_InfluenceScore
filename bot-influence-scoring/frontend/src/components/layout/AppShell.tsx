import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function AppShell() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-bg-base">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-[1280px] mx-auto h-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
