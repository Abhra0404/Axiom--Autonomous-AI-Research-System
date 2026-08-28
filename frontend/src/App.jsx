import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import NewResearch from "./pages/NewResearch";
import ResearchRun from "./pages/ResearchRun";
import Report from "./pages/Report";

function App() {
  return (
    <BrowserRouter>
      <Routes>

        <Route
          path="/"
          element={<Dashboard />}
        />

        <Route
          path="/research/new"
          element={<NewResearch />}
        />

        <Route
          path="/research/:runId"
          element={<ResearchRun />}
        />

        <Route
          path="/research/:runId/report"
          element={<Report />}
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;