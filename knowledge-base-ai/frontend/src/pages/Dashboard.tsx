/**
 * Dashboard — landing page showing quick links and system status.
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getHealth } from '../services/api';
import type { HealthResponse } from '../services/types';

export default function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : 'Unable to reach backend';
        setError(msg);
      });
  }, []);

  return (
    <div className="page page--dashboard">
      <h1>Knowledge Base AI</h1>
      <p className="subtitle">
        Your local, private document knowledge base powered by local AI models.
      </p>

      <div className="quick-links">
        <Link to="/documents" className="card card--link">
          <h2>Documents</h2>
          <p>Ingest and manage your document library.</p>
        </Link>
        <Link to="/chat" className="card card--link">
          <h2>Chat</h2>
          <p>Ask questions grounded in your documents.</p>
        </Link>
      </div>

      <section className="system-status" aria-label="System status">
        <h2>System Status</h2>
        {error && (
          <p className="status-error" role="alert">
            {error}
          </p>
        )}
        {health && !error && (
          <dl className="status-list">
            <dt>Backend</dt>
            <dd className={health.status === 'ok' ? 'status-ok' : 'status-error'}>
              {health.status}
            </dd>
            <dt>Ollama</dt>
            <dd className={health.ollama === 'ok' ? 'status-ok' : 'status-warn'}>
              {health.ollama}
            </dd>
            <dt>Embedding model</dt>
            <dd>{health.embedding_model}</dd>
            <dt>LLM model</dt>
            <dd>{health.llm_model}</dd>
            {health.reembedding && (
              <>
                <dt>Re-embedding</dt>
                <dd className="status-warn">In progress — search results may vary</dd>
              </>
            )}
          </dl>
        )}
      </section>
    </div>
  );
}
