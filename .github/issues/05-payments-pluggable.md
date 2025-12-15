Summary
- Add a pluggable payments interface for paid activities (gateway-agnostic).

Rationale
- Enable paid registrations similar to Indico’s payment plugins.

Scope
- Abstract payments service; start with a dummy provider; plan for Stripe/etc.
- Record payment status on signup.

Acceptance Criteria
- Activities can be marked paid/free with a price field.
- For paid activities, signups require a successful payment (dummy in dev).

Tasks
- Define payments service interface and webhook handler shape.
- Add payment fields to Activity/Signup.
- Implement a mock provider and document integration points.