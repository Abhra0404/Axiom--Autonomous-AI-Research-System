import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  Check,
  Circle,
  FileText,
  Loader2,
  Search,
  ShieldCheck,
} from "lucide-react";
import { Link, useParams } from "react-router-dom";

const API_URL = "http://localhost:8000";

const stages = [
  "Planning",
  "Searching",
  "Evidence",
  "Claims",
  "Relationships",
  "Critique",
  "Report",
];

function ResearchRun() {
  const { runId } = useParams();

  const [status, setStatus] = useState("queued");
  const [research, setResearch] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let interval;

    async function fetchResearch() {
      try {
        const response = await fetch(
          `${API_URL}/research/${runId}`
        );

        if (!response.ok) {
          throw new Error(
            "Unable to retrieve research."
          );
        }

        const data = await response.json();

        setResearch({
          ...data,
          id: runId,
        });
      } catch (err) {
        setError(err.message);
      }
    }

    async function fetchResearchStatus() {
      try {
        const response = await fetch(
          `${API_URL}/research/${runId}/status`
        );

        if (!response.ok) {
          throw new Error(
            "Unable to retrieve research status."
          );
        }

        const data = await response.json();

        setStatus(data.status);

        if (
          data.status === "completed" ||
          data.status === "failed" ||
          data.status === "max_iterations"
        ) {
          clearInterval(interval);
          await fetchResearch();
        }
      } catch (err) {
        setError(err.message);
      }
    }

    fetchResearchStatus();

    interval = setInterval(
      fetchResearchStatus,
      2000
    );

    return () => {
      clearInterval(interval);
    };
  }, [runId]);

  const isComplete =
    status === "completed" ||
    status === "max_iterations";

  const isFailed = status === "failed";

  const claims =
    research?.analyses?.flatMap(
      (analysis) => analysis.claims || []
    ) || [];

  const evidence =
    research?.analyses?.flatMap(
      (analysis) => analysis.evidence || []
    ) || [];

  const relationships =
    research?.relationships || [];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">

      {/* Header */}

      <header className="flex h-16 items-center border-b border-zinc-800 px-6">
        <Link
          to="/"
          className="mr-4 rounded-lg p-2 text-zinc-500 transition hover:bg-zinc-900 hover:text-white"
        >
          <ArrowLeft size={18} />
        </Link>

        <div>
          <h1 className="font-semibold">
            Research Run
          </h1>

          <p className="text-xs text-zinc-600">
            {runId}
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 p-6">

        {/* Error */}

        {error && (
          <div className="rounded-xl border border-red-900/50 bg-red-950/20 p-4 text-sm text-red-400">
            {error}
          </div>
        )}

        {/* Research Header */}

        <section className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-6">
          <div className="flex flex-col justify-between gap-5 md:flex-row md:items-center">

            <div className="min-w-0">
              <p className="text-xs uppercase tracking-widest text-zinc-600">
                Research Question
              </p>

              <h2 className="mt-2 text-2xl font-semibold tracking-tight">
                {research?.plan?.question ||
                  "Research in progress..."}
              </h2>
            </div>

            <StatusBadge status={status} />

          </div>
        </section>

        {/* Pipeline */}

        <section className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-6">

          <div className="mb-6">
            <h3 className="font-semibold">
              Research Pipeline
            </h3>

            <p className="mt-1 text-sm text-zinc-600">
              Autonomous research progress
            </p>
          </div>

          <div className="grid gap-3 md:grid-cols-4 lg:grid-cols-7">
            {stages.map(
              (stage, index) => (
                <PipelineStage
                  key={stage}
                  label={stage}
                  index={index}
                  complete={isComplete}
                />
              )
            )}
          </div>

        </section>

        {/* Metrics */}

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">

          <Metric
            label="Iterations"
            value={
              research?.iterations ??
              research?.state?.iteration ??
              0
            }
          />

          <Metric
            label="Sources"
            value={
              research?.sources?.length || 0
            }
          />

          <Metric
            label="Claims"
            value={claims.length}
          />

          <Metric
            label="Evidence"
            value={evidence.length}
          />

          <Metric
            label="Confidence"
            value={
              research?.critique
                ?.overall_confidence != null
                ? `${Math.round(
                    research.critique
                      .overall_confidence * 100
                  )}%`
                : "—"
            }
          />

        </section>

        {/* Claims */}

        <CollapsibleSection
          title="Claims"
          description={`${claims.length} claims extracted from the collected evidence.`}
          icon={<ShieldCheck size={18} />}
          count={claims.length}
        >
          {claims.length > 0 ? (
            <div className="max-h-[600px] space-y-3 overflow-y-auto pr-2">
              {claims.map((claim) => (
                <div
                  key={claim.id}
                  className="rounded-lg border border-zinc-800 bg-zinc-950 p-4"
                >
                  <div className="flex justify-between gap-5">

                    <div className="min-w-0">
                      <p className="text-sm leading-6">
                        {claim.statement}
                      </p>

                      <p className="mt-2 text-xs text-zinc-700">
                        Source: {claim.source_id}
                      </p>
                    </div>

                    <span className="shrink-0 text-xs text-zinc-500">
                      {Math.round(
                        claim.confidence * 100
                      )}
                      %
                    </span>

                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState text="No claims available." />
          )}
        </CollapsibleSection>

        {/* Evidence */}

        <CollapsibleSection
          title="Evidence"
          description={`${evidence.length} evidence items extracted.`}
          icon={<Search size={18} />}
          count={evidence.length}
        >
          {evidence.length > 0 ? (
            <div className="max-h-[600px] space-y-3 overflow-y-auto pr-2">
              {evidence.map((item) => (
                <div
                  key={item.id}
                  className="rounded-lg border border-zinc-800 bg-zinc-950 p-4"
                >
                  <p className="text-sm leading-6 text-zinc-300">
                    {item.content}
                  </p>

                  <div className="mt-3 flex flex-wrap gap-4 text-xs text-zinc-600">
                    <span>
                      Claim: {item.claim_id}
                    </span>

                    <span>
                      Source: {item.source_id}
                    </span>

                    <span>
                      Strength: {item.strength}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState text="No evidence available." />
          )}
        </CollapsibleSection>

        {/* Claim Relationships */}

        <CollapsibleSection
          title="Claim Relationships"
          description={`${relationships.length} relationships detected between claims.`}
          icon={<Activity size={18} />}
          count={relationships.length}
        >
          {relationships.length > 0 ? (
            <div className="max-h-[500px] space-y-2 overflow-y-auto pr-2">
              {relationships.map(
                (relationship, index) => (
                  <div
                    key={index}
                    className="flex flex-wrap items-center gap-3 rounded-lg border border-zinc-800 bg-zinc-950 p-4"
                  >
                    <span className="text-xs text-zinc-500">
                      {relationship.claim_a}
                    </span>

                    <span className="rounded-full border border-zinc-800 px-2 py-1 text-[10px] uppercase tracking-wider text-zinc-500">
                      {relationship.relationship}
                    </span>

                    <span className="text-xs text-zinc-500">
                      {relationship.claim_b}
                    </span>

                    <span className="ml-auto text-xs text-zinc-600">
                      {Math.round(
                        relationship.confidence * 100
                      )}
                      %
                    </span>
                  </div>
                )
              )}
            </div>
          ) : (
            <EmptyState text="No relationships detected." />
          )}
        </CollapsibleSection>

        {/* Sources */}

        {/* Sources */}

<section className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-6">

  <div className="mb-5 flex items-center gap-3">
    <Search
      size={18}
      className="text-zinc-400"
    />

    <div>
      <h3 className="font-semibold">
        Sources
      </h3>

      <p className="text-sm text-zinc-600">
        {research?.sources?.length || 0} sources used during research.
      </p>
    </div>
  </div>

  {research?.sources?.length > 0 ? (
    <div className="max-h-[600px] space-y-2 overflow-y-auto pr-2">
      {research.sources.map((source) => (
        <a
          key={source.id}
          href={source.url}
          target="_blank"
          rel="noreferrer"
          className="block rounded-lg border border-zinc-800 bg-zinc-950 p-4 transition hover:border-zinc-700"
        >
          <div className="flex items-start justify-between gap-4">

            <div className="min-w-0">
              <p className="text-sm font-medium">
                {source.title}
              </p>

              <p className="mt-1 truncate text-xs text-zinc-600">
                {source.url}
              </p>
            </div>

            <div className="flex shrink-0 gap-2">
              <span className="rounded-full border border-zinc-800 px-2 py-1 text-[10px] text-zinc-600">
                {source.source_type}
              </span>

              <span className="rounded-full border border-zinc-800 px-2 py-1 text-[10px] text-zinc-600">
                Q{" "}
                {Math.round(
                  (source.quality_score || 0) * 100
                )}
                %
              </span>
            </div>

          </div>
        </a>
      ))}
    </div>
  ) : (
    <EmptyState text="No sources available." />
  )}

</section>

        {/* Critique */}

        {research?.critique && (
          <section className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-6">

            <div className="mb-6 flex items-center gap-3">
              <AlertTriangle
                size={18}
                className="text-zinc-400"
              />

              <div>
                <h3 className="font-semibold">
                  Research Critique
                </h3>

                <p className="text-sm text-zinc-600">
                  Evaluation of the research quality.
                </p>
              </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2">

              <CritiqueList
                title="Strengths"
                items={
                  research.critique
                    .strengths
                }
              />

              <CritiqueList
                title="Weaknesses"
                items={
                  research.critique
                    .weaknesses
                }
              />

              <CritiqueList
                title="Missing Information"
                items={
                  research.critique
                    .missing_information
                }
              />

              <CritiqueList
                title="Follow-up Questions"
                items={
                  research.critique
                    .follow_up_questions
                }
              />

            </div>

          </section>
        )}

        {/* Completion */}

        {isComplete && !isFailed && (
          <section className="flex flex-col justify-between gap-5 rounded-xl border border-zinc-800 bg-zinc-900/40 p-6 md:flex-row md:items-center">

            <div className="flex items-center gap-3">
              <FileText
                size={20}
                className="text-zinc-400"
              />

              <div>
                <h3 className="font-semibold">
                  Research Complete
                </h3>

                <p className="text-sm text-zinc-600">
                  Your research investigation is complete.
                </p>
              </div>
            </div>

            <Link
              to={`/research/${runId}/report`}
              className="rounded-lg bg-white px-4 py-2 text-center text-sm font-medium text-black transition hover:bg-zinc-200"
            >
              View Report
            </Link>

          </section>
        )}

        {/* Failed */}

        {isFailed && (
          <section className="rounded-xl border border-red-900/50 bg-red-950/20 p-6">
            <h3 className="font-semibold text-red-400">
              Research Failed
            </h3>

            <p className="mt-2 text-sm text-red-500/70">
              The research run could not be completed.
            </p>
          </section>
        )}

      </main>
    </div>
  );
}


/* =========================================================
   Collapsible Section
========================================================= */

function CollapsibleSection({
  title,
  description,
  icon,
  count,
  children,
}) {
  const [open, setOpen] = useState(false);

  return (
    <section className="rounded-xl border border-zinc-800 bg-zinc-900/40">

      <button
        type="button"
        onClick={() =>
          setOpen((value) => !value)
        }
        className="flex w-full items-center justify-between gap-4 p-6 text-left transition hover:bg-zinc-900/60"
      >
        <div className="flex min-w-0 items-center gap-3">

          <div className="shrink-0 text-zinc-400">
            {icon}
          </div>

          <div className="min-w-0">

            <div className="flex items-center gap-2">
              <h3 className="font-semibold">
                {title}
              </h3>

              <span className="rounded-full border border-zinc-800 px-2 py-0.5 text-[10px] text-zinc-600">
                {count}
              </span>
            </div>

            <p className="mt-1 text-sm text-zinc-600">
              {description}
            </p>

          </div>

        </div>

        <span className="shrink-0 text-xs text-zinc-500">
          {open ? "Hide" : "Show"}
        </span>

      </button>

      {open && (
        <div className="border-t border-zinc-800 p-6">
          {children}
        </div>
      )}

    </section>
  );
}


/* =========================================================
   Pipeline Stage
========================================================= */

function PipelineStage({
  label,
  index,
  complete,
}) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-4">

      <div className="mb-3">
        {complete ? (
          <Check size={16} />
        ) : (
          <Circle
            size={16}
            className="text-zinc-700"
          />
        )}
      </div>

      <p className="text-xs text-zinc-600">
        {String(index + 1).padStart(2, "0")}
      </p>

      <p className="mt-1 text-sm font-medium">
        {label}
      </p>

    </div>
  );
}


/* =========================================================
   Metric
========================================================= */

function Metric({
  label,
  value,
}) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-5">

      <p className="text-sm text-zinc-600">
        {label}
      </p>

      <p className="mt-2 text-2xl font-semibold">
        {value}
      </p>

    </div>
  );
}


/* =========================================================
   Status Badge
========================================================= */

function StatusBadge({
  status,
}) {
  const running =
    status === "queued" ||
    status === "running";

  if (status === "completed") {
    return (
      <span className="flex w-fit items-center gap-2 rounded-full border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300">
        <Check size={13} />
        Completed
      </span>
    );
  }

  if (status === "failed") {
    return (
      <span className="rounded-full border border-red-900/50 px-3 py-1.5 text-xs text-red-400">
        Failed
      </span>
    );
  }

  if (status === "max_iterations") {
    return (
      <span className="rounded-full border border-yellow-900/50 px-3 py-1.5 text-xs text-yellow-500">
        Max Iterations
      </span>
    );
  }

  return (
    <span className="flex w-fit items-center gap-2 rounded-full border border-zinc-700 px-3 py-1.5 text-xs text-zinc-400">
      {running ? (
        <Loader2
          size={13}
          className="animate-spin"
        />
      ) : (
        <Circle size={13} />
      )}

      {status}
    </span>
  );
}


/* =========================================================
   Critique List
========================================================= */

function CritiqueList({
  title,
  items = [],
}) {
  return (
    <div>

      <h4 className="mb-3 text-sm font-medium">
        {title}
      </h4>

      {items?.length > 0 ? (
        <ul className="space-y-2">

          {items.map(
            (item, index) => (
              <li
                key={index}
                className="text-sm leading-6 text-zinc-500"
              >
                • {item}
              </li>
            )
          )}

        </ul>
      ) : (
        <p className="text-sm text-zinc-700">
          None
        </p>
      )}

    </div>
  );
}


/* =========================================================
   Empty State
========================================================= */

function EmptyState({
  text,
}) {
  return (
    <div className="rounded-lg border border-dashed border-zinc-800 p-8 text-center text-sm text-zinc-700">
      {text}
    </div>
  );
}

export default ResearchRun;

