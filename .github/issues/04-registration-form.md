Summary
- Improve registration to support additional fields (e.g., name, grade) and basic per-activity quotas.

Rationale
- Approach Indico’s flexible registration forms and quota management.

Scope
- Extend signup payload to include registrant fields; validate required fields.
- Per-activity settings for required fields and capacity.

Acceptance Criteria
- Organizer can configure required fields.
- API validates and stores extra fields with signup; `/activities` shows counts.

Tasks
- Extend DB schema for signup details.
- Add config fields to `Activity` for required fields.
- Update API and UI accordingly.