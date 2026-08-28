import { useState } from "react";
import { ArrowLeft, Brain, Loader2 } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

const API_URL = "http://127.0.0.1:8000";

function NewResearch() {
  const navigate = useNavigate();

  const [topic, setTopic] = useState("");
  const [depth, setDepth] = useState("deep");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    if (!topic.trim()) {
      setError("Enter a research question.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/research`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            topic: topic.trim(),
            depth,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Failed to start research."
        );
      }

      const data = await response.json();

      navigate(
        `/research/${data.run_id}`
      );
    } catch (err) {
      setError(
        err.message ||
          "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <header className="flex h-16 items-center border-b border-zinc-800 px-6">
        <Link
          to="/"
          className="mr-4 text-zinc-500 hover:text-white"
        >
          <ArrowLeft size={18} />
        </Link>

        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-black">
            <Brain size={17} />
          </div>

          <div>
            <h1 className="font-semibold">
              New Research
            </h1>

            <p className="text-xs text-zinc-500">
              Start an autonomous investigation
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-16">
        <div className="mb-10">
          <p className="text-sm font-medium text-zinc-500">
            AXIOM RESEARCH
          </p>

          <h2 className="mt-3 text-4xl font-semibold tracking-tight">
            What do you want to investigate?
          </h2>

          <p className="mt-3 max-w-2xl text-zinc-500">
            Axiom will plan the investigation,
            search sources, extract evidence,
            analyze claims, and critique the
            research before producing a report.
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-6"
        >
          <div>
            <label className="mb-2 block text-sm font-medium">
              Research question
            </label>

            <textarea
              value={topic}
              onChange={(event) =>
                setTopic(event.target.value)
              }
              placeholder="e.g. Does RAG reduce hallucinations in LLMs?"
              rows={6}
              className="w-full resize-none rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 text-sm outline-none transition placeholder:text-zinc-700 focus:border-zinc-600"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">
              Research depth
            </label>

            <select
              value={depth}
              onChange={(event) =>
                setDepth(event.target.value)
              }
              className="rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-3 text-sm outline-none"
            >
              <option value="shallow">
                Shallow
              </option>

              <option value="medium">
                Medium
              </option>

              <option value="deep">
                Deep
              </option>
            </select>
          </div>

          {error && (
            <div className="rounded-lg border border-red-900/50 bg-red-950/20 p-3 text-sm text-red-400">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-medium text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2
                  size={16}
                  className="animate-spin"
                />
                Starting research...
              </>
            ) : (
              "Start Research"
            )}
          </button>
        </form>
      </main>
    </div>
  );
}

export default NewResearch;