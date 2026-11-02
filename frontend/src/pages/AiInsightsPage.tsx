import { useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { ErrorState } from "../components/ErrorState";
import { EvidenceSummary } from "../components/EvidenceSummary";
import { LoadingState } from "../components/LoadingState";
import type { AIInsightsResponse } from "../types/api";

const SUGGESTIONS = [
  "Better at this venue?",
  "More consistent recently?",
  "Batting or chasing ground?",
];

function displayAnswer(result: AIInsightsResponse): string {
  if (result.status === "unavailable") {
    return "AI is off. Add your Gemini key in backend/.env (GEMINI_API_KEY), restart the API, then ask again.";
  }
  if (result.status === "error") {
    return result.notes[0] ?? "AI request failed. See backend logs or try again.";
  }
  return result.answer;
}

export function AiInsightsPage() {
  const { matchId = "" } = useParams();
  const [searchParams] = useSearchParams();
  const playerA = searchParams.get("a") ?? undefined;
  const playerB = searchParams.get("b") ?? undefined;

  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AIInsightsResponse | null>(null);
  const [showEvidence, setShowEvidence] = useState(false);
  const [showRawJson, setShowRawJson] = useState(false);

  async function submit(q: string) {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    setShowEvidence(false);
    setShowRawJson(false);
    try {
      const res = await api.aiInsights({
        question: q.trim(),
        match_id: matchId,
        player_a_id: playerA,
        player_b_id: playerB,
      });
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <h1 className="page-title">AI insights</h1>

      <div className="flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => {
              setQuestion(s);
              void submit(s);
            }}
            className="btn-ghost text-xs"
          >
            {s}
          </button>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          void submit(question);
        }}
        className="space-y-3"
      >
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={3}
          maxLength={500}
          placeholder="Your question"
          className="input-field"
        />
        <button type="submit" disabled={loading || !question.trim()} className="btn-primary">
          {loading ? "…" : "Ask"}
        </button>
      </form>

      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}

      {result ? (
        <div className="space-y-3">
          <article
            className={`panel p-4 text-sm leading-relaxed ${
              result.status === "ok" ? "text-white/90" : "text-d11-muted"
            }`}
          >
            {displayAnswer(result)}
          </article>
          {result.status === "validation_warning" && result.notes.length ? (
            <p className="text-xs text-yellow-200">{result.notes[0]}</p>
          ) : null}
          <button
            type="button"
            onClick={() => setShowEvidence((v) => !v)}
            className="text-xs font-semibold text-d11-red"
          >
            {showEvidence ? "Hide stats" : "View stats"}
          </button>
          {showEvidence ? (
            <>
              <EvidenceSummary evidence={result.evidence} />
              <button
                type="button"
                onClick={() => setShowRawJson((v) => !v)}
                className="text-xs text-d11-muted hover:text-white"
              >
                {showRawJson ? "Hide JSON" : "Raw JSON"}
              </button>
              {showRawJson ? (
                <pre className="panel max-h-60 overflow-auto p-3 text-xs text-d11-muted">
                  {JSON.stringify(result.evidence, null, 2)}
                </pre>
              ) : null}
            </>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
