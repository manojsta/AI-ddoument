# Authentication and Read/Write authorization

## Data model
`users` contains a UUID, unique username/email, Argon2 password hash, `privilege` (`read` or `write`), `is_admin`, `is_active`, and creation timestamp. User rows are in PostgreSQL. Password plaintext is never persisted.

## Request flow
1. `POST /api/v1/auth/login` verifies the supplied username/email and password, then returns a signed JWT.
2. React stores the access token and sends it in the Authorization Bearer header.
3. `get_current_user` validates signature/expiry and loads an active user from the database.
4. `require_read`, `require_write`, and `require_admin` enforce the authorization policy on the API. Frontend upload controls are also hidden for Read accounts, but frontend visibility is not treated as security.

## Initial admin
Set `JWT_SECRET_KEY` (unique random string, >=32 chars) and `ADMIN_PASSWORD` (>=12 chars) in `.env` before first startup. Startup seeds an administrator only if no admin exists. Subsequent startup does not reset passwords or overwrite accounts.

## Endpoints
- `POST /api/v1/auth/login` — public login
- `GET /api/v1/auth/me` — current identity
- `POST /api/v1/admin/users` — admin only; creates Read/Write or admin account
- `GET /api/v1/admin/users` — admin only
- Document listing, detail, download, AI search/chat — authenticated Read or Write
- Upload, bulk upload, metadata update, archive/restore, reindex — Write or Admin

## Deployment
Keep existing PostgreSQL and documents volumes. `Base.metadata.create_all()` adds the users table without dropping existing document data. Back up before upgrading. Never use `docker compose down -v` for an in-place upgrade. Rotate secrets securely and use TLS in production.

## Mandatory first login and security-question recovery

New users created by an administrator are marked `must_change_password=true`
and `security_setup_complete=false`. The first successful login returns only a
15-minute `first_login_setup` bearer token. It does not return a normal API
access token. The user must set a new password and choose three distinct
questions from the predefined list before a normal access token is issued.

Answers are trimmed, case-folded, and whitespace-normalized, then hashed using
`pwdlib`'s recommended Argon2id password hasher. Each answer receives a unique
random salt; plaintext answers are never persisted. Only the selected question
keys and answer hashes are stored in `security_answers`.

Forgot Password accepts a username or email, returns the exact three prompts
saved for that account, and verifies all three answers. Only a complete match
creates a random, one-time reset token stored as a SHA-256 digest with a
five-minute expiry. The token is consumed on successful password reset. A
wrong answer does not issue a reset token. Admin-initiated password resets
invalidate pending reset tokens, clear old security-answer hashes, and force
the user through first-login setup again.

The API uses `Base.metadata.create_all` for the new `security_answers` table
and applies backward-compatible PostgreSQL column additions at startup:

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS security_setup_complete BOOLEAN NOT NULL DEFAULT TRUE;
```

Existing accounts are grandfathered to preserve existing access. Newly created
accounts and the bootstrap administrator are explicitly marked for first-login
setup. Ensure `JWT_SECRET_KEY` is a strong random secret of at least 32
characters and keep the database and backup files protected.
