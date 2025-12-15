Summary
- Add a minimal room booking system: rooms, availability search, reservations.

Rationale
- Provide basic scheduling/logistics support inspired by Indico’s room booking.

Scope
- Models for Room and Reservation; conflict detection on create.
- Simple availability search by time window and capacity.

Acceptance Criteria
- Organizer can create/cancel reservations without overlaps.
- Public can view a room’s upcoming availability (read-only).

Tasks
- Define models and unique constraints.
- Implement search and reservation endpoints.
- Basic UI table for room availability.