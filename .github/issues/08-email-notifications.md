Summary
- Send email notifications for signup confirmations, capacity reached, and reminders.

Rationale
- Improve communication and align with Indico’s emailing capabilities.

Scope
- SMTP integration; simple templated emails.
- Background sending to avoid blocking requests.

Acceptance Criteria
- On successful signup, registrant receives confirmation email.
- Organizer can trigger a reminder to all participants of an activity.

Tasks
- Add SMTP settings and mailer utility.
- Create basic email templates.
- Add endpoints/commands to send reminders.