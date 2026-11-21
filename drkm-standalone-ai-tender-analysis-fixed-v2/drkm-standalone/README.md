# IPumpnet AI Knowledge — On-Premises Document Repository & AI Knowledge Platform

An incremental implementation for a self-hosted document repository with local OCR/text extraction,
metadata suggestions, semantic vector retrieval, and RAG chat using Ollama. It is designed
for local development on Windows 11 with Docker Desktop and for adaptation to on-premises Linux.

## Included
- FastAPI REST API and Swagger UI
- React/Vite user interface
- PostgreSQL + pgvector
- Local Ollama LLM and embedding model
- Redis-backed Celery worker for asynchronous indexing
- Local filesystem document storage (persistent Docker volume)
- PDF, DOCX, XLSX, TXT extraction; Tesseract OCR for supported image uploads; scanned-PDF OCR is a documented extension point
- Chunking, embeddings, semantic retrieval, keyword retrieval, RAG answers with source/page metadata
- Basic shared API-key gate, upload validation, SHA-256 duplicate detection, reversible archive and application audit events
- Docker Compose deployment

## Quick start (Windows 11 CMD)
1. Install and start Docker Desktop (Linux containers / WSL2 backend).
2. Extract this ZIP, open **Command Prompt**, and `cd` into the extracted `drkm-standalone` folder.
3. Copy environment template:
   ```cmd
   copy .env.example .env
   ```
4. Start services:
   ```cmd
   docker compose up -d --build
   ```
5. Download local models into Ollama:
   ```cmd
   docker compose exec ollama ollama pull llama3.2:3b
   docker compose exec ollama ollama pull nomic-embed-text
   ```
6. Open:
   - Web UI: http://localhost:3000
   - API docs: http://localhost:8000/docs
   - API health: http://localhost:8000/health

First model download can take several GB and depends on your internet connection. Once downloaded,
inference runs locally. To operate fully offline, pre-load the models before disconnecting.

## Basic workflow
1. Open the UI and upload a PDF, DOCX, XLSX or TXT.
2. Wait for indexing status to become `indexed`.
3. Open AI Search and enter a question, or use Chat to ask a question about the repository.
4. Answers include source document IDs, names and page numbers when available.

## Useful CMD commands
```cmd
docker compose ps
docker compose logs --tail=200
docker compose logs -f api
docker compose down
docker compose up -d
```
Do **not** use `docker compose down -v` unless you intend to delete the database and uploaded files.

## Configuration
Edit `.env` before deployment. Change `DRKM_API_KEY`, database credentials and allowed origins.
For a production deployment, put Nginx or an enterprise ingress with TLS in front of the services,
replace the simple API-key mode with enterprise OIDC/LDAP SSO, enable backups, configure malware
scanning, and perform security, load, recovery and accessibility testing.

## Important limitations
This is a complete runnable **starter implementation**, not a certified production product and not
a claim of compliance with every SRS requirement. It does not yet implement enterprise SSO, granular
document ACL administration, immutable/WORM audit, legal hold workflows, HA, backup orchestration,
or formal SLA testing. The sample API-key protection is intentionally simple. Add authorization
checks to every retrieval path before exposing it to multiple tenants or users.

## API
- `POST /api/v1/documents/upload` — multipart upload
- `GET /api/v1/documents` — list documents and processing states
- `GET /api/v1/documents/{id}` — document detail
- `POST /api/v1/ai/search` — hybrid semantic/keyword search
- `POST /api/v1/ai/chat` — RAG question answering with citations
- `POST /api/v1/documents/{id}/reindex` — enqueue reindex
- `GET /health` — health check

For local development, Swagger UI is at http://localhost:8000/docs.


## Incremental implementation update

See `docs/IMPLEMENTATION-UPDATE.md` for the new endpoints, database compatibility notes and
the requirements that remain outstanding. This update adds multi-file upload, document metadata
editing/filtering, soft archive/restore, downloads, audit-event listing, dashboard counts and
scanned-PDF OCR fallback. It does not implement all 84 requirements in the attached SRS.

**Preserve existing data:** keep the current `.env` file and Docker named volumes. Update the
existing project directory in place. Never use `docker compose down -v` for an upgrade.


## Password reset and document versioning update

- Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL` and `PUBLIC_BASE_URL` in `.env` to enable Forgot Password emails. Reset links are single-use and expire after 30 minutes. Passwords must be at least 12 characters.
- Administrators can reset a user's password from **User Administration**. The API endpoint is `POST /api/v1/admin/users/{user_id}/reset-password`.
- Administrators can upload a replacement version from the repository. The logical document ID is retained; each prior binary is preserved in `document_versions`, and the current version number increments. Same-name uploads by administrators are treated as replacements; users with write privilege can upload new documents but cannot replace existing ones.
- Version history: `GET /api/v1/documents/{document_id}/versions`; download a historical version at `GET /api/v1/documents/{document_id}/versions/{version_number}/download`.
- Permanent deletion is admin-only: `DELETE /api/v1/documents/{document_id}`. It removes the current file, version files, and database record. Legal-hold documents cannot be deleted.

The added tables are created by the existing `Base.metadata.create_all()` startup routine. Back up the database and document volume before deploying. SMTP delivery must be configured and tested in your environment; failed delivery is logged server-side and the API intentionally does not reveal whether an email address is registered.


## AI Tender Analysis & Compliance Assistant

The application includes an **AI Tender Analysis & Compliance Assistant** tab. Upload all tender volumes, corrigenda and annexures in the Documents tab and wait until each file is indexed. The analysis action processes every indexed document and every indexed text chunk available to the signed-in account, in source batches, then synthesizes a detailed report covering:

- Eligibility: technical criteria, turnover, similar experience, certifications and registrations.
- Commercial terms: EMD, tender fees, performance security, payment, retention and penalties.
- Technical scope: specifications, quality, inspection, testing and acceptance.
- Bid submission: mandatory documents, declarations, forms, annexures and bid formats.
- Important dates and bid validity.
- Risks, rejection/disqualification, LD, warranty, termination and deviations.
- A final compliance checklist with requirement, clause, page, action, suggested responsible department and compliance status.

The report cites source filenames and page numbers where available, identifies missing/unclear information, and defaults checklist status to **Pending verification**. The report can be exported as Markdown. Backend endpoint: `POST /api/v1/ai/tender-analysis` (authenticated read access). The feature uses the configured local Ollama model and requires indexed document text. It is an AI-assisted review, not a substitute for legal/procurement validation.
