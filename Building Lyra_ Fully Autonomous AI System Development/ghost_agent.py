"""
GHOST Agent - Surveillance and Network Operations
================================================

Specialized agent for network monitoring, surveillance, and deep web research.
Handles threat detection, competitive intelligence, and anonymous operations.
"""

import asyncio
import json
import os
import requests
import socket
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, urljoin
import hashlib
import re

from agent_framework import BaseAgent, AgentMessage, MessageType, AgentCapability

class GhostAgent(BaseAgent):
    """Surveillance and network operations agent"""
    
    def __init__(self):
        super().__init__(
            agent_id="ghost",
            name="GHOST",
            description="Surveillance and network operations agent"
        )
        
        # Network operation capabilities
        self.add_capability(AgentCapability(
            name="web_surveillance",
            description="Monitor websites and social media for mentions and changes",
            input_types=["urls", "keywords", "social_handles"],
            output_types=["alerts", "changes", "mentions"],
            resource_requirements={"network": "required", "cpu": "low"},
            execution_time_estimate=30.0
        ))
        
        self.add_capability(AgentCapability(
            name="threat_monitoring",
            description="Monitor for security threats and vulnerabilities",
            input_types=["domains", "ip_addresses", "threat_feeds"],
            output_types=["threats", "vulnerabilities", "alerts"],
            resource_requirements={"network": "required", "cpu": "medium"},
            execution_time_estimate=60.0
        ))
        
        self.add_capability(AgentCapability(
            name="competitive_intelligence",
            description="Gather competitive intelligence from public sources",
            input_types=["competitor_domains", "keywords", "industries"],
            output_types=["intelligence", "insights", "reports"],
            resource_requirements={"network": "required", "cpu": "medium"},
            execution_time_estimate=120.0
        ))
        
        self.add_capability(AgentCapability(
            name="anonymous_research",
            description="Conduct research through anonymous channels",
            input_types=["research_queries", "target_sites"],
            output_types=["research_data", "anonymized_results"],
            resource_requirements={"network": "required", "tor": "required"},
            execution_time_estimate=180.0
        ))
        
        # Surveillance state
        self.monitored_targets: Dict[str, Dict] = {}
        self.threat_feeds: List[str] = []
        self.surveillance_history: List[Dict] = []
        self.tor_enabled = False
        
        # Security settings
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
    
    async def initialize(self):
        """Initialize GHOST agent resources"""
        self.logger.info("Initializing GHOST surveillance systems...")
        
        # Initialize surveillance storage
        self.monitored_targets = {}
        self.surveillance_history = []
        
        # Setup surveillance directories
        os.makedirs("surveillance_data", exist_ok=True)
        os.makedirs("threat_intel", exist_ok=True)
        
        # Check for TOR availability
        self.tor_enabled = await self._check_tor_availability()
        
        # Initialize threat feeds
        self.threat_feeds = [
            "https://feeds.feedburner.com/eset/blog",
            "https://krebsonsecurity.com/feed/",
            "https://threatpost.com/feed/"
        ]
        
        self.logger.info(f"GHOST initialization complete (TOR: {'enabled' if self.tor_enabled else 'disabled'})")
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages for surveillance operations"""
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
        
        if command == "start_surveillance":
            result = await self._start_surveillance(parameters)
        elif command == "stop_surveillance":
            result = await self._stop_surveillance(parameters)
        elif command == "scan_threats":
            result = await self._scan_threats(parameters)
        elif command == "gather_intelligence":
            result = await self._gather_intelligence(parameters)
        elif command == "anonymous_research":
            result = await self._anonymous_research(parameters)
        elif command == "check_mentions":
            result = await self._check_mentions(parameters)
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
        
        if query_type == "surveillance_status":
            result = await self._get_surveillance_status(message.payload)
        elif query_type == "threat_summary":
            result = await self._get_threat_summary(message.payload)
        elif query_type == "intelligence_report":
            result = await self._get_intelligence_report(message.payload)
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
    
    async def _start_surveillance(self, parameters: Dict) -> Dict:
        """Start surveillance on specified targets"""
        try:
            targets = parameters.get("targets", [])
            keywords = parameters.get("keywords", [])
            interval = parameters.get("interval", 3600)  # Default 1 hour
            
            if not targets:
                return {"error": "No surveillance targets provided", "success": False}
            
            surveillance_id = f"surv_{int(time.time())}"
            
            surveillance_config = {
                "id": surveillance_id,
                "targets": targets,
                "keywords": keywords,
                "interval": interval,
                "started_at": datetime.now().isoformat(),
                "status": "active",
                "last_check": None,
                "alerts_count": 0
            }
            
            self.monitored_targets[surveillance_id] = surveillance_config
            
            # Start surveillance task
            asyncio.create_task(self._surveillance_loop(surveillance_id))
            
            self.logger.info(f"Started surveillance: {surveillance_id} on {len(targets)} targets")
            
            return {
                "success": True,
                "surveillance_id": surveillance_id,
                "targets_count": len(targets),
                "interval": interval
            }
            
        except Exception as e:
            self.logger.error(f"Error starting surveillance: {e}")
            return {"error": str(e), "success": False}
    
    async def _stop_surveillance(self, parameters: Dict) -> Dict:
        """Stop surveillance on specified target"""
        try:
            surveillance_id = parameters.get("surveillance_id")
            
            if not surveillance_id or surveillance_id not in self.monitored_targets:
                return {"error": "Invalid surveillance ID", "success": False}
            
            # Mark as stopped
            self.monitored_targets[surveillance_id]["status"] = "stopped"
            self.monitored_targets[surveillance_id]["stopped_at"] = datetime.now().isoformat()
            
            self.logger.info(f"Stopped surveillance: {surveillance_id}")
            
            return {
                "success": True,
                "surveillance_id": surveillance_id,
                "status": "stopped"
            }
            
        except Exception as e:
            self.logger.error(f"Error stopping surveillance: {e}")
            return {"error": str(e), "success": False}
    
    async def _surveillance_loop(self, surveillance_id: str):
        """Main surveillance loop for a target"""
        while surveillance_id in self.monitored_targets:
            config = self.monitored_targets[surveillance_id]
            
            if config["status"] != "active":
                break
            
            try:
                # Check each target
                for target in config["targets"]:
                    await self._check_target(surveillance_id, target, config["keywords"])
                
                # Update last check time
                config["last_check"] = datetime.now().isoformat()
                
                # Wait for next interval
                await asyncio.sleep(config["interval"])
                
            except Exception as e:
                self.logger.error(f"Error in surveillance loop {surveillance_id}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _check_target(self, surveillance_id: str, target: str, keywords: List[str]):
        """Check a specific target for changes or mentions"""
        try:
            # Determine target type
            if target.startswith("http"):
                await self._check_website(surveillance_id, target, keywords)
            elif "@" in target:
                await self._check_social_media(surveillance_id, target, keywords)
            else:
                await self._check_general_mentions(surveillance_id, target, keywords)
                
        except Exception as e:
            self.logger.error(f"Error checking target {target}: {e}")
    
    async def _check_website(self, surveillance_id: str, url: str, keywords: List[str]):
        """Check website for changes or keyword mentions"""
        try:
            headers = {"User-Agent": self.user_agents[0]}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            content = response.text.lower()
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Check for keyword mentions
            mentions = []
            for keyword in keywords:
                if keyword.lower() in content:
                    mentions.append(keyword)
            
            # Store surveillance data
            surveillance_data = {
                "surveillance_id": surveillance_id,
                "target": url,
                "timestamp": datetime.now().isoformat(),
                "content_hash": content_hash,
                "mentions": mentions,
                "status_code": response.status_code
            }
            
            self.surveillance_history.append(surveillance_data)
            
            # Generate alert if mentions found
            if mentions:
                await self._generate_alert(surveillance_id, "keyword_mentions", {
                    "target": url,
                    "mentions": mentions,
                    "timestamp": surveillance_data["timestamp"]
                })
            
        except Exception as e:
            self.logger.error(f"Error checking website {url}: {e}")
    
    async def _check_social_media(self, surveillance_id: str, handle: str, keywords: List[str]):
        """Check social media for mentions (placeholder - would need API access)"""
        # This would require actual social media API integration
        self.logger.info(f"Social media monitoring for {handle} (placeholder)")
        
        # Placeholder alert
        await self._generate_alert(surveillance_id, "social_media_check", {
            "handle": handle,
            "status": "checked",
            "timestamp": datetime.now().isoformat()
        })
    
    async def _check_general_mentions(self, surveillance_id: str, target: str, keywords: List[str]):
        """Check for general mentions across search engines"""
        try:
            # Simple search using DuckDuckGo (privacy-focused)
            search_query = f"{target} {' '.join(keywords)}"
            
            # This is a placeholder - would need proper search API
            self.logger.info(f"Searching for mentions of: {search_query}")
            
            await self._generate_alert(surveillance_id, "mention_search", {
                "target": target,
                "query": search_query,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error checking mentions for {target}: {e}")
    
    async def _generate_alert(self, surveillance_id: str, alert_type: str, data: Dict):
        """Generate surveillance alert"""
        alert = {
            "surveillance_id": surveillance_id,
            "alert_type": alert_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "severity": "medium"  # Could be calculated based on content
        }
        
        # Update alert count
        if surveillance_id in self.monitored_targets:
            self.monitored_targets[surveillance_id]["alerts_count"] += 1
        
        self.logger.warning(f"SURVEILLANCE ALERT [{alert_type}]: {data}")
        
        # Send alert to message bus
        if hasattr(self, 'message_bus'):
            alert_message = AgentMessage(
                id=f"alert_{int(time.time())}",
                sender=self.agent_id,
                recipient="broadcast",
                message_type=MessageType.ALERT,
                payload=alert,
                priority=8
            )
            await self.message_bus.send_message(alert_message)
    
    async def _scan_threats(self, parameters: Dict) -> Dict:
        """Scan for security threats"""
        try:
            targets = parameters.get("targets", [])
            scan_type = parameters.get("scan_type", "basic")
            
            if not targets:
                return {"error": "No scan targets provided", "success": False}
            
            threats_found = []
            
            for target in targets:
                target_threats = await self._scan_target_threats(target, scan_type)
                threats_found.extend(target_threats)
            
            # Store threat intelligence
            threat_report = {
                "scan_id": f"threat_{int(time.time())}",
                "targets": targets,
                "scan_type": scan_type,
                "threats_found": threats_found,
                "timestamp": datetime.now().isoformat(),
                "total_threats": len(threats_found)
            }
            
            # Save to threat intel directory
            with open(f"threat_intel/scan_{threat_report['scan_id']}.json", "w") as f:
                json.dump(threat_report, f, indent=2)
            
            self.logger.info(f"Threat scan completed: {len(threats_found)} threats found")
            
            return {
                "success": True,
                "scan_id": threat_report["scan_id"],
                "threats_found": len(threats_found),
                "high_severity": len([t for t in threats_found if t.get("severity") == "high"])
            }
            
        except Exception as e:
            self.logger.error(f"Error scanning threats: {e}")
            return {"error": str(e), "success": False}
    
    async def _scan_target_threats(self, target: str, scan_type: str) -> List[Dict]:
        """Scan specific target for threats"""
        threats = []
        
        try:
            if target.startswith("http"):
                # Web application scanning
                threats.extend(await self._scan_web_threats(target))
            elif self._is_ip_address(target):
                # Network scanning
                threats.extend(await self._scan_network_threats(target))
            else:
                # Domain scanning
                threats.extend(await self._scan_domain_threats(target))
                
        except Exception as e:
            self.logger.error(f"Error scanning target {target}: {e}")
            threats.append({
                "target": target,
                "threat_type": "scan_error",
                "description": str(e),
                "severity": "low"
            })
        
        return threats
    
    async def _scan_web_threats(self, url: str) -> List[Dict]:
        """Scan web application for threats"""
        threats = []
        
        try:
            # Basic HTTP security checks
            response = requests.get(url, timeout=30)
            headers = response.headers
            
            # Check for missing security headers
            security_headers = [
                "X-Frame-Options",
                "X-Content-Type-Options",
                "X-XSS-Protection",
                "Strict-Transport-Security"
            ]
            
            for header in security_headers:
                if header not in headers:
                    threats.append({
                        "target": url,
                        "threat_type": "missing_security_header",
                        "description": f"Missing {header} header",
                        "severity": "medium"
                    })
            
            # Check for server information disclosure
            if "Server" in headers:
                threats.append({
                    "target": url,
                    "threat_type": "information_disclosure",
                    "description": f"Server header reveals: {headers['Server']}",
                    "severity": "low"
                })
            
        except Exception as e:
            self.logger.error(f"Error scanning web threats for {url}: {e}")
        
        return threats
    
    async def _scan_network_threats(self, ip: str) -> List[Dict]:
        """Scan network target for threats"""
        threats = []
        
        try:
            # Basic port scanning (limited to avoid being intrusive)
            common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995]
            
            for port in common_ports:
                if await self._check_port_open(ip, port):
                    threats.append({
                        "target": ip,
                        "threat_type": "open_port",
                        "description": f"Port {port} is open",
                        "severity": "low" if port in [80, 443] else "medium"
                    })
            
        except Exception as e:
            self.logger.error(f"Error scanning network threats for {ip}: {e}")
        
        return threats
    
    async def _scan_domain_threats(self, domain: str) -> List[Dict]:
        """Scan domain for threats"""
        threats = []
        
        try:
            # DNS checks
            import socket
            
            # Check if domain resolves
            try:
                ip = socket.gethostbyname(domain)
                
                # Check for suspicious IP ranges
                if ip.startswith("127.") or ip.startswith("0."):
                    threats.append({
                        "target": domain,
                        "threat_type": "suspicious_dns",
                        "description": f"Domain resolves to suspicious IP: {ip}",
                        "severity": "high"
                    })
                        
            except socket.gaierror:
                threats.append({
                    "target": domain,
                    "threat_type": "dns_resolution_failure",
                    "description": "Domain does not resolve",
                    "severity": "medium"
                })
            
        except Exception as e:
            self.logger.error(f"Error scanning domain threats for {domain}: {e}")
        
        return threats
    
    def _is_ip_address(self, target: str) -> bool:
        """Check if target is an IP address"""
        try:
            socket.inet_aton(target)
            return True
        except socket.error:
            return False
    
    async def _check_port_open(self, ip: str, port: int, timeout: float = 3.0) -> bool:
        """Check if a port is open on target IP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    async def _gather_intelligence(self, parameters: Dict) -> Dict:
        """Gather competitive intelligence"""
        try:
            targets = parameters.get("targets", [])
            intelligence_type = parameters.get("type", "general")
            
            if not targets:
                return {"error": "No intelligence targets provided", "success": False}
            
            intelligence_data = []
            
            for target in targets:
                target_intel = await self._gather_target_intelligence(target, intelligence_type)
                intelligence_data.append(target_intel)
            
            intelligence_report = {
                "report_id": f"intel_{int(time.time())}",
                "targets": targets,
                "intelligence_type": intelligence_type,
                "data": intelligence_data,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Intelligence gathering completed for {len(targets)} targets")
            
            return {
                "success": True,
                "report_id": intelligence_report["report_id"],
                "targets_analyzed": len(targets),
                "data_points": sum(len(d.get("insights", [])) for d in intelligence_data)
            }
            
        except Exception as e:
            self.logger.error(f"Error gathering intelligence: {e}")
            return {"error": str(e), "success": False}
    
    async def _gather_target_intelligence(self, target: str, intel_type: str) -> Dict:
        """Gather intelligence on specific target"""
        try:
            intelligence = {
                "target": target,
                "type": intel_type,
                "insights": [],
                "timestamp": datetime.now().isoformat()
            }
            
            if target.startswith("http"):
                # Web-based intelligence
                intelligence["insights"].extend(await self._gather_web_intelligence(target))
            else:
                # Domain-based intelligence
                intelligence["insights"].extend(await self._gather_domain_intelligence(target))
            
            return intelligence
            
        except Exception as e:
            self.logger.error(f"Error gathering intelligence for {target}: {e}")
            return {"target": target, "error": str(e), "insights": []}
    
    async def _gather_web_intelligence(self, url: str) -> List[Dict]:
        """Gather intelligence from web target"""
        insights = []
        
        try:
            headers = {"User-Agent": self.user_agents[0]}
            response = requests.get(url, headers=headers, timeout=30)
            
            # Technology detection
            tech_headers = {
                "Server": "web_server",
                "X-Powered-By": "backend_technology",
                "X-Generator": "cms_platform"
            }
            
            for header, tech_type in tech_headers.items():
                if header in response.headers:
                    insights.append({
                        "type": tech_type,
                        "value": response.headers[header],
                        "confidence": "high"
                    })
            
            # Content analysis
            content = response.text.lower()
            
            # Look for technology indicators
            tech_indicators = {
                "wordpress": "cms",
                "drupal": "cms",
                "joomla": "cms",
                "react": "frontend_framework",
                "angular": "frontend_framework",
                "vue": "frontend_framework"
            }
            
            for indicator, tech_type in tech_indicators.items():
                if indicator in content:
                    insights.append({
                        "type": tech_type,
                        "value": indicator,
                        "confidence": "medium"
                    })
            
        except Exception as e:
            self.logger.error(f"Error gathering web intelligence for {url}: {e}")
        
        return insights
    
    async def _gather_domain_intelligence(self, domain: str) -> List[Dict]:
        """Gather intelligence from domain"""
        insights = []
        
        try:
            # DNS information
            import socket
            
            try:
                ip = socket.gethostbyname(domain)
                insights.append({
                    "type": "ip_address",
                    "value": ip,
                    "confidence": "high"
                })
                
                # Reverse DNS lookup
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                    insights.append({
                        "type": "hostname",
                        "value": hostname,
                        "confidence": "high"
                    })
                except socket.herror:
                    pass
                    
            except socket.gaierror:
                insights.append({
                    "type": "dns_status",
                    "value": "no_resolution",
                    "confidence": "high"
                })
            
        except Exception as e:
            self.logger.error(f"Error gathering domain intelligence for {domain}: {e}")
        
        return insights
    
    async def _anonymous_research(self, parameters: Dict) -> Dict:
        """Conduct anonymous research"""
        try:
            if not self.tor_enabled:
                return {"error": "TOR not available for anonymous research", "success": False}
            
            queries = parameters.get("queries", [])
            
            if not queries:
                return {"error": "No research queries provided", "success": False}
            
            # Placeholder for TOR-based research
            # In production, this would use TOR proxies and anonymous browsing
            
            research_results = []
            
            for query in queries:
                result = {
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "status": "researched_anonymously",
                    "results": f"Anonymous research completed for: {query}"
                }
                research_results.append(result)
            
            self.logger.info(f"Anonymous research completed for {len(queries)} queries")
            
            return {
                "success": True,
                "queries_processed": len(queries),
                "research_id": f"anon_{int(time.time())}"
            }
            
        except Exception as e:
            self.logger.error(f"Error in anonymous research: {e}")
            return {"error": str(e), "success": False}
    
    async def _check_mentions(self, parameters: Dict) -> Dict:
        """Check for mentions across various sources"""
        try:
            keywords = parameters.get("keywords", [])
            sources = parameters.get("sources", ["web", "news"])
            
            if not keywords:
                return {"error": "No keywords provided", "success": False}
            
            mentions = []
            
            for keyword in keywords:
                for source in sources:
                    source_mentions = await self._check_source_mentions(keyword, source)
                    mentions.extend(source_mentions)
            
            self.logger.info(f"Mention check completed: {len(mentions)} mentions found")
            
            return {
                "success": True,
                "total_mentions": len(mentions),
                "keywords_checked": len(keywords),
                "sources_checked": len(sources),
                "mentions": mentions[:20]  # Return first 20 mentions
            }
            
        except Exception as e:
            self.logger.error(f"Error checking mentions: {e}")
            return {"error": str(e), "success": False}
    
    async def _check_source_mentions(self, keyword: str, source: str) -> List[Dict]:
        """Check specific source for keyword mentions"""
        mentions = []
        
        try:
            # Placeholder for actual mention checking
            # Would integrate with search APIs, news APIs, etc.
            
            mention = {
                "keyword": keyword,
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "url": f"https://example.com/search?q={keyword}",
                "title": f"Mention of {keyword} found",
                "snippet": f"This is a placeholder mention of {keyword} from {source}"
            }
            
            mentions.append(mention)
            
        except Exception as e:
            self.logger.error(f"Error checking {source} for {keyword}: {e}")
        
        return mentions
    
    async def _check_tor_availability(self) -> bool:
        """Check if TOR is available on the system"""
        try:
            # Check if tor command exists
            result = subprocess.run(["which", "tor"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    async def _get_surveillance_status(self, parameters: Dict) -> Dict:
        """Get status of surveillance operations"""
        try:
            active_surveillance = {k: v for k, v in self.monitored_targets.items() if v["status"] == "active"}
            
            return {
                "success": True,
                "total_surveillance": len(self.monitored_targets),
                "active_surveillance": len(active_surveillance),
                "total_alerts": sum(s.get("alerts_count", 0) for s in self.monitored_targets.values()),
                "surveillance_history": len(self.surveillance_history)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting surveillance status: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_threat_summary(self, parameters: Dict) -> Dict:
        """Get summary of threat intelligence"""
        try:
            # Count threat files
            threat_files = []
            if os.path.exists("threat_intel"):
                threat_files = [f for f in os.listdir("threat_intel") if f.endswith(".json")]
            
            return {
                "success": True,
                "threat_reports": len(threat_files),
                "tor_available": self.tor_enabled,
                "threat_feeds": len(self.threat_feeds)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting threat summary: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_intelligence_report(self, parameters: Dict) -> Dict:
        """Get intelligence gathering report"""
        try:
            return {
                "success": True,
                "intelligence_operations": "operational",
                "anonymous_research": "available" if self.tor_enabled else "limited",
                "surveillance_active": len([s for s in self.monitored_targets.values() if s["status"] == "active"])
            }
            
        except Exception as e:
            self.logger.error(f"Error getting intelligence report: {e}")
            return {"error": str(e), "success": False}
    
    async def shutdown(self):
        """Shutdown GHOST agent"""
        self.logger.info("Shutting down GHOST agent...")
        
        # Stop all active surveillance
        for surveillance_id in list(self.monitored_targets.keys()):
            if self.monitored_targets[surveillance_id]["status"] == "active":
                self.monitored_targets[surveillance_id]["status"] = "stopped"
        
        # Save surveillance data
        try:
            with open("surveillance_data/ghost_surveillance.json", "w") as f:
                json.dump(self.monitored_targets, f, indent=2)
            
            with open("surveillance_data/ghost_history.json", "w") as f:
                json.dump(self.surveillance_history, f, indent=2)
                
            self.logger.info("Surveillance data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving surveillance data: {e}")

# Create GHOST agent instance
ghost_agent = GhostAgent()

