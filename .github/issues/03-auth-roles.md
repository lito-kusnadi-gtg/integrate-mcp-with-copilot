Summary
- Add authentication and basic roles: admin, organizer, student.

Rationale
- Enable permissions for managing activities, viewing rosters, and administering the system.

Scope
- Minimal auth (session or JWT) with FastAPI; role field on User.
- Protect admin/organizer endpoints; public read-only endpoints stay open.

Acceptance Criteria
- Users can sign in; role determines access to protected endpoints.
- Admin can create/update/delete activities; students can sign up/unregister.

Tasks
- Add `User` model and password (or OAuth2) flow.
- Add dependency guards to protected endpoints.
- Seed demo users for local development.