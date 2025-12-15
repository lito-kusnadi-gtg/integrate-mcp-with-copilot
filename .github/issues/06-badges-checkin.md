Summary
- Generate badges/tickets (PDF) and support basic check-in at event start.

Rationale
- Provide an on-site experience closer to Indico’s badges and check-in.

Scope
- Simple template-based PDF generation; per-signup QR code.
- Check-in endpoint that marks attendance by scanning/entering code.

Acceptance Criteria
- Organizer can download badges for an activity; each badge has QR.
- Check-in API flips an attendance flag; basic UI feedback.

Tasks
- Add badge template and QR generation lib.
- Add attendance fields to Signup.
- Create endpoints for badge export and check-in.