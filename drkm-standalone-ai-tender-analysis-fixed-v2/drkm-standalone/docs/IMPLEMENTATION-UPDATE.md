# IPumpnet AI Knowledge — implementation update

This update extends the existing starter project. It does not reset or migrate existing document rows,
existing vector rows, or the named Docker volumes.

## Added in this update

- Multi-file upload endpoint: `POST /api/v1/documents/bulk-upload`.
- Metadata editing for document type, vendor, project, station, asset, equipment, version,
  document/expiry dates, confidentiality, source, uploader, tags, description, retention date and legal hold.
- Repository filtering by filename, status, document type, vendor and asset, with pagination.
- Soft archive and restore endpoints. Archive hides a record from the normal list; it does not delete
  its file or database row. A document marked `legal_hold` cannot be archived.
- Authenticated document download endpoint.
- Application audit-event table and audit API for upload, duplicate detection, metadata updates,
  archive/restore, download, reindex, search and AI chat events.
- Dashboard summary of document statuses and indexed chunk count.
- Semantic search similarity scores and metadata filters.
- OCR fallback for scanned PDF pages where regular PDF text extraction returns no text.
- Frontend controls for bulk upload, filename filtering, archive, dashboard and recent audit events.

## API additions

- `POST /api/v1/documents/bulk-upload` — upload multiple files.
- `PATCH /api/v1/documents/{id}/metadata` — update supported metadata keys.
- `POST /api/v1/documents/{id}/archive` — reversible soft archive.
- `POST /api/v1/documents/{id}/restore` — restore an archived document.
- `GET /api/v1/documents/{id}/download` — download the original file.
- `GET /api/v1/audit` — list recent application audit events.
- `GET /api/v1/dashboard/summary` — repository counts.
- `GET /api/v1/documents` — now supports `q`, `status`, `document_type`, `vendor`, `asset`,
  `include_archived`, `limit` and `offset`.
- `POST /api/v1/ai/search` — now supports `document_type`, `vendor` and `asset` filters and returns
  a cosine similarity score.

## Database compatibility and safety

The existing `documents` and `document_chunks` tables are unchanged. The application startup's
existing `Base.metadata.create_all()` call creates the new `audit_events` table if it is absent;
it does not drop existing tables or rows. Existing JSONB document metadata is reused.

Keep your existing `.env` file and the Docker named volumes. Do not run `docker compose down -v`.
Back up the database and document volume before applying any production update.

## Requirements still needing work or formal verification

This is an incremental implementation, not completion of all 84 SRS requirements.

- Production identity: OIDC/SSO, user accounts, per-user and per-document RBAC.
- Malware scanning and quarantine.
- Full mandatory metadata validation and configurable taxonomy/auto-classification.
- Structured extraction of asset/equipment/spares/warranty/SLA/calibration obligations, schema governance,
  confidence scoring and human validation workflow.
- Exact/near-duplicate version linking and full document version comparison/check-in/check-out.
- Retention schedules, legal-hold administration and approved secure purge. Current archive is reversible
  and deliberately does not physically delete files.
- Immutable/tamper-evident audit storage. Current audit events are append-only through the application
  but are not protected against database administrators or direct database modification.
- Encryption at rest/in transit, TLS termination, key management and security review.
- Email/SMS alerts, workflow engine, CAD/DWG viewer, enterprise integrations and KPI/report exports.
- Object/blob storage, tenant quotas, horizontal scaling, HA, backup orchestration, measured RPO/RTO,
  SLA/load testing and WCAG 2.1 AA verification.
- Search latency and OCR/extraction accuracy targets need benchmark datasets and test runs.

## Deployment note

The ZIP deliberately excludes the uploaded `.env` file. Keep the `.env` from your current installation.
The application API uses a shared API key and should remain on a trusted local network until enterprise
authentication and authorization are implemented.


## Authentication and RBAC update

The project now includes individual JWT authentication, Argon2 password hashing, an administrator-seeded first account, admin-only user creation/listing, and Read/Write privilege checks. See `AUTHENTICATION-RBAC.md`. Configure `JWT_SECRET_KEY` and `ADMIN_PASSWORD` in `.env` before starting the updated stack. Existing document data is preserved; startup creates the additional `users` table.


## Password and version-control enhancement

- Added single-use, 30-minute password reset tokens stored as SHA-256 hashes, reset email delivery over configured SMTP, and admin-initiated password resets.
- Added `document_versions` history preserving prior binaries, version metadata, upload timestamps and uploader identity.
- Admin replacement keeps the stable document ID and increments `version_number`; prior versions remain downloadable.
- Added admin-only permanent document deletion (blocked by legal hold), including all stored historical binaries.
- Added UI controls for Forgot Password, admin password reset, version upload, version history and deletion.

Configure SMTP settings from `.env.example` before relying on Forgot Password. The API returns a generic response to prevent account enumeration.
