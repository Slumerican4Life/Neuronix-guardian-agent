"""
ATLAS Agent - Scheduling and Executive Management
===============================================

Specialized agent for time management, scheduling, and executive coordination.
Handles Google Calendar integration, task management, and deadline tracking.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import calendar
import time

from agent_framework import BaseAgent, AgentMessage, MessageType, AgentCapability

class AtlasAgent(BaseAgent):
    """Scheduling and executive management agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="atlas",
            name="ATLAS",
            description="Scheduling and executive management agent"
        )
        
        # Scheduling capabilities
        self.add_capability(AgentCapability(
            name="calendar_management",
            description="Manage Google Calendar events and scheduling",
            input_types=["calendar_events", "scheduling_requests"],
            output_types=["calendar_updates", "scheduling_confirmations"],
            resource_requirements={"google_api": "required", "cpu": "low"},
            execution_time_estimate=5.0
        ))
        
        self.add_capability(AgentCapability(
            name="task_scheduling",
            description="Schedule and prioritize tasks with deadlines",
            input_types=["tasks", "priorities", "deadlines"],
            output_types=["schedules", "priority_lists", "reminders"],
            resource_requirements={"cpu": "low", "memory": "low"},
            execution_time_estimate=3.0
        ))
        
        self.add_capability(AgentCapability(
            name="deadline_tracking",
            description="Track deadlines and send alerts",
            input_types=["deadlines", "projects"],
            output_types=["alerts", "status_reports", "reminders"],
            resource_requirements={"cpu": "low"},
            execution_time_estimate=2.0
        ))
        
        self.add_capability(AgentCapability(
            name="meeting_coordination",
            description="Coordinate meetings and manage attendees",
            input_types=["meeting_requests", "attendee_lists", "availability"],
            output_types=["meeting_schedules", "invitations", "confirmations"],
            resource_requirements={"google_api": "required", "email": "required"},
            execution_time_estimate=10.0
        ))
        
        self.add_capability(AgentCapability(
            name="time_optimization",
            description="Optimize schedules and identify time conflicts",
            input_types=["schedules", "priorities", "constraints"],
            output_types=["optimized_schedules", "conflict_reports", "recommendations"],
            resource_requirements={"cpu": "medium"},
            execution_time_estimate=15.0
        ))
        
        # Scheduling state
        self.scheduled_tasks: Dict[str, Dict] = {}
        self.calendar_events: Dict[str, Dict] = {}
        self.deadlines: Dict[str, Dict] = {}
        self.reminders: List[Dict] = []
        self.time_blocks: Dict[str, List[Dict]] = {}
        
        # Google Calendar integration (placeholder)
        self.google_calendar_enabled = False
        self.calendar_service = None
    
    async def initialize(self):
        """Initialize ATLAS agent resources"""
        self.logger.info("Initializing ATLAS scheduling systems...")
        
        # Initialize scheduling storage
        self.scheduled_tasks = {}
        self.calendar_events = {}
        self.deadlines = {}
        self.reminders = []
        
        # Setup scheduling directories
        os.makedirs("schedules", exist_ok=True)
        os.makedirs("calendar_data", exist_ok=True)
        
        # Initialize Google Calendar (placeholder)
        self.google_calendar_enabled = await self._init_google_calendar()
        
        # Start reminder checking loop
        asyncio.create_task(self._reminder_loop())
        
        self.logger.info(f"ATLAS initialization complete (Google Calendar: {'enabled' if self.google_calendar_enabled else 'disabled'})")
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages for scheduling operations"""
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
        
        if command == "schedule_task":
            result = await self._schedule_task(parameters)
        elif command == "create_calendar_event":
            result = await self._create_calendar_event(parameters)
        elif command == "set_deadline":
            result = await self._set_deadline(parameters)
        elif command == "schedule_meeting":
            result = await self._schedule_meeting(parameters)
        elif command == "optimize_schedule":
            result = await self._optimize_schedule(parameters)
        elif command == "set_reminder":
            result = await self._set_reminder(parameters)
        elif command == "check_availability":
            result = await self._check_availability(parameters)
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
        
        if query_type == "schedule_status":
            result = await self._get_schedule_status(message.payload)
        elif query_type == "upcoming_events":
            result = await self._get_upcoming_events(message.payload)
        elif query_type == "deadline_report":
            result = await self._get_deadline_report(message.payload)
        elif query_type == "time_analysis":
            result = await self._get_time_analysis(message.payload)
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
    
    async def _schedule_task(self, parameters: Dict) -> Dict:
        """Schedule a new task"""
        try:
            task_name = parameters.get("name")
            description = parameters.get("description", "")
            priority = parameters.get("priority", 5)  # 1-10 scale
            estimated_duration = parameters.get("duration", 60)  # minutes
            deadline = parameters.get("deadline")
            dependencies = parameters.get("dependencies", [])
            
            if not task_name:
                return {"error": "Task name is required", "success": False}
            
            task_id = f"task_{int(time.time())}_{len(self.scheduled_tasks)}"
            
            # Find optimal time slot
            optimal_slot = await self._find_optimal_time_slot(estimated_duration, deadline, priority)
            
            task = {
                "id": task_id,
                "name": task_name,
                "description": description,
                "priority": priority,
                "estimated_duration": estimated_duration,
                "deadline": deadline,
                "dependencies": dependencies,
                "scheduled_time": optimal_slot,
                "status": "scheduled",
                "created_at": datetime.now().isoformat(),
                "completed_at": None
            }
            
            self.scheduled_tasks[task_id] = task
            
            # Set reminder if deadline exists
            if deadline:
                await self._create_deadline_reminder(task_id, deadline)
            
            self.logger.info(f"Scheduled task: {task_name} for {optimal_slot}")
            
            return {
                "success": True,
                "task_id": task_id,
                "scheduled_time": optimal_slot,
                "priority": priority
            }
            
        except Exception as e:
            self.logger.error(f"Error scheduling task: {e}")
            return {"error": str(e), "success": False}
    
    async def _find_optimal_time_slot(self, duration: int, deadline: Optional[str], priority: int) -> str:
        """Find optimal time slot for task scheduling"""
        try:
            now = datetime.now()
            
            # If deadline specified, work backwards from deadline
            if deadline:
                deadline_dt = datetime.fromisoformat(deadline)
                # Schedule 25% before deadline to allow buffer
                buffer_time = (deadline_dt - now) * 0.25
                optimal_time = deadline_dt - buffer_time
            else:
                # Schedule based on priority
                if priority >= 8:  # High priority - schedule soon
                    optimal_time = now + timedelta(hours=2)
                elif priority >= 5:  # Medium priority - schedule within day
                    optimal_time = now + timedelta(hours=8)
                else:  # Low priority - schedule within week
                    optimal_time = now + timedelta(days=2)
            
            # Round to next hour
            optimal_time = optimal_time.replace(minute=0, second=0, microsecond=0)
            
            # Check for conflicts and adjust if needed
            while await self._has_time_conflict(optimal_time, duration):
                optimal_time += timedelta(hours=1)
            
            return optimal_time.isoformat()
            
        except Exception as e:
            self.logger.error(f"Error finding optimal time slot: {e}")
            # Fallback to 2 hours from now
            return (datetime.now() + timedelta(hours=2)).isoformat()
    
    async def _has_time_conflict(self, start_time: datetime, duration: int) -> bool:
        """Check if proposed time slot conflicts with existing schedule"""
        end_time = start_time + timedelta(minutes=duration)
        
        # Check against scheduled tasks
        for task in self.scheduled_tasks.values():
            if task["status"] != "scheduled":
                continue
                
            task_start = datetime.fromisoformat(task["scheduled_time"])
            task_end = task_start + timedelta(minutes=task["estimated_duration"])
            
            # Check for overlap
            if (start_time < task_end) and (end_time > task_start):
                return True
        
        # Check against calendar events
        for event in self.calendar_events.values():
            event_start = datetime.fromisoformat(event["start_time"])
            event_end = datetime.fromisoformat(event["end_time"])
            
            # Check for overlap
            if (start_time < event_end) and (end_time > event_start):
                return True
        
        return False
    
    async def _create_calendar_event(self, parameters: Dict) -> Dict:
        """Create a calendar event"""
        try:
            title = parameters.get("title")
            description = parameters.get("description", "")
            start_time = parameters.get("start_time")
            end_time = parameters.get("end_time")
            attendees = parameters.get("attendees", [])
            location = parameters.get("location", "")
            
            if not title or not start_time or not end_time:
                return {"error": "Title, start_time, and end_time are required", "success": False}
            
            event_id = f"event_{int(time.time())}_{len(self.calendar_events)}"
            
            event = {
                "id": event_id,
                "title": title,
                "description": description,
                "start_time": start_time,
                "end_time": end_time,
                "attendees": attendees,
                "location": location,
                "created_at": datetime.now().isoformat(),
                "status": "confirmed"
            }
            
            self.calendar_events[event_id] = event
            
            # If Google Calendar is enabled, sync to Google Calendar
            if self.google_calendar_enabled:
                await self._sync_to_google_calendar(event)
            
            self.logger.info(f"Created calendar event: {title}")
            
            return {
                "success": True,
                "event_id": event_id,
                "title": title,
                "start_time": start_time
            }
            
        except Exception as e:
            self.logger.error(f"Error creating calendar event: {e}")
            return {"error": str(e), "success": False}
    
    async def _set_deadline(self, parameters: Dict) -> Dict:
        """Set a deadline for tracking"""
        try:
            name = parameters.get("name")
            deadline_time = parameters.get("deadline")
            description = parameters.get("description", "")
            priority = parameters.get("priority", 5)
            project = parameters.get("project", "")
            
            if not name or not deadline_time:
                return {"error": "Name and deadline time are required", "success": False}
            
            deadline_id = f"deadline_{int(time.time())}_{len(self.deadlines)}"
            
            deadline = {
                "id": deadline_id,
                "name": name,
                "deadline": deadline_time,
                "description": description,
                "priority": priority,
                "project": project,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "completed_at": None
            }
            
            self.deadlines[deadline_id] = deadline
            
            # Create reminders
            await self._create_deadline_reminders(deadline_id, deadline_time)
            
            self.logger.info(f"Set deadline: {name} for {deadline_time}")
            
            return {
                "success": True,
                "deadline_id": deadline_id,
                "name": name,
                "deadline": deadline_time
            }
            
        except Exception as e:
            self.logger.error(f"Error setting deadline: {e}")
            return {"error": str(e), "success": False}
    
    async def _create_deadline_reminders(self, deadline_id: str, deadline_time: str):
        """Create multiple reminders for a deadline"""
        try:
            deadline_dt = datetime.fromisoformat(deadline_time)
            now = datetime.now()
            
            # Create reminders at different intervals
            reminder_intervals = [
                timedelta(days=7),   # 1 week before
                timedelta(days=3),   # 3 days before
                timedelta(days=1),   # 1 day before
                timedelta(hours=4),  # 4 hours before
                timedelta(hours=1),  # 1 hour before
            ]
            
            for interval in reminder_intervals:
                reminder_time = deadline_dt - interval
                
                # Only create reminder if it's in the future
                if reminder_time > now:
                    reminder = {
                        "id": f"reminder_{deadline_id}_{interval.total_seconds()}",
                        "deadline_id": deadline_id,
                        "reminder_time": reminder_time.isoformat(),
                        "interval": str(interval),
                        "status": "pending",
                        "created_at": datetime.now().isoformat()
                    }
                    
                    self.reminders.append(reminder)
            
        except Exception as e:
            self.logger.error(f"Error creating deadline reminders: {e}")
    
    async def _schedule_meeting(self, parameters: Dict) -> Dict:
        """Schedule a meeting with attendees"""
        try:
            title = parameters.get("title")
            attendees = parameters.get("attendees", [])
            duration = parameters.get("duration", 60)  # minutes
            preferred_times = parameters.get("preferred_times", [])
            description = parameters.get("description", "")
            
            if not title or not attendees:
                return {"error": "Title and attendees are required", "success": False}
            
            # Find best time slot
            if preferred_times:
                best_time = preferred_times[0]  # Use first preferred time for now
            else:
                # Find next available slot
                best_time = await self._find_next_available_slot(duration)
            
            # Create calendar event
            event_params = {
                "title": title,
                "description": description,
                "start_time": best_time,
                "end_time": (datetime.fromisoformat(best_time) + timedelta(minutes=duration)).isoformat(),
                "attendees": attendees
            }
            
            event_result = await self._create_calendar_event(event_params)
            
            if event_result["success"]:
                # Send meeting invitations (placeholder)
                await self._send_meeting_invitations(event_result["event_id"], attendees)
                
                self.logger.info(f"Scheduled meeting: {title} with {len(attendees)} attendees")
                
                return {
                    "success": True,
                    "event_id": event_result["event_id"],
                    "meeting_time": best_time,
                    "attendees_count": len(attendees)
                }
            else:
                return event_result
            
        except Exception as e:
            self.logger.error(f"Error scheduling meeting: {e}")
            return {"error": str(e), "success": False}
    
    async def _find_next_available_slot(self, duration: int) -> str:
        """Find next available time slot of specified duration"""
        now = datetime.now()
        
        # Start looking from next hour
        candidate_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        
        # Look for available slot within next 7 days
        end_search = now + timedelta(days=7)
        
        while candidate_time < end_search:
            if not await self._has_time_conflict(candidate_time, duration):
                return candidate_time.isoformat()
            
            candidate_time += timedelta(hours=1)
        
        # Fallback to 24 hours from now
        return (now + timedelta(days=1)).isoformat()
    
    async def _send_meeting_invitations(self, event_id: str, attendees: List[str]):
        """Send meeting invitations to attendees (placeholder)"""
        # This would integrate with email system
        self.logger.info(f"Sending meeting invitations for event {event_id} to {len(attendees)} attendees")
        
        # Placeholder - would send actual emails
        for attendee in attendees:
            self.logger.info(f"Invitation sent to: {attendee}")
    
    async def _optimize_schedule(self, parameters: Dict) -> Dict:
        """Optimize schedule for better time management"""
        try:
            date_range = parameters.get("date_range", 7)  # days
            
            # Analyze current schedule
            optimization_report = await self._analyze_schedule_efficiency(date_range)
            
            # Generate recommendations
            recommendations = await self._generate_schedule_recommendations(optimization_report)
            
            self.logger.info(f"Schedule optimization completed with {len(recommendations)} recommendations")
            
            return {
                "success": True,
                "optimization_report": optimization_report,
                "recommendations": recommendations,
                "efficiency_score": optimization_report.get("efficiency_score", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing schedule: {e}")
            return {"error": str(e), "success": False}
    
    async def _analyze_schedule_efficiency(self, days: int) -> Dict:
        """Analyze schedule efficiency over specified days"""
        try:
            now = datetime.now()
            start_date = now
            end_date = now + timedelta(days=days)
            
            # Count scheduled items
            tasks_in_range = 0
            events_in_range = 0
            total_scheduled_time = 0
            
            for task in self.scheduled_tasks.values():
                task_time = datetime.fromisoformat(task["scheduled_time"])
                if start_date <= task_time <= end_date:
                    tasks_in_range += 1
                    total_scheduled_time += task["estimated_duration"]
            
            for event in self.calendar_events.values():
                event_start = datetime.fromisoformat(event["start_time"])
                event_end = datetime.fromisoformat(event["end_time"])
                if start_date <= event_start <= end_date:
                    events_in_range += 1
                    total_scheduled_time += (event_end - event_start).total_seconds() / 60
            
            # Calculate efficiency metrics
            total_available_time = days * 8 * 60  # 8 working hours per day
            utilization_rate = total_scheduled_time / total_available_time if total_available_time > 0 else 0
            
            # Simple efficiency score (0-100)
            efficiency_score = min(100, utilization_rate * 100)
            
            return {
                "date_range": days,
                "tasks_scheduled": tasks_in_range,
                "events_scheduled": events_in_range,
                "total_scheduled_minutes": total_scheduled_time,
                "utilization_rate": utilization_rate,
                "efficiency_score": efficiency_score,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing schedule efficiency: {e}")
            return {}
    
    async def _generate_schedule_recommendations(self, analysis: Dict) -> List[Dict]:
        """Generate schedule optimization recommendations"""
        recommendations = []
        
        try:
            utilization_rate = analysis.get("utilization_rate", 0)
            
            if utilization_rate < 0.3:
                recommendations.append({
                    "type": "underutilization",
                    "priority": "medium",
                    "description": "Schedule utilization is low. Consider adding more productive tasks.",
                    "action": "Schedule additional high-priority tasks"
                })
            elif utilization_rate > 0.8:
                recommendations.append({
                    "type": "overutilization",
                    "priority": "high",
                    "description": "Schedule is heavily packed. Consider redistributing tasks.",
                    "action": "Move some tasks to less busy periods"
                })
            
            # Check for deadline conflicts
            upcoming_deadlines = [d for d in self.deadlines.values() if d["status"] == "active"]
            if len(upcoming_deadlines) > 5:
                recommendations.append({
                    "type": "deadline_pressure",
                    "priority": "high",
                    "description": f"{len(upcoming_deadlines)} active deadlines detected.",
                    "action": "Review and prioritize deadline-related tasks"
                })
            
            # Check for task clustering
            if analysis.get("tasks_scheduled", 0) > analysis.get("events_scheduled", 0) * 3:
                recommendations.append({
                    "type": "task_clustering",
                    "priority": "low",
                    "description": "Many tasks scheduled. Consider batching similar tasks.",
                    "action": "Group similar tasks together for better focus"
                })
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    async def _set_reminder(self, parameters: Dict) -> Dict:
        """Set a custom reminder"""
        try:
            message = parameters.get("message")
            reminder_time = parameters.get("time")
            priority = parameters.get("priority", 5)
            
            if not message or not reminder_time:
                return {"error": "Message and time are required", "success": False}
            
            reminder = {
                "id": f"reminder_{int(time.time())}",
                "message": message,
                "reminder_time": reminder_time,
                "priority": priority,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            
            self.reminders.append(reminder)
            
            self.logger.info(f"Set reminder: {message} for {reminder_time}")
            
            return {
                "success": True,
                "reminder_id": reminder["id"],
                "message": message,
                "time": reminder_time
            }
            
        except Exception as e:
            self.logger.error(f"Error setting reminder: {e}")
            return {"error": str(e), "success": False}
    
    async def _check_availability(self, parameters: Dict) -> Dict:
        """Check availability for a time period"""
        try:
            start_time = parameters.get("start_time")
            end_time = parameters.get("end_time")
            
            if not start_time or not end_time:
                return {"error": "Start time and end time are required", "success": False}
            
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
            
            # Check for conflicts
            conflicts = []
            
            # Check tasks
            for task in self.scheduled_tasks.values():
                if task["status"] != "scheduled":
                    continue
                    
                task_start = datetime.fromisoformat(task["scheduled_time"])
                task_end = task_start + timedelta(minutes=task["estimated_duration"])
                
                if (start_dt < task_end) and (end_dt > task_start):
                    conflicts.append({
                        "type": "task",
                        "name": task["name"],
                        "start": task_start.isoformat(),
                        "end": task_end.isoformat()
                    })
            
            # Check events
            for event in self.calendar_events.values():
                event_start = datetime.fromisoformat(event["start_time"])
                event_end = datetime.fromisoformat(event["end_time"])
                
                if (start_dt < event_end) and (end_dt > event_start):
                    conflicts.append({
                        "type": "event",
                        "name": event["title"],
                        "start": event_start.isoformat(),
                        "end": event_end.isoformat()
                    })
            
            is_available = len(conflicts) == 0
            
            return {
                "success": True,
                "available": is_available,
                "conflicts": conflicts,
                "conflict_count": len(conflicts)
            }
            
        except Exception as e:
            self.logger.error(f"Error checking availability: {e}")
            return {"error": str(e), "success": False}
    
    async def _reminder_loop(self):
        """Main loop for checking and sending reminders"""
        while self.running:
            try:
                now = datetime.now()
                
                # Check for due reminders
                due_reminders = []
                for reminder in self.reminders:
                    if reminder["status"] == "pending":
                        reminder_time = datetime.fromisoformat(reminder["reminder_time"])
                        if now >= reminder_time:
                            due_reminders.append(reminder)
                
                # Send due reminders
                for reminder in due_reminders:
                    await self._send_reminder(reminder)
                    reminder["status"] = "sent"
                
                # Sleep for 1 minute before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in reminder loop: {e}")
                await asyncio.sleep(60)
    
    async def _send_reminder(self, reminder: Dict):
        """Send a reminder alert"""
        try:
            # Send reminder as alert message
            if hasattr(self, 'message_bus'):
                alert_message = AgentMessage(
                    id=f"reminder_{reminder['id']}",
                    sender=self.agent_id,
                    recipient="broadcast",
                    message_type=MessageType.ALERT,
                    payload={
                        "type": "reminder",
                        "message": reminder["message"],
                        "priority": reminder["priority"],
                        "timestamp": datetime.now().isoformat()
                    },
                    priority=reminder["priority"]
                )
                await self.message_bus.send_message(alert_message)
            
            self.logger.info(f"📅 REMINDER: {reminder['message']}")
            
        except Exception as e:
            self.logger.error(f"Error sending reminder: {e}")
    
    async def _init_google_calendar(self) -> bool:
        """Initialize Google Calendar integration (placeholder)"""
        # This would set up Google Calendar API credentials and service
        # For now, return False to indicate it's not available
        return False
    
    async def _sync_to_google_calendar(self, event: Dict):
        """Sync event to Google Calendar (placeholder)"""
        # This would use Google Calendar API to create/update events
        self.logger.info(f"Syncing event to Google Calendar: {event['title']}")
    
    async def _get_schedule_status(self, parameters: Dict) -> Dict:
        """Get current schedule status"""
        try:
            return {
                "success": True,
                "scheduled_tasks": len(self.scheduled_tasks),
                "calendar_events": len(self.calendar_events),
                "active_deadlines": len([d for d in self.deadlines.values() if d["status"] == "active"]),
                "pending_reminders": len([r for r in self.reminders if r["status"] == "pending"]),
                "google_calendar_enabled": self.google_calendar_enabled
            }
            
        except Exception as e:
            self.logger.error(f"Error getting schedule status: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_upcoming_events(self, parameters: Dict) -> Dict:
        """Get upcoming events and tasks"""
        try:
            days_ahead = parameters.get("days", 7)
            now = datetime.now()
            end_time = now + timedelta(days=days_ahead)
            
            upcoming_items = []
            
            # Add tasks
            for task in self.scheduled_tasks.values():
                if task["status"] == "scheduled":
                    task_time = datetime.fromisoformat(task["scheduled_time"])
                    if now <= task_time <= end_time:
                        upcoming_items.append({
                            "type": "task",
                            "name": task["name"],
                            "time": task_time.isoformat(),
                            "priority": task["priority"]
                        })
            
            # Add events
            for event in self.calendar_events.values():
                event_time = datetime.fromisoformat(event["start_time"])
                if now <= event_time <= end_time:
                    upcoming_items.append({
                        "type": "event",
                        "name": event["title"],
                        "time": event_time.isoformat(),
                        "duration": (datetime.fromisoformat(event["end_time"]) - event_time).total_seconds() / 60
                    })
            
            # Sort by time
            upcoming_items.sort(key=lambda x: x["time"])
            
            return {
                "success": True,
                "upcoming_items": upcoming_items[:20],  # Limit to 20 items
                "total_items": len(upcoming_items),
                "date_range": days_ahead
            }
            
        except Exception as e:
            self.logger.error(f"Error getting upcoming events: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_deadline_report(self, parameters: Dict) -> Dict:
        """Get deadline status report"""
        try:
            active_deadlines = [d for d in self.deadlines.values() if d["status"] == "active"]
            
            # Categorize by urgency
            now = datetime.now()
            urgent = []  # < 24 hours
            soon = []    # < 7 days
            upcoming = [] # > 7 days
            
            for deadline in active_deadlines:
                deadline_time = datetime.fromisoformat(deadline["deadline"])
                time_until = deadline_time - now
                
                if time_until.total_seconds() < 24 * 3600:
                    urgent.append(deadline)
                elif time_until.total_seconds() < 7 * 24 * 3600:
                    soon.append(deadline)
                else:
                    upcoming.append(deadline)
            
            return {
                "success": True,
                "total_deadlines": len(active_deadlines),
                "urgent": len(urgent),
                "soon": len(soon),
                "upcoming": len(upcoming),
                "urgent_deadlines": [{"name": d["name"], "deadline": d["deadline"]} for d in urgent]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting deadline report: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_time_analysis(self, parameters: Dict) -> Dict:
        """Get time usage analysis"""
        try:
            days = parameters.get("days", 7)
            analysis = await self._analyze_schedule_efficiency(days)
            
            return {
                "success": True,
                "time_analysis": analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error getting time analysis: {e}")
            return {"error": str(e), "success": False}
    
    async def shutdown(self):
        """Shutdown ATLAS agent"""
        self.logger.info("Shutting down ATLAS agent...")
        
        # Save scheduling data
        try:
            with open("schedules/atlas_tasks.json", "w") as f:
                json.dump(self.scheduled_tasks, f, indent=2)
            
            with open("calendar_data/atlas_events.json", "w") as f:
                json.dump(self.calendar_events, f, indent=2)
            
            with open("schedules/atlas_deadlines.json", "w") as f:
                json.dump(self.deadlines, f, indent=2)
            
            with open("schedules/atlas_reminders.json", "w") as f:
                json.dump(self.reminders, f, indent=2)
                
            self.logger.info("Scheduling data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving scheduling data: {e}")

# Create ATLAS agent instance
atlas_agent = AtlasAgent()

