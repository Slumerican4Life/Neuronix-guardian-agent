"""
Google Services Agent Integration
===============================

Integration layer between Lyra's agent system and Google services.
Provides agent-compatible interface for Google Calendar, Gmail, and Drive operations.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from agents.agent_framework import BaseAgent, AgentMessage, MessageType, AgentCapability
from integrations.google_services import google_services

class GoogleServicesAgent(BaseAgent):
    """Agent for Google services integration"""
    
    def __init__(self):
        super().__init__(
            agent_id="google_services",
            name="GOOGLE_SERVICES",
            description="Google services integration agent for Calendar, Gmail, and Drive"
        )
        
        # Google services capabilities
        self.add_capability(AgentCapability(
            name="calendar_management",
            description="Manage Google Calendar events and scheduling",
            input_types=["calendar_requests", "event_data"],
            output_types=["calendar_events", "event_confirmations"],
            resource_requirements={"google_api": "required", "network": "required"},
            execution_time_estimate=5.0
        ))
        
        self.add_capability(AgentCapability(
            name="email_management",
            description="Read, send, and manage Gmail messages",
            input_types=["email_queries", "message_data"],
            output_types=["email_messages", "send_confirmations"],
            resource_requirements={"google_api": "required", "network": "required"},
            execution_time_estimate=10.0
        ))
        
        self.add_capability(AgentCapability(
            name="drive_management",
            description="Upload, download, and manage Google Drive files",
            input_types=["file_operations", "drive_queries"],
            output_types=["file_listings", "upload_confirmations"],
            resource_requirements={"google_api": "required", "network": "required"},
            execution_time_estimate=15.0
        ))
        
        # Integration state
        self.google_authenticated = False
        self.last_sync_time = None
        self.cached_events = []
        self.cached_emails = []
    
    async def initialize(self):
        """Initialize Google services agent"""
        self.logger.info("Initializing Google Services agent...")
        
        # Check Google services authentication
        self.google_authenticated = google_services.is_authenticated()
        
        if self.google_authenticated:
            self.logger.info("Google services authenticated successfully")
            
            # Initial sync
            await self._sync_initial_data()
        else:
            self.logger.warning("Google services not authenticated - some features will be limited")
        
        self.logger.info("Google Services agent initialization complete")
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages for Google services operations"""
        try:
            if message.message_type == MessageType.COMMAND:
                return await self._handle_command(message)
            elif message.message_type == MessageType.QUERY:
                return await self._handle_query(message)
            else:
                self.logger.debug(f"Ignoring message type: {message.message_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return AgentMessage(
                id=f"err_{message.id}",
                sender=self.agent_id,
                recipient=message.sender,
                message_type=MessageType.RESPONSE,
                payload={"error": str(e), "success": False},
                correlation_id=message.correlation_id
            )
    
    async def _handle_command(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle command messages"""
        command = message.payload.get("command")
        parameters = message.payload.get("parameters", {})
        
        if command == "create_calendar_event":
            result = await self._create_calendar_event(parameters)
        elif command == "get_calendar_events":
            result = await self._get_calendar_events(parameters)
        elif command == "send_email":
            result = await self._send_email(parameters)
        elif command == "read_emails":
            result = await self._read_emails(parameters)
        elif command == "upload_file":
            result = await self._upload_file(parameters)
        elif command == "download_file":
            result = await self._download_file(parameters)
        elif command == "list_drive_files":
            result = await self._list_drive_files(parameters)
        elif command == "sync_data":
            result = await self._sync_data(parameters)
        else:
            result = {"error": f"Unknown command: {command}", "success": False}
        
        return AgentMessage(
            id=f"resp_{message.id}",
            sender=self.agent_id,
            recipient=message.sender,
            message_type=MessageType.RESPONSE,
            payload=result,
            correlation_id=message.correlation_id
        )
    
    async def _handle_query(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle query messages"""
        query_type = message.payload.get("query_type")
        
        if query_type == "service_status":
            result = await self._get_service_status(message.payload)
        elif query_type == "upcoming_events":
            result = await self._get_upcoming_events(message.payload)
        elif query_type == "unread_emails":
            result = await self._get_unread_emails(message.payload)
        elif query_type == "recent_files":
            result = await self._get_recent_files(message.payload)
        elif query_type == "capabilities":
            result = {"capabilities": list(self.capabilities.keys()), "success": True}
        else:
            result = {"error": f"Unknown query type: {query_type}", "success": False}
        
        return AgentMessage(
            id=f"resp_{message.id}",
            sender=self.agent_id,
            recipient=message.sender,
            message_type=MessageType.RESPONSE,
            payload=result,
            correlation_id=message.correlation_id
        )
    
    # ==================== CALENDAR OPERATIONS ====================
    
    async def _create_calendar_event(self, parameters: Dict) -> Dict:
        """Create a calendar event"""
        try:
            if not self.google_authenticated:
                return {"error": "Google services not authenticated", "success": False}
            
            title = parameters.get("title")
            start_time = parameters.get("start_time")
            end_time = parameters.get("end_time")
            description = parameters.get("description", "")
            location = parameters.get("location", "")
            attendees = parameters.get("attendees", [])
            
            if not title or not start_time or not end_time:
                return {"error": "Title, start_time, and end_time are required", "success": False}
            
            # Create event using Google services
            event_id = google_services.create_calendar_event(
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=description,
                location=location,
                attendees=attendees
            )
            
            if event_id:
                self.logger.info(f"Created calendar event: {title}")
                
                # Send alert to other agents
                if hasattr(self, 'message_bus'):
                    alert_message = AgentMessage(
                        id=f"cal_alert_{int(datetime.now().timestamp())}",
                        sender=self.agent_id,
                        recipient="broadcast",
                        message_type=MessageType.ALERT,
                        payload={
                            "type": "calendar_event_created",
                            "event_id": event_id,
                            "title": title,
                            "start_time": start_time
                        },
                        priority=6
                    )
                    await self.message_bus.send_message(alert_message)
                
                return {
                    "success": True,
                    "event_id": event_id,
                    "title": title,
                    "start_time": start_time
                }
            else:
                return {"error": "Failed to create calendar event", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error creating calendar event: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_calendar_events(self, parameters: Dict) -> Dict:
        """Get calendar events"""
        try:
            if not self.google_authenticated:
                return {"error": "Google services not authenticated", "success": False}
            
            max_results = parameters.get("max_results", 10)
            days_ahead = parameters.get("days_ahead", 7)
            
            # Get events
            events = google_services.get_upcoming_calendar_events(days_ahead=days_ahead)
            
            # Limit results
            events = events[:max_results]
            
            self.logger.info(f"Retrieved {len(events)} calendar events")
            
            return {
                "success": True,
                "events": events,
                "count": len(events)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting calendar events: {e}")
            return {"error": str(e), "success": False}
    
    # ==================== EMAIL OPERATIONS ====================
    
    async def _send_email(self, parameters: Dict) -> Dict:
        """Send an email"""
        try:
            if not self.google_authenticated:
                return {"error": "Google services not authenticated", "success": False}
            
            to = parameters.get("to")
            subject = parameters.get("subject")
            body = parameters.get("body")
            cc = parameters.get("cc", [])
            bcc = parameters.get("bcc", [])
            
            if not to or not subject or not body:
                return {"error": "To, subject, and body are required", "success": False}
            
            # Send email using Google services
            message_id = google_services.send_gmail_message(
                to=to,
                subject=subject,
                body=body,
                cc=cc,
                bcc=bcc
            )
            
            if message_id:
                self.logger.info(f"Sent email: {subject} to {to}")
                
                return {
                    "success": True,
                    "message_id": message_id,
                    "to": to,
                    "subject": subject
                }
            else:
                return {"error": "Failed to send email", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return {"error": str(e), "success": False}
    
    async def _read_emails(self, parameters: Dict) -> Dict:
        """Read emails"""
        try:
            if not self.google_authenticated:
                return {"error": "Google services not authenticated", "success": False}
            
            query = parameters.get("query", "")
            max_results = parameters.get("max_results", 10)
            mark_as_read = parameters.get("mark_as_read", False)
            
            # Get emails
            emails = google_services.get_gmail_messages(query=query, max_results=max_results)
            
            # Mark as read if requested
            if mark_as_read:
                for email in emails:
                    google_services.mark_message_as_read(email['id'])
            
            self.logger.info(f"Retrieved {len(emails)} emails")
            
            return {
                "success": True,
                "emails": emails,
                "count": len(emails)
            }
            
        except Exception as e:
            self.logger.error(f"Error reading emails: {e}")
            return {"error": str(e), "success": False}
    
    # ==================== DRIVE OPERATIONS ====================
    
    async def _upload_file(self, parameters: Dict) -> Dict:
        """Upload file to Google Drive"""
        try:
            if not self.google_authenticated:
                return {"error": "Google services not authenticated", "success": False}
            
            file_path = parameters.get("file_path")
            file_name = parameters.get("file_name")
            folder_id = parameters.get("folder_id")
            description = parameters.get("description", "")
            
            if not file_path:
                return {"error": "File path is required", "success": False}
            
            # Upload file
            file_id = google_services.upload_drive_file(
                file_path=file_path,
                file_name=file_name,
                folder_id=folder_id,
                description=description
            )
            
            if file_id:
                self.logger.info(f"Uploaded file to Drive: {file_path}")
                
                return {
                    "success": True,
                    "file_id": file_id,
                    "file_path": file_path
                }
            else:
                return {"error": "Failed to upload file", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error uploading file: {e}")
            return {"error": str(e), "success": False}
    
    async def _download_file(self, parameters: Dict) -> Dict:
        """Download file from Google Drive"""
        try:
            if not self.google_authenticated:
                return {"error": "Google services not authenticated", "success": False}
            
            file_id = parameters.get("file_id")
            download_path = parameters.get("download_path")
            
            if not file_id or not download_path:
                return {"error": "File ID and download path are required", "success": False}
            
            # Download file
            success = google_services.download_drive_file(file_id, download_path)
            
            if success:
                self.logger.info(f"Downloaded file from Drive: {file_id}")
                
                return {
                    "success": True,
                    "file_id": file_id,
                    "download_path": download_path
                }
            else:
                return {"error": "Failed to download file", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error downloading file: {e}")
            return {"error": str(e), "success": False}
    
    async def _list_drive_files(self, parameters: Dict) -> Dict:
        """List Google Drive files"""
        try:
            if not self.google_authenticated:
                return {"error": "Google services not authenticated", "success": False}
            
            query = parameters.get("query", "")
            max_results = parameters.get("max_results", 10)
            folder_id = parameters.get("folder_id")
            
            # List files
            files = google_services.list_drive_files(
                query=query,
                max_results=max_results,
                folder_id=folder_id
            )
            
            self.logger.info(f"Listed {len(files)} Drive files")
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
            
        except Exception as e:
            self.logger.error(f"Error listing Drive files: {e}")
            return {"error": str(e), "success": False}
    
    # ==================== SYNC AND STATUS OPERATIONS ====================
    
    async def _sync_data(self, parameters: Dict) -> Dict:
        """Sync data from Google services"""
        try:
            if not self.google_authenticated:
                return {"error": "Google services not authenticated", "success": False}
            
            sync_calendar = parameters.get("sync_calendar", True)
            sync_emails = parameters.get("sync_emails", True)
            
            synced_data = {}
            
            if sync_calendar:
                self.cached_events = google_services.get_upcoming_calendar_events(days_ahead=30)
                synced_data["calendar_events"] = len(self.cached_events)
            
            if sync_emails:
                self.cached_emails = google_services.get_gmail_messages(query="is:unread", max_results=50)
                synced_data["unread_emails"] = len(self.cached_emails)
            
            self.last_sync_time = datetime.now().isoformat()
            
            self.logger.info(f"Synced Google services data: {synced_data}")
            
            return {
                "success": True,
                "synced_data": synced_data,
                "sync_time": self.last_sync_time
            }
            
        except Exception as e:
            self.logger.error(f"Error syncing data: {e}")
            return {"error": str(e), "success": False}
    
    async def _sync_initial_data(self):
        """Perform initial data sync"""
        try:
            await self._sync_data({"sync_calendar": True, "sync_emails": True})
        except Exception as e:
            self.logger.error(f"Error in initial sync: {e}")
    
    async def _get_service_status(self, parameters: Dict) -> Dict:
        """Get Google services status"""
        try:
            status = google_services.get_service_status()
            
            return {
                "success": True,
                "google_services_status": status,
                "last_sync": self.last_sync_time,
                "cached_events": len(self.cached_events),
                "cached_emails": len(self.cached_emails)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting service status: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_upcoming_events(self, parameters: Dict) -> Dict:
        """Get upcoming calendar events"""
        try:
            days_ahead = parameters.get("days_ahead", 7)
            
            if self.cached_events:
                # Filter cached events
                now = datetime.now()
                end_time = now + timedelta(days=days_ahead)
                
                upcoming = []
                for event in self.cached_events:
                    event_start = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                    if now <= event_start <= end_time:
                        upcoming.append(event)
                
                return {
                    "success": True,
                    "upcoming_events": upcoming[:10],
                    "count": len(upcoming)
                }
            else:
                # Fetch fresh data
                return await self._get_calendar_events({"days_ahead": days_ahead, "max_results": 10})
                
        except Exception as e:
            self.logger.error(f"Error getting upcoming events: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_unread_emails(self, parameters: Dict) -> Dict:
        """Get unread emails"""
        try:
            max_results = parameters.get("max_results", 10)
            
            if self.cached_emails:
                return {
                    "success": True,
                    "unread_emails": self.cached_emails[:max_results],
                    "count": len(self.cached_emails)
                }
            else:
                # Fetch fresh data
                return await self._read_emails({"query": "is:unread", "max_results": max_results})
                
        except Exception as e:
            self.logger.error(f"Error getting unread emails: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_recent_files(self, parameters: Dict) -> Dict:
        """Get recent Drive files"""
        try:
            max_results = parameters.get("max_results", 10)
            
            return await self._list_drive_files({
                "query": "trashed=false",
                "max_results": max_results
            })
            
        except Exception as e:
            self.logger.error(f"Error getting recent files: {e}")
            return {"error": str(e), "success": False}
    
    async def shutdown(self):
        """Shutdown Google services agent"""
        self.logger.info("Shutting down Google Services agent...")
        
        # Save cached data
        try:
            cache_data = {
                "last_sync_time": self.last_sync_time,
                "cached_events": self.cached_events,
                "cached_emails": self.cached_emails,
                "google_authenticated": self.google_authenticated
            }
            
            with open("integrations/google_services_cache.json", "w") as f:
                json.dump(cache_data, f, indent=2)
                
            self.logger.info("Google services cache saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving Google services cache: {e}")

# Create Google services agent instance
google_services_agent = GoogleServicesAgent()

