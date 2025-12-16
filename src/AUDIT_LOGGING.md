# Audit Logging System

## Overview

The audit logging system records all key actions performed in the Mergington High School Activities application, including student signups, unregistrations, and future features like uploads and check-ins.

## Features

### What Gets Logged

- **Student Signups**: When a student signs up for an activity
- **Unregistrations**: When a student is unregistered from an activity
- **User Information**: Email address of the person performing the action
- **Activity Context**: Which activity was affected
- **IP Address**: Client IP address for security tracking
- **Timestamp**: UTC timestamp of when the action occurred

### Privacy-Aware Storage

- **Configurable Retention**: Set retention period via `AUDIT_LOG_RETENTION_DAYS` environment variable (default: 90 days)
- **Automatic Cleanup**: Old logs are automatically removed based on retention policy
- **Minimal Data Collection**: Only essential information is logged

## Admin Access

### Authentication

Access to audit logs requires admin role authentication. Use the admin token to authenticate.

### Admin Endpoints

#### View Audit Logs
```
GET /admin/audit-logs?limit=100&offset=0
Authorization: Bearer admin-token-xyz
```

Returns paginated audit logs with statistics.

#### Export Audit Logs
```
GET /admin/audit-logs/export
Authorization: Bearer admin-token-xyz
```

Downloads all audit logs as a CSV file.

#### Get Statistics
```
GET /admin/audit-logs/stats
Authorization: Bearer admin-token-xyz
```

Returns statistics including total logs, action counts, and retention information.

## Admin UI

Access the admin interface at: `http://localhost:8000/static/admin.html`

### Features

- **Statistics Dashboard**: View total logs and action counts at a glance
- **Log Table**: Browse all audit entries with pagination
- **Action Badges**: Color-coded badges for different action types
  - 🟢 Signup (Green)
  - 🔴 Unregister (Red)
  - 🔵 Upload (Blue)
  - 🟠 Check-in (Orange)
- **CSV Export**: Download complete audit trail
- **Refresh**: Reload data on demand
- **Timezone Support**: Timestamps include timezone information

## Configuration

### Environment Variables

```bash
# Set retention period in days (default: 90)
export AUDIT_LOG_RETENTION_DAYS=90

# Start the application
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Retention Policy

- Logs older than the retention period are automatically deleted
- Cleanup runs periodically (every 24 hours) to avoid performance impact
- Set `AUDIT_LOG_RETENTION_DAYS=0` to disable automatic cleanup (not recommended)

## Security

### Token Storage

- Admin tokens are stored in `sessionStorage` (not `localStorage`)
- Tokens are cleared when the browser session ends
- This reduces the risk of token theft from persistent storage

### IP Address Logging

- Captures client IP address for each action
- Supports proxy/load balancer environments via `X-Forwarded-For` header
- Helps with security audits and abuse prevention

### Access Control

- Only users with admin role can access audit logs
- Non-admin users receive a 403 Forbidden error
- All audit log endpoints require authentication

## Database Schema

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    action VARCHAR NOT NULL,
    user_email VARCHAR NOT NULL,
    activity_name VARCHAR,
    details VARCHAR,
    ip_address VARCHAR
);
```

## Example Usage

### View Recent Signups

```bash
curl -X GET "http://localhost:8000/admin/audit-logs?limit=10" \
  -H "Authorization: Bearer admin-token-xyz"
```

### Export All Logs

```bash
curl -X GET "http://localhost:8000/admin/audit-logs/export" \
  -H "Authorization: Bearer admin-token-xyz" \
  -o audit_logs.csv
```

### Check Statistics

```bash
curl -X GET "http://localhost:8000/admin/audit-logs/stats" \
  -H "Authorization: Bearer admin-token-xyz"
```

## Future Enhancements

The audit logging system is designed to be extensible. Future actions that could be logged include:

- **File Uploads**: When students or organizers upload files
- **Check-ins**: When students check in to activities
- **Activity Creation**: When new activities are created
- **Activity Deletion**: When activities are removed
- **Profile Updates**: When user profiles are modified

To add new logged actions, simply call the `log_audit_event` function:

```python
log_audit_event(
    db=db,
    action="new_action_type",
    user_email="user@example.com",
    activity_name="Activity Name",
    details="Description of what happened",
    ip_address=get_client_ip(request)
)
```

## Troubleshooting

### Cannot Access Admin Panel

- Verify you're using the correct admin token
- Check that the token is being sent in the Authorization header
- Ensure your browser allows sessionStorage

### Logs Not Appearing

- Check that actions are actually being logged (look for log_audit_event calls)
- Verify the database file has write permissions
- Check server logs for any errors

### Export Not Working

- Ensure you're authenticated with an admin token
- Check that your browser allows file downloads
- Verify the server has sufficient memory for large exports

## Support

For questions or issues related to the audit logging system, please refer to the main application documentation or contact the development team.
