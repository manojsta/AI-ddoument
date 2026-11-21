# Tender analysis and API reliability fixes

## Changes included

- Nginx `/api/` proxy now has explicit connection/send/read timeouts, forwarded headers, HTTP/1.1 and buffering disabled for long-running API calls.
- The frontend API client reads response bodies safely and reports HTTP status plus a short sanitized response excerpt when a proxy returns HTML or another non-JSON body.
- Unhandled FastAPI exceptions are returned as JSON error envelopes rather than HTML error pages.
- Ollama embedding/generation calls now report malformed/non-JSON and empty responses as actionable service errors.
- Tender Name is mandatory when uploading tender documents and when requesting tender analysis.
- Tender analysis selects only indexed documents with an exact case-insensitive `metadata_json.tender_name` match. Documents from other tenders are excluded.
- Document metadata supports `tender_name`, `document_role`, `related_document_id`, `annexure_number`, and `corrigendum_number`. Roles are validated; parent-document associations are checked and cannot cross tender boundaries when both documents have a tender assignment.
- A Tender metadata action in the repository allows assigning older documents to a tender and linking annexures/corrigenda to a parent document by UUID.
- Document re-indexing preserves existing tender and association metadata instead of overwriting it. Version snapshots retain metadata; replacement versions retain the current tender association.
- Same-content files can exist independently in different tenders; duplicate detection is scoped to the tender when a Tender Name is provided.
- Analysis response includes the detailed report and a separately extractable compliance checklist. The UI provides separate checklist display/export.
- The UI displays processing stages and reports analysis errors without silently failing.

## Assigning existing documents

The repository's **Tender metadata** action can assign the exact Tender Name and role. For API clients, use:

```http
PATCH /api/v1/documents/{document_id}/metadata
Content-Type: application/json
Authorization: Bearer <token>

{"metadata":{"tender_name":"Tender ABC","document_role":"annexure","related_document_id":"<parent-document-uuid>","annexure_number":"A-1"}}
```

Use `document_role: "corrigendum"` and `corrigendum_number` for corrigenda. The parent UUID is optional for standalone tender documents. All documents to be analyzed must have the same exact Tender Name and be indexed.

## Run

```bash
cp .env.example .env
# Set strong JWT_SECRET_KEY and ADMIN_PASSWORD values in .env
docker compose build --no-cache
docker compose up -d
```

The frontend is served on port 3000. Backend health is available at `/health`.

## Validation status

- Python syntax compilation passed for the active backend modules (`main.py`, `worker.py`, and `services/ai.py`).
- A full frontend production build could not be run in this environment because `npm install` repeatedly timed out while fetching dependencies. Run `npm run build` in the frontend directory or `docker compose build web` in an environment with npm registry access before deployment.
- End-to-end tests require running PostgreSQL/pgvector, Redis, Ollama and the Celery worker; these services were not available in this patch environment.
