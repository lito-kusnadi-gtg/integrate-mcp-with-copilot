## Summary
- Add persistent storage using a database (SQLite for dev, PostgreSQL for prod) with models for `Activity`, `Participant`, and `Signup`.

## Rationale
- Move from in-memory data to durable, multi-user safe storage and enable future features (auth, quotas, auditing).

## Scope
- ORM setup (SQLModel or SQLAlchemy) and migrations (Alembic).
- Replace in-memory `activities` with DB-backed CRUD.
- Seed initial demo data.

## Acceptance Criteria
- Server restarts do not lose activities or signups.
- `/activities` reads from DB; signup/unregister mutate DB.
- Alembic migrations exist and run successfully.

## Tasks
- Choose ORM and add dependencies.
- Define models and relationships.
- Add Alembic and initial migration.
- Replace handlers in `src/app.py` to use DB session.
- Add simple seed script.