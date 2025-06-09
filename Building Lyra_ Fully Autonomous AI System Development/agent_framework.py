"""
Lyra Multi-Agent Architecture
============================

Core framework for the multi-agent system supporting SYNAPSE, GHOST, and ATLAS agents.
Provides communication, coordination, and management capabilities for autonomous operation.
"""

import asyncio
import json
import uuid
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import logging
from concurrent.futures import ThreadPoolExecutor

class MessageType(Enum):
    COMMAND = "command"
    QUERY = "query"
    RESPONSE = "response"
    ALERT = "alert"
    BROADCAST = "broadcast"
    HEARTBEAT = "heartbeat"

class AgentStatus(Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    BUSY = "busy"
    IDLE = "idle"
    ERROR = "error"
    SHUTDOWN = "shutdown"

@dataclass
class AgentMessage:
    """Inter-agent communication message"""
    id: str
    sender: str
    recipient: str
    message_type: MessageType
    payload: Dict[str, Any]
    priority: int = 5  # 1-10 scale
    timestamp: str = None
    correlation_id: Optional[str] = None
    expires_at: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.id is None:
            self.id = f"msg_{uuid.uuid4().hex[:12]}"

@dataclass
class AgentCapability:
    """Defines an agent's capability"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    resource_requirements: Dict[str, Any]
    execution_time_estimate: float  # seconds

class BaseAgent(ABC):
    """Base class for all Lyra agents"""
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.status = AgentStatus.INITIALIZING
        self.capabilities: Dict[str, AgentCapability] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.response_handlers: Dict[str, Callable] = {}
        self.running = False
        self.last_heartbeat = datetime.now()
        
        # Performance metrics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.average_response_time = 0.0
        self.resource_usage = {"cpu": 0.0, "memory": 0.0}
        
        # Setup logging
        self.logger = logging.getLogger(f"lyra.agent.{agent_id}")
        
    @abstractmethod
    async def initialize(self):
        """Initialize agent-specific resources"""
        pass
    
    @abstractmethod
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming message and return response if needed"""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """Clean shutdown of agent resources"""
        pass
    
    def add_capability(self, capability: AgentCapability):
        """Add a capability to this agent"""
        self.capabilities[capability.name] = capability
        self.logger.info(f"Added capability: {capability.name}")
    
    async def start(self):
        """Start the agent's main processing loop"""
        self.running = True
        self.status = AgentStatus.ACTIVE
        
        await self.initialize()
        
        # Start message processing loop
        asyncio.create_task(self._message_loop())
        asyncio.create_task(self._heartbeat_loop())
        
        self.logger.info(f"Agent {self.name} started successfully")
    
    async def stop(self):
        """Stop the agent"""
        self.running = False
        self.status = AgentStatus.SHUTDOWN
        await self.shutdown()
        self.logger.info(f"Agent {self.name} stopped")
    
    async def _message_loop(self):
        """Main message processing loop"""
        while self.running:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                start_time = time.time()
                self.status = AgentStatus.BUSY
                
                # Process the message
                response = await self.process_message(message)
                
                # Send response if generated
                if response and hasattr(self, 'message_bus'):
                    await self.message_bus.send_message(response)
                
                # Update metrics
                processing_time = time.time() - start_time
                self.tasks_completed += 1
                self.average_response_time = (
                    (self.average_response_time * (self.tasks_completed - 1) + processing_time) 
                    / self.tasks_completed
                )
                
                self.status = AgentStatus.IDLE
                
            except asyncio.TimeoutError:
                # No message received, continue loop
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
                self.tasks_failed += 1
                self.status = AgentStatus.ERROR
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        while self.running:
            self.last_heartbeat = datetime.now()
            
            if hasattr(self, 'message_bus'):
                heartbeat = AgentMessage(
                    id=f"hb_{uuid.uuid4().hex[:8]}",
                    sender=self.agent_id,
                    recipient="system",
                    message_type=MessageType.HEARTBEAT,
                    payload={
                        "status": self.status.value,
                        "tasks_completed": self.tasks_completed,
                        "tasks_failed": self.tasks_failed,
                        "average_response_time": self.average_response_time,
                        "capabilities": list(self.capabilities.keys())
                    }
                )
                await self.message_bus.send_message(heartbeat)
            
            await asyncio.sleep(30)  # Heartbeat every 30 seconds

class MessageBus:
    """Central message bus for inter-agent communication"""
    
    def __init__(self, db_path: str = "lyra_messages.db"):
        self.db_path = db_path
        self.agents: Dict[str, BaseAgent] = {}
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.running = False
        self._init_database()
        
        # Setup logging
        self.logger = logging.getLogger("lyra.messagebus")
    
    def _init_database(self):
        """Initialize message storage database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                message_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                priority INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                correlation_id TEXT,
                expires_at TEXT,
                processed BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the message bus"""
        self.agents[agent.agent_id] = agent
        agent.message_bus = self
        self.logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the message bus"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent: {agent_id}")
    
    async def send_message(self, message: AgentMessage):
        """Send message to target agent(s)"""
        # Store message in database
        self._store_message(message)
        
        if message.recipient == "broadcast":
            # Send to all agents except sender
            for agent_id, agent in self.agents.items():
                if agent_id != message.sender:
                    await agent.message_queue.put(message)
        elif message.recipient in self.agents:
            # Send to specific agent
            target_agent = self.agents[message.recipient]
            await target_agent.message_queue.put(message)
        else:
            self.logger.warning(f"Unknown recipient: {message.recipient}")
    
    def _store_message(self, message: AgentMessage):
        """Store message in database for audit trail"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message.id,
            message.sender,
            message.recipient,
            message.message_type.value,
            json.dumps(message.payload),
            message.priority,
            message.timestamp,
            message.correlation_id,
            message.expires_at,
            False
        ))
        
        conn.commit()
        conn.close()
    
    async def query_agent(self, target_agent: str, query_type: str, payload: Dict, timeout: float = 30.0) -> Optional[Dict]:
        """Send query to agent and wait for response"""
        correlation_id = f"query_{uuid.uuid4().hex[:12]}"
        
        query_message = AgentMessage(
            id=f"q_{uuid.uuid4().hex[:12]}",
            sender="system",
            recipient=target_agent,
            message_type=MessageType.QUERY,
            payload={"query_type": query_type, **payload},
            correlation_id=correlation_id
        )
        
        # Setup response handler
        response_future = asyncio.Future()
        self.response_handlers[correlation_id] = response_future
        
        # Send query
        await self.send_message(query_message)
        
        try:
            # Wait for response
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response.payload
        except asyncio.TimeoutError:
            self.logger.warning(f"Query to {target_agent} timed out")
            return None
        finally:
            # Cleanup response handler
            if correlation_id in self.response_handlers:
                del self.response_handlers[correlation_id]

class AgentManager:
    """Manages the lifecycle and coordination of all agents"""
    
    def __init__(self):
        self.message_bus = MessageBus()
        self.agents: Dict[str, BaseAgent] = {}
        self.running = False
        
        # Setup logging
        self.logger = logging.getLogger("lyra.agentmanager")
    
    def register_agent(self, agent: BaseAgent):
        """Register and start an agent"""
        self.agents[agent.agent_id] = agent
        self.message_bus.register_agent(agent)
    
    async def start_all_agents(self):
        """Start all registered agents"""
        self.running = True
        
        for agent in self.agents.values():
            await agent.start()
        
        self.logger.info("All agents started successfully")
    
    async def stop_all_agents(self):
        """Stop all agents gracefully"""
        self.running = False
        
        for agent in self.agents.values():
            await agent.stop()
        
        self.logger.info("All agents stopped")
    
    def get_agent_status(self) -> Dict[str, Dict]:
        """Get status of all agents"""
        status = {}
        for agent_id, agent in self.agents.items():
            status[agent_id] = {
                "name": agent.name,
                "status": agent.status.value,
                "tasks_completed": agent.tasks_completed,
                "tasks_failed": agent.tasks_failed,
                "average_response_time": agent.average_response_time,
                "last_heartbeat": agent.last_heartbeat.isoformat(),
                "capabilities": list(agent.capabilities.keys())
            }
        return status
    
    async def broadcast_message(self, message_type: MessageType, payload: Dict, priority: int = 5):
        """Broadcast message to all agents"""
        message = AgentMessage(
            id=f"bc_{uuid.uuid4().hex[:12]}",
            sender="system",
            recipient="broadcast",
            message_type=message_type,
            payload=payload,
            priority=priority
        )
        
        await self.message_bus.send_message(message)
    
    async def send_command(self, target_agent: str, command: str, parameters: Dict = None) -> bool:
        """Send command to specific agent"""
        if target_agent not in self.agents:
            return False
        
        message = AgentMessage(
            id=f"cmd_{uuid.uuid4().hex[:12]}",
            sender="system",
            recipient=target_agent,
            message_type=MessageType.COMMAND,
            payload={"command": command, "parameters": parameters or {}}
        )
        
        await self.message_bus.send_message(message)
        return True
    
    def get_agents_by_capability(self, capability_name: str) -> List[str]:
        """Get list of agent IDs that have a specific capability"""
        capable_agents = []
        for agent_id, agent in self.agents.items():
            if capability_name in agent.capabilities:
                capable_agents.append(agent_id)
        return capable_agents
    
    async def distribute_task(self, task_type: str, task_data: Dict, required_capability: str = None) -> Optional[str]:
        """Distribute task to most suitable agent"""
        if required_capability:
            candidate_agents = self.get_agents_by_capability(required_capability)
        else:
            candidate_agents = list(self.agents.keys())
        
        if not candidate_agents:
            self.logger.warning(f"No agents available for task type: {task_type}")
            return None
        
        # Simple load balancing - choose agent with lowest task count
        best_agent = min(candidate_agents, key=lambda aid: self.agents[aid].tasks_completed)
        
        # Send task as command
        await self.send_command(best_agent, task_type, task_data)
        
        return best_agent

# Global agent manager instance
lyra_agent_manager = AgentManager()

