import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { GraphExplorer } from './views/GraphExplorer';
import { Leaderboard } from './views/Leaderboard';
import { RankingComparison } from './views/RankingComparison';
import { UploadAnalyze } from './views/UploadAnalyze';
import { Settings } from './views/Settings';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/"         element={<GraphExplorer />} />
          <Route path="/rankings" element={<Leaderboard />} />
          <Route path="/compare"  element={<RankingComparison />} />
          <Route path="/upload"   element={<UploadAnalyze />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
