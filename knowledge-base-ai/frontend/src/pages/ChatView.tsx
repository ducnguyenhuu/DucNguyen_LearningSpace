/**
 * ChatView — placeholder implemented in Phase 4 (T052-T053).
 * Renders a stub so routes resolve without errors.
 */
import { Link } from 'react-router-dom';

export default function ChatView() {
  return (
    <div className="page page--chat">
      <h1>Chat</h1>
      <p>
        The conversational interface will be available here. First,{' '}
        <Link to="/documents">ingest some documents</Link>.
      </p>
    </div>
  );
}
