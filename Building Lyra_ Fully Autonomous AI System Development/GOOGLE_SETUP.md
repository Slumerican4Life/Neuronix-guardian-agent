# Google Services Setup Instructions

## Overview
The Google Services integration provides Lyra with access to:
- **Google Calendar**: Create, read, update, and delete calendar events
- **Gmail**: Read, send, and manage email messages
- **Google Drive**: Upload, download, and manage files

## Setup Process

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable the following APIs:
   - Google Calendar API
   - Gmail API
   - Google Drive API

### 2. Configure OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **Internal** (for organization use) or **External** (for personal use)
3. Fill in required information:
   - App name: "Lyra AI System"
   - User support email: Your email
   - Developer contact: Your email

### 3. Create OAuth 2.0 Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. Choose **Desktop application**
4. Name: "Lyra Desktop Client"
5. Download the JSON file and save as `credentials.json` in the integrations directory

### 4. Required Scopes
The integration uses these OAuth scopes:
- `https://www.googleapis.com/auth/calendar` - Calendar access
- `https://www.googleapis.com/auth/gmail.readonly` - Read Gmail
- `https://www.googleapis.com/auth/gmail.send` - Send Gmail
- `https://www.googleapis.com/auth/gmail.modify` - Modify Gmail
- `https://www.googleapis.com/auth/drive` - Drive access
- `https://www.googleapis.com/auth/drive.file` - Drive file access

### 5. First Run Authentication
1. Place `credentials.json` in the integrations directory
2. Run any Google services operation
3. Browser will open for OAuth consent
4. Grant permissions to Lyra
5. Token will be saved as `token.pickle` for future use

## Usage Examples

### Calendar Operations
```python
# Create calendar event
event_id = google_services.create_calendar_event(
    title="Meeting with team",
    start_time="2025-06-10T10:00:00Z",
    end_time="2025-06-10T11:00:00Z",
    description="Weekly team sync",
    attendees=["team@company.com"]
)

# Get upcoming events
events = google_services.get_upcoming_calendar_events(days_ahead=7)
```

### Gmail Operations
```python
# Send email
message_id = google_services.send_gmail_message(
    to="recipient@example.com",
    subject="Update from Lyra",
    body="This is an automated message from Lyra AI."
)

# Read unread emails
emails = google_services.get_gmail_messages(query="is:unread", max_results=10)
```

### Drive Operations
```python
# Upload file
file_id = google_services.upload_drive_file(
    file_path="/path/to/file.pdf",
    file_name="document.pdf",
    description="Important document"
)

# List files
files = google_services.list_drive_files(query="name contains 'report'")
```

## Agent Integration

The Google Services Agent provides seamless integration with Lyra's multi-agent system:

```python
# Through agent system
await lyra_agent_manager.send_command('google_services', 'create_calendar_event', {
    'title': 'AI System Review',
    'start_time': '2025-06-10T14:00:00Z',
    'end_time': '2025-06-10T15:00:00Z',
    'description': 'Review Lyra system performance'
})
```

## Security Notes

1. **Credentials Protection**: Never commit `credentials.json` or `token.pickle` to version control
2. **Scope Limitation**: Only request necessary OAuth scopes
3. **Token Refresh**: Tokens are automatically refreshed when expired
4. **Audit Logging**: All operations are logged for security monitoring

## Troubleshooting

### Common Issues
1. **"Credentials file not found"**: Ensure `credentials.json` is in the integrations directory
2. **"Authentication failed"**: Check OAuth consent screen configuration
3. **"API not enabled"**: Enable required APIs in Google Cloud Console
4. **"Quota exceeded"**: Check API usage limits in Google Cloud Console

### Error Handling
The integration includes comprehensive error handling:
- HTTP errors from Google APIs
- Authentication failures
- Network connectivity issues
- Rate limiting and quota management

## Production Deployment

For production use:
1. Use service account credentials instead of OAuth for server applications
2. Implement proper secret management
3. Set up monitoring and alerting
4. Configure backup authentication methods
5. Implement rate limiting and retry logic

