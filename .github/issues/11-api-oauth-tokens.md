Summary
- Expose a public HTTP API for activities, signups, and program with token-based auth.

Rationale
- Enable integrations and automation similar to Indico’s HTTP Export API and OAuth.

Scope
- Issue per-user API tokens with scopes; protect write endpoints by scope.
- Document endpoints (OpenAPI) and usage examples.

Acceptance Criteria
- API tokens can be created/revoked by admins.
- API docs include endpoints and scope requirements; tokens work on protected routes.

Tasks
- Add token model and middleware.
- Add scopes and guard endpoints.
- Expand FastAPI docs and examples.