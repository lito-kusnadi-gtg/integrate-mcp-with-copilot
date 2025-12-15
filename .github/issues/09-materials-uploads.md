## Summary
- Allow organizers to upload materials (PDF, slides) per activity with access control.

## Rationale
- Support sharing resources and archival akin to Indico materials.

## Scope
- File uploads to local storage (dev) with metadata in DB.
- Download endpoints honor permissions; public/private toggle.

## Acceptance Criteria
- Organizer can upload and list materials under an activity.
- Public can download when marked public; private requires organizer role.

## Tasks
- Add storage path config and model for Attachment/Material.
- Implement upload/download endpoints and ACL checks.
- Display materials section in the UI.