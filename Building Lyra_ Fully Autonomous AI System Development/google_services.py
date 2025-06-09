"""
Google Services Integration for Lyra
===================================

Comprehensive integration module for Google services including Calendar, Gmail, Drive, and Cloud.
Provides unified interface for all Google API interactions with proper authentication and error handling.
"""

import os
import json
import pickle
import base64
import email
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    import io
except ImportError:
    print("Google API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

class GoogleServicesIntegration:
    """Unified Google services integration for Lyra"""
    
    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.pickle"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.credentials = None
        
        # Service instances
        self.calendar_service = None
        self.gmail_service = None
        self.drive_service = None
        
        # Scopes for different services
        self.scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
        ]
        
        # Setup logging
        self.logger = logging.getLogger("lyra.google_services")
        
        # Initialize authentication
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google services"""
        try:
            # Load existing credentials
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # If credentials are invalid or don't exist, get new ones
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        self.logger.error(f"Credentials file not found: {self.credentials_path}")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.scopes)
                    self.credentials = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Initialize services
            self._initialize_services()
            self.logger.info("Google services authentication successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def _initialize_services(self):
        """Initialize Google service instances"""
        try:
            self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
            self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            self.logger.info("Google services initialized successfully")
        except Exception as e:
            self.logger.error(f"Service initialization failed: {e}")
    
    # ==================== CALENDAR METHODS ====================
    
    def get_calendar_events(self, calendar_id: str = 'primary', max_results: int = 10, 
                           time_min: Optional[str] = None, time_max: Optional[str] = None) -> List[Dict]:
        """Get calendar events"""
        try:
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.calendar_service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'description': event.get('description', ''),
                    'start': start,
                    'end': end,
                    'location': event.get('location', ''),
                    'attendees': [attendee.get('email') for attendee in event.get('attendees', [])]
                })
            
            self.logger.info(f"Retrieved {len(formatted_events)} calendar events")
            return formatted_events
            
        except HttpError as e:
            self.logger.error(f"Calendar API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error getting calendar events: {e}")
            return []
    
    def create_calendar_event(self, title: str, start_time: str, end_time: str,
                             description: str = "", location: str = "", 
                             attendees: List[str] = None, calendar_id: str = 'primary') -> Optional[str]:
        """Create a calendar event"""
        try:
            event = {
                'summary': title,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': 'UTC',
                },
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = self.calendar_service.events().insert(
                calendarId=calendar_id, body=event).execute()
            
            event_id = created_event['id']
            self.logger.info(f"Created calendar event: {title} (ID: {event_id})")
            return event_id
            
        except HttpError as e:
            self.logger.error(f"Calendar API error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating calendar event: {e}")
            return None
    
    def update_calendar_event(self, event_id: str, updates: Dict, calendar_id: str = 'primary') -> bool:
        """Update a calendar event"""
        try:
            # Get existing event
            event = self.calendar_service.events().get(
                calendarId=calendar_id, eventId=event_id).execute()
            
            # Apply updates
            for key, value in updates.items():
                if key in ['start', 'end'] and isinstance(value, str):
                    event[key] = {'dateTime': value, 'timeZone': 'UTC'}
                else:
                    event[key] = value
            
            # Update event
            updated_event = self.calendar_service.events().update(
                calendarId=calendar_id, eventId=event_id, body=event).execute()
            
            self.logger.info(f"Updated calendar event: {event_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Calendar API error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error updating calendar event: {e}")
            return False
    
    def delete_calendar_event(self, event_id: str, calendar_id: str = 'primary') -> bool:
        """Delete a calendar event"""
        try:
            self.calendar_service.events().delete(
                calendarId=calendar_id, eventId=event_id).execute()
            
            self.logger.info(f"Deleted calendar event: {event_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Calendar API error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error deleting calendar event: {e}")
            return False
    
    # ==================== GMAIL METHODS ====================
    
    def get_gmail_messages(self, query: str = "", max_results: int = 10, 
                          label_ids: List[str] = None) -> List[Dict]:
        """Get Gmail messages"""
        try:
            # Search for messages
            search_params = {
                'userId': 'me',
                'q': query,
                'maxResults': max_results
            }
            
            if label_ids:
                search_params['labelIds'] = label_ids
            
            results = self.gmail_service.users().messages().list(**search_params).execute()
            messages = results.get('messages', [])
            
            formatted_messages = []
            for message in messages:
                # Get full message details
                msg = self.gmail_service.users().messages().get(
                    userId='me', id=message['id']).execute()
                
                # Extract headers
                headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
                
                # Extract body
                body = self._extract_message_body(msg['payload'])
                
                formatted_messages.append({
                    'id': message['id'],
                    'thread_id': msg['threadId'],
                    'subject': headers.get('Subject', 'No subject'),
                    'from': headers.get('From', 'Unknown sender'),
                    'to': headers.get('To', ''),
                    'date': headers.get('Date', ''),
                    'body': body,
                    'labels': msg.get('labelIds', []),
                    'snippet': msg.get('snippet', '')
                })
            
            self.logger.info(f"Retrieved {len(formatted_messages)} Gmail messages")
            return formatted_messages
            
        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error getting Gmail messages: {e}")
            return []
    
    def _extract_message_body(self, payload: Dict) -> str:
        """Extract message body from Gmail payload"""
        try:
            body = ""
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
                    elif part['mimeType'] == 'text/html' and not body:
                        data = part['body']['data']
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                if payload['mimeType'] == 'text/plain':
                    data = payload['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
            
            return body
            
        except Exception as e:
            self.logger.error(f"Error extracting message body: {e}")
            return ""
    
    def send_gmail_message(self, to: str, subject: str, body: str, 
                          from_email: str = None, cc: List[str] = None, 
                          bcc: List[str] = None) -> Optional[str]:
        """Send Gmail message"""
        try:
            # Create message
            message = email.mime.text.MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if from_email:
                message['from'] = from_email
            
            if cc:
                message['cc'] = ', '.join(cc)
            
            if bcc:
                message['bcc'] = ', '.join(bcc)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send message
            send_result = self.gmail_service.users().messages().send(
                userId='me', body={'raw': raw_message}).execute()
            
            message_id = send_result['id']
            self.logger.info(f"Sent Gmail message: {subject} (ID: {message_id})")
            return message_id
            
        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error sending Gmail message: {e}")
            return None
    
    def mark_message_as_read(self, message_id: str) -> bool:
        """Mark Gmail message as read"""
        try:
            self.gmail_service.users().messages().modify(
                userId='me', id=message_id, 
                body={'removeLabelIds': ['UNREAD']}).execute()
            
            self.logger.info(f"Marked message as read: {message_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error marking message as read: {e}")
            return False
    
    def delete_gmail_message(self, message_id: str) -> bool:
        """Delete Gmail message"""
        try:
            self.gmail_service.users().messages().delete(
                userId='me', id=message_id).execute()
            
            self.logger.info(f"Deleted Gmail message: {message_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error deleting Gmail message: {e}")
            return False
    
    # ==================== DRIVE METHODS ====================
    
    def list_drive_files(self, query: str = "", max_results: int = 10, 
                        folder_id: str = None) -> List[Dict]:
        """List Google Drive files"""
        try:
            search_query = query
            if folder_id:
                search_query += f" and parents in '{folder_id}'"
            
            results = self.drive_service.files().list(
                q=search_query,
                pageSize=max_results,
                fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, parents)"
            ).execute()
            
            files = results.get('files', [])
            
            formatted_files = []
            for file in files:
                formatted_files.append({
                    'id': file['id'],
                    'name': file['name'],
                    'mime_type': file['mimeType'],
                    'size': file.get('size', '0'),
                    'created_time': file['createdTime'],
                    'modified_time': file['modifiedTime'],
                    'parents': file.get('parents', [])
                })
            
            self.logger.info(f"Listed {len(formatted_files)} Drive files")
            return formatted_files
            
        except HttpError as e:
            self.logger.error(f"Drive API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error listing Drive files: {e}")
            return []
    
    def upload_drive_file(self, file_path: str, file_name: str = None, 
                         folder_id: str = None, description: str = "") -> Optional[str]:
        """Upload file to Google Drive"""
        try:
            if not file_name:
                file_name = os.path.basename(file_path)
            
            # File metadata
            file_metadata = {
                'name': file_name,
                'description': description
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Upload file
            media = MediaFileUpload(file_path, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata, media_body=media, fields='id').execute()
            
            file_id = file.get('id')
            self.logger.info(f"Uploaded file to Drive: {file_name} (ID: {file_id})")
            return file_id
            
        except HttpError as e:
            self.logger.error(f"Drive API error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error uploading file to Drive: {e}")
            return None
    
    def download_drive_file(self, file_id: str, download_path: str) -> bool:
        """Download file from Google Drive"""
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            
            with open(download_path, 'wb') as file:
                downloader = MediaIoBaseDownload(file, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
            
            self.logger.info(f"Downloaded file from Drive: {file_id} to {download_path}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Drive API error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error downloading file from Drive: {e}")
            return False
    
    def delete_drive_file(self, file_id: str) -> bool:
        """Delete file from Google Drive"""
        try:
            self.drive_service.files().delete(fileId=file_id).execute()
            
            self.logger.info(f"Deleted file from Drive: {file_id}")
            return True
            
        except HttpError as e:
            self.logger.error(f"Drive API error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error deleting file from Drive: {e}")
            return False
    
    def create_drive_folder(self, folder_name: str, parent_folder_id: str = None) -> Optional[str]:
        """Create folder in Google Drive"""
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            folder = self.drive_service.files().create(
                body=file_metadata, fields='id').execute()
            
            folder_id = folder.get('id')
            self.logger.info(f"Created Drive folder: {folder_name} (ID: {folder_id})")
            return folder_id
            
        except HttpError as e:
            self.logger.error(f"Drive API error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating Drive folder: {e}")
            return None
    
    # ==================== UTILITY METHODS ====================
    
    def get_user_profile(self) -> Optional[Dict]:
        """Get user profile information"""
        try:
            profile = self.gmail_service.users().getProfile(userId='me').execute()
            
            return {
                'email': profile['emailAddress'],
                'messages_total': profile['messagesTotal'],
                'threads_total': profile['threadsTotal'],
                'history_id': profile['historyId']
            }
            
        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting user profile: {e}")
            return None
    
    def search_emails_by_criteria(self, sender: str = None, subject: str = None, 
                                 has_attachment: bool = None, is_unread: bool = None,
                                 date_after: str = None, date_before: str = None) -> List[Dict]:
        """Search emails by various criteria"""
        query_parts = []
        
        if sender:
            query_parts.append(f"from:{sender}")
        if subject:
            query_parts.append(f"subject:{subject}")
        if has_attachment:
            query_parts.append("has:attachment")
        if is_unread:
            query_parts.append("is:unread")
        if date_after:
            query_parts.append(f"after:{date_after}")
        if date_before:
            query_parts.append(f"before:{date_before}")
        
        query = " ".join(query_parts)
        return self.get_gmail_messages(query=query)
    
    def get_upcoming_calendar_events(self, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming calendar events for specified days"""
        time_min = datetime.utcnow().isoformat() + 'Z'
        time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        return self.get_calendar_events(time_min=time_min, time_max=time_max, max_results=50)
    
    def backup_emails_to_drive(self, query: str = "is:important", folder_name: str = "Email Backup") -> bool:
        """Backup emails to Google Drive"""
        try:
            # Create backup folder
            folder_id = self.create_drive_folder(folder_name)
            if not folder_id:
                return False
            
            # Get emails
            emails = self.get_gmail_messages(query=query, max_results=100)
            
            # Save emails as JSON
            backup_data = {
                'backup_date': datetime.now().isoformat(),
                'query': query,
                'emails': emails
            }
            
            # Create temporary file
            backup_file = f"email_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            # Upload to Drive
            file_id = self.upload_drive_file(backup_file, folder_id=folder_id)
            
            # Clean up temporary file
            os.remove(backup_file)
            
            self.logger.info(f"Backed up {len(emails)} emails to Drive")
            return file_id is not None
            
        except Exception as e:
            self.logger.error(f"Error backing up emails: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if services are authenticated"""
        return (self.credentials is not None and 
                self.credentials.valid and 
                self.calendar_service is not None and 
                self.gmail_service is not None and 
                self.drive_service is not None)
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get status of all Google services"""
        return {
            'authenticated': self.is_authenticated(),
            'calendar': self.calendar_service is not None,
            'gmail': self.gmail_service is not None,
            'drive': self.drive_service is not None
        }

# Global Google services instance
google_services = GoogleServicesIntegration()

