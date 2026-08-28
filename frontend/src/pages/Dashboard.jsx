import { useEffect, useState } from "react";
import {
  Activity,
  Brain,
  FileText,
  Plus,
  Search,
  Settings,
} from "lucide-react";
import { Link } from "react-router-dom";

const API_URL = "http://127.0.0.1:8000";

function Dashboard() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRuns() {
      try {
        const response = await fetch(
          `${API_URL}/research`
        );

        if (!response.ok) {
          throw new Error(
            "Failed to load research runs."
          );
        }

        const data = await response.json();

        const runIds = data.runs || [];

        const details = await Promise.all(
          runIds.map(async (id) => {
            try {
              const runResponse = await fetch(
                `${API_URL}/research/${id}`
              );

              if (!runResponse.ok) {
                return null;
              }

              const run =
                await runResponse.json();

              return {
                ...run,
                id,
              };
            } catch {
              return null;
            }
          })
        );

        setRuns(
          details.filter(
            (run) => run !== null
          )
        );
      } catch (error) {
        console.error(
          "Failed to load research:",
          error
        );
      } finally {
        setLoading(false);
      }
    }

    loadRuns();
  }, []);

  // ---------------------------------------------------------
  // Dashboard metrics
  // ---------------------------------------------------------

  const totalRuns = runs.length;

  const totalSources = runs.reduce(
    (total, run) =>
      total +
      (run.sources?.length || 0),
    0
  );

  const totalClaims = runs.reduce(
    (total, run) =>
      total +
      (run.analyses || []).reduce(
        (count, analysis) =>
          count +
          (analysis.claims?.length || 0),
        0
      ),
    0
  );

  const confidenceValues = runs
    .map(
      (run) =>
        run.critique
          ?.overall_confidence
    )
    .filter(
      (value) =>
        typeof value === "number"
    );

  const averageConfidence =
    confidenceValues.length > 0
      ? Math.round(
          (confidenceValues.reduce(
            (sum, value) =>
              sum + value,
            0
          ) /
            confidenceValues.length) *
            100
        )
      : null;

  return (
    <div className="flex min-h-screen bg-zinc-950 text-zinc-100">
      {/* Sidebar */}

      <aside className="hidden w-64 border-r border-zinc-800 bg-zinc-950 md:flex md:flex-col">
        <div className="flex h-16 items-center gap-3 border-b border-zinc-800 px-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-black">
            <Brain size={18} />
          </div>

          <div>
            <h1 className="font-semibold tracking-tight">
              AXIOM
            </h1>

            <p className="text-[10px] uppercase tracking-widest text-zinc-500">
              Research System
            </p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 p-3">
          <NavItem
            icon={<Activity size={17} />}
            label="Overview"
            active
          />

          <Link to="/research/new">
            <NavItem
              icon={<Plus size={17} />}
              label="New Research"
            />
          </Link>

        </nav>

        <div className="border-t border-zinc-800 p-3">
          <NavItem
            icon={<Settings size={17} />}
            label="Settings"
          />
        </div>
      </aside>

      {/* Main */}

      <main className="flex-1">
        <header className="flex h-16 items-center justify-between border-b border-zinc-800 px-6">
          <div>
            <h2 className="text-lg font-semibold">
              Research Overview
            </h2>

            <p className="text-sm text-zinc-500">
              Monitor your autonomous research runs.
            </p>
          </div>

          <Link
            to="/research/new"
            className="flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-black transition hover:bg-zinc-200"
          >
            <Plus size={16} />
            New Research
          </Link>
        </header>

        <div className="mx-auto max-w-7xl space-y-8 p-6">

          {/* Stats */}

          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard
              label="Research Runs"
              value={totalRuns}
              description="Total research runs"
            />

            <StatCard
              label="Sources"
              value={totalSources}
              description="Sources analyzed"
            />

            <StatCard
              label="Claims"
              value={totalClaims}
              description="Claims extracted"
            />

            <StatCard
              label="Avg. Confidence"
              value={
                averageConfidence !== null
                  ? `${averageConfidence}%`
                  : "—"
              }
              description="Across research runs"
            />
          </section>

          {/* Recent Research */}

          <section className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h3 className="font-semibold">
                  Recent Research
                </h3>

                <p className="mt-1 text-sm text-zinc-500">
                  Your latest research investigations.
                </p>
              </div>

              <Search
                size={18}
                className="text-zinc-500"
              />
            </div>

            {loading ? (
              <p className="text-sm text-zinc-600">
                Loading research...
              </p>
            ) : runs.length === 0 ? (
              <div className="rounded-lg border border-dashed border-zinc-800 p-10 text-center">
                <p className="text-sm text-zinc-500">
                  No research runs yet.
                </p>

                <Link
                  to="/research/new"
                  className="mt-4 inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-black"
                >
                  <Plus size={15} />
                  Start your first research
                </Link>
              </div>
            ) : (
              <div className="space-y-2">
                {runs
                  .slice(0, 5)
                  .map((run) => (
                    <Link
                      key={run.id}
                      to={`/research/${run.id}`}
                      className="block"
                    >
                      <ResearchRow
                        question={
                          run.plan?.question ||
                          "Untitled research"
                        }
                        status={
                          run.critique
                            ?.sufficient
                            ? "Completed"
                            : "Research"
                        }
                        sources={`${
                          run.sources
                            ?.length || 0
                        } sources`}
                        confidence={
                          run.critique
                            ?.overall_confidence
                            ? `${Math.round(
                                run
                                  .critique
                                  .overall_confidence *
                                  100
                              )}%`
                            : "—"
                        }
                      />
                    </Link>
                  ))}
              </div>
            )}
          </section>

          {/* Pipeline */}

          <section className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5">
            <div className="mb-6">
              <h3 className="font-semibold">
                Research Pipeline
              </h3>

              <p className="mt-1 text-sm text-zinc-500">
                How Axiom transforms a research
                question into evidence-backed
                conclusions.
              </p>
            </div>

            <div className="grid gap-3 md:grid-cols-4 lg:grid-cols-8">
              {[
                "Question",
                "Planning",
                "Search",
                "Evidence",
                "Claims",
                "Relationships",
                "Critique",
                "Report",
              ].map(
                (step, index) => (
                  <div
                    key={step}
                    className="rounded-lg border border-zinc-800 bg-zinc-950 p-4"
                  >
                    <span className="text-xs text-zinc-600">
                      {String(
                        index + 1
                      ).padStart(2, "0")}
                    </span>

                    <p className="mt-2 text-sm font-medium">
                      {step}
                    </p>
                  </div>
                )
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

function NavItem({
  icon,
  label,
  active = false,
}) {
  return (
    <div
      className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition ${
        active
          ? "bg-zinc-800 text-white"
          : "text-zinc-500 hover:bg-zinc-900 hover:text-zinc-200"
      }`}
    >
      {icon}
      {label}
    </div>
  );
}

function StatCard({
  label,
  value,
  description,
}) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5">
      <p className="text-sm text-zinc-500">
        {label}
      </p>

      <p className="mt-2 text-3xl font-semibold tracking-tight">
        {value}
      </p>

      <p className="mt-1 text-xs text-zinc-600">
        {description}
      </p>
    </div>
  );
}

function ResearchRow({
  question,
  status,
  sources,
  confidence,
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-zinc-800 bg-zinc-950 p-4 transition hover:border-zinc-700">
      <div className="min-w-0">
        <p className="truncate text-sm font-medium">
          {question}
        </p>

        <p className="mt-1 text-xs text-zinc-600">
          {sources}
        </p>
      </div>

      <div className="ml-4 flex shrink-0 items-center gap-4">
        <span className="hidden text-sm font-medium sm:block">
          {confidence}
        </span>

        <span className="rounded-full border border-zinc-700 px-2.5 py-1 text-xs text-zinc-400">
          {status}
        </span>
      </div>
    </div>
  );
}

export default Dashboard;