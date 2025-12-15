Summary
- Introduce a minimal program/timetable model: sessions, tracks, and contributions.

Rationale
- Start toward Indico’s scheduling by modeling program items and timeslots.

Scope
- Models for Session, Track, Contribution with start/end times and room reference.
- List program for an activity; no drag-and-drop UI yet.

Acceptance Criteria
- Organizer can create sessions and contributions under an activity.
- Public API returns a structured program for display.

Tasks
- Add models and CRUD endpoints.
- Extend UI to render a simple timetable view.