# API examples

All `/api/v1` endpoints require the `X-API-Key` header.

## List documents with filters

```bash
curl -H "X-API-Key: YOUR_KEY" "http://localhost:8000/api/v1/documents?q=pump&status=indexed&limit=50"
```

## Update document metadata

```bash
curl -X PATCH "http://localhost:8000/api/v1/documents/DOCUMENT_UUID/metadata" \
  -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"metadata":{"document_type":"Manual","vendor":"IPumpnet","asset":"IPN-150","confidentiality":"Internal"}}'
```

## Archive and restore (no permanent deletion)

```bash
curl -X POST -H "X-API-Key: YOUR_KEY" "http://localhost:8000/api/v1/documents/DOCUMENT_UUID/archive"
curl -X POST -H "X-API-Key: YOUR_KEY" "http://localhost:8000/api/v1/documents/DOCUMENT_UUID/restore"
```

## Dashboard and audit

```bash
curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/api/v1/dashboard/summary
curl -H "X-API-Key: YOUR_KEY" "http://localhost:8000/api/v1/audit?limit=50"
```

Existing endpoints remain available: upload, document list/detail, reindex, AI search, AI chat,
AI status and health.
