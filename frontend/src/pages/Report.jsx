import { useEffect, useState } from "react";
import {
  ArrowLeft,
  ExternalLink,
  FileText,
  Loader2,
} from "lucide-react";
import { Link, useParams } from "react-router-dom";
import ReactMarkdown from "react-markdown";

const API_URL = "http://localhost:8000";

function Report() {
  const { runId } = useParams();

  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadReport() {
      try {
        const response = await fetch(
          `${API_URL}/research/${runId}/report`
        );

        if (!response.ok) {
          throw new Error(
            "Unable to load research report."
          );
        }

        const data = await response.json();

        setReport(data.report || "");
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadReport();
  }, [runId]);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">

      {/* Header */}

      <header className="sticky top-0 z-10 flex h-16 items-center border-b border-zinc-800 bg-zinc-950/95 px-6 backdrop-blur">
        <Link
          to={`/research/${runId}`}
          className="mr-4 rounded-lg p-2 text-zinc-500 transition hover:bg-zinc-900 hover:text-white"
        >
          <ArrowLeft size={18} />
        </Link>

        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-black">
            <FileText size={17} />
          </div>

          <div>
            <h1 className="font-semibold">
              Research Report
            </h1>

            <p className="text-xs text-zinc-600">
              {runId}
            </p>
          </div>
        </div>
      </header>

      {/* Report */}

      <main className="mx-auto max-w-4xl px-6 py-10">

        {loading && (
          <div className="flex items-center justify-center py-24 text-zinc-500">
            <Loader2
              size={20}
              className="mr-3 animate-spin"
            />
            Loading report...
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-red-900/50 bg-red-950/20 p-5 text-sm text-red-400">
            {error}
          </div>
        )}

        {!loading && !error && (
          <article className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/30">

            {/* Report header */}

            <div className="border-b border-zinc-800 px-8 py-8 md:px-12">
              <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-widest text-zinc-600">
                <FileText size={13} />
                Axiom Research Report
              </div>

              <h2 className="text-3xl font-semibold tracking-tight">
                Research Findings
              </h2>

              <p className="mt-2 text-sm text-zinc-600">
                Run ID: {runId}
              </p>
            </div>

            {/* Markdown content */}

            <div className="px-8 py-10 md:px-12 md:py-12">

              <div className="report-content">
                <ReactMarkdown
                  components={{
                    h1: ({ children }) => (
                      <h1 className="mb-8 border-b border-zinc-800 pb-5 text-3xl font-bold tracking-tight text-white">
                        {children}
                      </h1>
                    ),

                    h2: ({ children }) => (
                      <h2 className="mb-4 mt-12 border-b border-zinc-800 pb-3 text-xl font-semibold tracking-tight text-white">
                        {children}
                      </h2>
                    ),

                    h3: ({ children }) => (
                      <h3 className="mb-3 mt-8 text-lg font-semibold text-zinc-100">
                        {children}
                      </h3>
                    ),

                    p: ({ children }) => (
                      <p className="mb-5 text-[15px] leading-7 text-zinc-400">
                        {children}
                      </p>
                    ),

                    ul: ({ children }) => (
                      <ul className="mb-6 ml-5 list-disc space-y-3 text-zinc-400">
                        {children}
                      </ul>
                    ),

                    ol: ({ children }) => (
                      <ol className="mb-6 ml-5 list-decimal space-y-3 text-zinc-400">
                        {children}
                      </ol>
                    ),

                    li: ({ children }) => (
                      <li className="pl-2 text-[15px] leading-7">
                        {children}
                      </li>
                    ),

                    strong: ({ children }) => (
                      <strong className="font-semibold text-zinc-200">
                        {children}
                      </strong>
                    ),

                    em: ({ children }) => (
                      <em className="text-zinc-300">
                        {children}
                      </em>
                    ),

                    blockquote: ({ children }) => (
                      <blockquote className="my-6 border-l-2 border-zinc-600 pl-5 text-zinc-500">
                        {children}
                      </blockquote>
                    ),

                    code: ({ children }) => (
                      <code className="rounded bg-zinc-800 px-1.5 py-0.5 font-mono text-sm text-zinc-300">
                        {children}
                      </code>
                    ),

                    a: ({ href, children }) => (
                      <a
                        href={href}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-zinc-200 underline decoration-zinc-700 underline-offset-4 transition hover:decoration-zinc-300"
                      >
                        {children}
                        <ExternalLink size={12} />
                      </a>
                    ),

                    hr: () => (
                      <hr className="my-10 border-zinc-800" />
                    ),
                  }}
                >
                  {report}
                </ReactMarkdown>
              </div>

            </div>

          </article>
        )}

      </main>
    </div>
  );
}

export default Report;