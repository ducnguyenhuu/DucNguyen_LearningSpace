/**
 * DocumentDetail — placeholder implemented in Phase 5 (document summary).
 */
import { useParams } from 'react-router-dom';

export default function DocumentDetail() {
  const { documentId } = useParams<{ documentId: string }>();
  return (
    <div className="page page--document-detail">
      <h1>Document Detail</h1>
      <p>Document ID: {documentId}</p>
    </div>
  );
}
