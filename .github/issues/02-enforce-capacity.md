Summary
- Enforce `max_participants` during signup and provide clear error messages and UI feedback.

Rationale
- Prevent oversubscription and align with Indico-style quota enforcement.

Scope
- Server-side capacity checks; return 400 when full.
- Optional waitlist flag in DB (future-proof for notifications).

Acceptance Criteria
- When capacity reached, signup returns error and UI shows message.
- Concurrency-safe (transaction-level) enforcement.

Tasks
- Add unique constraint on (activity_id, email).
- Add capacity check and transactional insert.
- Update frontend to surface errors consistently.