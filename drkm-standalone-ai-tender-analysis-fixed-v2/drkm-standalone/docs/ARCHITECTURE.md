# Architecture and security notes

## Request path
Browser -> React/Nginx -> FastAPI -> PostgreSQL / Redis / Ollama.
Uploads are written to the persistent documents volume and indexed asynchronously by Celery.
The worker extracts content, creates chunks, requests local embeddings and stores vectors in pgvector.
Search embeds the query and retrieves nearest chunks. Chat places retrieved passages into a constrained
prompt and asks the local LLM to answer with source references.

## Important production work
- Implement user identity through enterprise OIDC/SAML/LDAP and enforce tenant/document ACLs in every query.
- Add malware scanning (e.g. ClamAV) before a file is made available.
- Add PDF OCR fallback for scanned PDFs (render pages with Poppler, then Tesseract/PaddleOCR).
- Add document versioning, legal hold, retention/purge, immutable audit and backup/restore.
- Add pgvector indexes (HNSW/IVFFlat) after choosing dimensions and benchmarking corpus size.
- Add rate limits, upload quotas, model request limits and prompt-injection tests.
- Add model registry/allow-list and offline model artifact management.
- Add evaluation datasets for extraction, retrieval, answer faithfulness and citations.
