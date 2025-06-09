"""
SYNAPSE Agent - Knowledge Processing and Integration
==================================================

Specialized agent for knowledge ingestion, processing, and integration.
Handles PDF parsing, web content analysis, and knowledge graph construction.
"""

import asyncio
import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io

from agent_framework import BaseAgent, AgentMessage, MessageType, AgentCapability

class SynapseAgent(BaseAgent):
    """Knowledge processing agent for document analysis and information extraction"""
    
    def __init__(self):
        super().__init__(
            agent_id="synapse",
            name="SYNAPSE",
            description="Knowledge processing and integration agent"
        )
        
        # Knowledge processing capabilities
        self.add_capability(AgentCapability(
            name="pdf_analysis",
            description="Extract and analyze content from PDF documents",
            input_types=["pdf_file", "pdf_url"],
            output_types=["structured_text", "metadata", "summary"],
            resource_requirements={"memory": "medium", "cpu": "low"},
            execution_time_estimate=10.0
        ))
        
        self.add_capability(AgentCapability(
            name="web_content_extraction",
            description="Extract and analyze web page content",
            input_types=["url", "html"],
            output_types=["structured_text", "metadata", "links"],
            resource_requirements={"network": "required", "cpu": "low"},
            execution_time_estimate=5.0
        ))
        
        self.add_capability(AgentCapability(
            name="knowledge_synthesis",
            description="Synthesize information from multiple sources",
            input_types=["text_documents", "metadata"],
            output_types=["knowledge_graph", "insights", "summary"],
            resource_requirements={"memory": "high", "cpu": "medium"},
            execution_time_estimate=30.0
        ))
        
        self.add_capability(AgentCapability(
            name="semantic_analysis",
            description="Perform semantic analysis and entity extraction",
            input_types=["text"],
            output_types=["entities", "relationships", "topics"],
            resource_requirements={"cpu": "medium"},
            execution_time_estimate=15.0
        ))
        
        # Knowledge storage
        self.knowledge_cache: Dict[str, Dict] = {}
        self.processed_documents: Dict[str, Dict] = {}
    
    async def initialize(self):
        """Initialize SYNAPSE agent resources"""
        self.logger.info("Initializing SYNAPSE knowledge processing systems...")
        
        # Initialize knowledge storage
        self.knowledge_cache = {}
        self.processed_documents = {}
        
        # Setup document processing directories
        os.makedirs("knowledge_cache", exist_ok=True)
        os.makedirs("processed_docs", exist_ok=True)
        
        self.logger.info("SYNAPSE initialization complete")
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages for knowledge operations"""
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
        
        if command == "process_pdf":
            result = await self._process_pdf(parameters)
        elif command == "extract_web_content":
            result = await self._extract_web_content(parameters)
        elif command == "synthesize_knowledge":
            result = await self._synthesize_knowledge(parameters)
        elif command == "analyze_semantics":
            result = await self._analyze_semantics(parameters)
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
        
        if query_type == "knowledge_search":
            result = await self._search_knowledge(message.payload)
        elif query_type == "document_status":
            result = await self._get_document_status(message.payload)
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
    
    async def _process_pdf(self, parameters: Dict) -> Dict:
        """Process PDF document and extract knowledge"""
        try:
            pdf_path = parameters.get("file_path")
            pdf_url = parameters.get("url")
            
            if not pdf_path and not pdf_url:
                return {"error": "No PDF path or URL provided", "success": False}
            
            # Download PDF if URL provided
            if pdf_url:
                pdf_content = await self._download_pdf(pdf_url)
                if not pdf_content:
                    return {"error": "Failed to download PDF", "success": False}
            else:
                with open(pdf_path, 'rb') as file:
                    pdf_content = file.read()
            
            # Extract text from PDF
            text_content = self._extract_pdf_text(pdf_content)
            
            # Generate document hash for caching
            doc_hash = hashlib.sha256(pdf_content).hexdigest()[:16]
            
            # Analyze content
            analysis = await self._analyze_document_content(text_content)
            
            # Store processed document
            document_info = {
                "hash": doc_hash,
                "source": pdf_url or pdf_path,
                "type": "pdf",
                "content": text_content,
                "analysis": analysis,
                "processed_at": datetime.now().isoformat(),
                "word_count": len(text_content.split()),
                "page_count": text_content.count("\\f") + 1  # Rough page count
            }
            
            self.processed_documents[doc_hash] = document_info
            
            # Cache knowledge
            self.knowledge_cache[doc_hash] = {
                "entities": analysis.get("entities", []),
                "topics": analysis.get("topics", []),
                "summary": analysis.get("summary", ""),
                "key_points": analysis.get("key_points", [])
            }
            
            self.logger.info(f"Processed PDF document: {doc_hash}")
            
            return {
                "success": True,
                "document_hash": doc_hash,
                "word_count": document_info["word_count"],
                "page_count": document_info["page_count"],
                "entities": analysis.get("entities", [])[:10],  # Top 10 entities
                "topics": analysis.get("topics", [])[:5],       # Top 5 topics
                "summary": analysis.get("summary", "")[:500]    # First 500 chars of summary
            }
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {e}")
            return {"error": str(e), "success": False}
    
    async def _download_pdf(self, url: str) -> Optional[bytes]:
        """Download PDF from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            if 'application/pdf' in response.headers.get('content-type', ''):
                return response.content
            else:
                self.logger.warning(f"URL does not point to PDF: {url}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading PDF: {e}")
            return None
    
    def _extract_pdf_text(self, pdf_content: bytes) -> str:
        """Extract text content from PDF bytes"""
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\\n\\n"
            
            return text_content.strip()
            
        except Exception as e:
            self.logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    async def _extract_web_content(self, parameters: Dict) -> Dict:
        """Extract content from web page"""
        try:
            url = parameters.get("url")
            if not url:
                return {"error": "No URL provided", "success": False}
            
            # Download web page
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text(separator=' ', strip=True)
            
            # Extract metadata
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title"
            
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ''
            
            # Extract links
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            
            # Analyze content
            analysis = await self._analyze_document_content(text_content)
            
            # Generate content hash
            content_hash = hashlib.sha256(text_content.encode()).hexdigest()[:16]
            
            # Store processed content
            document_info = {
                "hash": content_hash,
                "source": url,
                "type": "web_page",
                "title": title_text,
                "description": description,
                "content": text_content,
                "links": links[:50],  # Limit to first 50 links
                "analysis": analysis,
                "processed_at": datetime.now().isoformat(),
                "word_count": len(text_content.split())
            }
            
            self.processed_documents[content_hash] = document_info
            
            self.logger.info(f"Processed web content: {url}")
            
            return {
                "success": True,
                "document_hash": content_hash,
                "title": title_text,
                "word_count": document_info["word_count"],
                "entities": analysis.get("entities", [])[:10],
                "topics": analysis.get("topics", [])[:5],
                "summary": analysis.get("summary", "")[:500]
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting web content: {e}")
            return {"error": str(e), "success": False}
    
    async def _analyze_document_content(self, text: str) -> Dict:
        """Analyze document content for entities, topics, and insights"""
        try:
            # Simple analysis - in production, would use NLP libraries
            words = text.lower().split()
            word_freq = {}
            
            # Count word frequencies
            for word in words:
                if len(word) > 3 and word.isalpha():
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Extract top topics (most frequent words)
            topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Simple entity extraction (capitalized words)
            entities = []
            for word in text.split():
                if word[0].isupper() and len(word) > 2 and word.isalpha():
                    entities.append(word)
            
            # Remove duplicates and limit
            entities = list(set(entities))[:20]
            
            # Generate simple summary (first few sentences)
            sentences = text.split('.')[:3]
            summary = '. '.join(sentences).strip()
            
            # Extract key points (sentences with important keywords)
            important_keywords = ['important', 'key', 'critical', 'significant', 'major', 'primary']
            key_points = []
            
            for sentence in text.split('.'):
                if any(keyword in sentence.lower() for keyword in important_keywords):
                    key_points.append(sentence.strip())
            
            return {
                "entities": entities,
                "topics": [topic[0] for topic in topics],
                "summary": summary,
                "key_points": key_points[:5],
                "word_count": len(words),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing content: {e}")
            return {}
    
    async def _synthesize_knowledge(self, parameters: Dict) -> Dict:
        """Synthesize knowledge from multiple sources"""
        try:
            document_hashes = parameters.get("document_hashes", [])
            
            if not document_hashes:
                return {"error": "No document hashes provided", "success": False}
            
            # Collect knowledge from specified documents
            all_entities = []
            all_topics = []
            all_summaries = []
            all_key_points = []
            
            for doc_hash in document_hashes:
                if doc_hash in self.knowledge_cache:
                    knowledge = self.knowledge_cache[doc_hash]
                    all_entities.extend(knowledge.get("entities", []))
                    all_topics.extend(knowledge.get("topics", []))
                    all_summaries.append(knowledge.get("summary", ""))
                    all_key_points.extend(knowledge.get("key_points", []))
            
            # Synthesize common themes
            entity_freq = {}
            for entity in all_entities:
                entity_freq[entity] = entity_freq.get(entity, 0) + 1
            
            topic_freq = {}
            for topic in all_topics:
                topic_freq[topic] = topic_freq.get(topic, 0) + 1
            
            # Get most common entities and topics
            common_entities = sorted(entity_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            common_topics = sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Create synthesis
            synthesis = {
                "common_entities": [entity for entity, count in common_entities],
                "common_topics": [topic for topic, count in common_topics],
                "document_count": len(document_hashes),
                "total_key_points": len(all_key_points),
                "synthesis_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Synthesized knowledge from {len(document_hashes)} documents")
            
            return {
                "success": True,
                "synthesis": synthesis
            }
            
        except Exception as e:
            self.logger.error(f"Error synthesizing knowledge: {e}")
            return {"error": str(e), "success": False}
    
    async def _analyze_semantics(self, parameters: Dict) -> Dict:
        """Perform semantic analysis on text"""
        try:
            text = parameters.get("text", "")
            if not text:
                return {"error": "No text provided", "success": False}
            
            # Simple semantic analysis
            analysis = await self._analyze_document_content(text)
            
            return {
                "success": True,
                "semantic_analysis": analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error in semantic analysis: {e}")
            return {"error": str(e), "success": False}
    
    async def _search_knowledge(self, parameters: Dict) -> Dict:
        """Search processed knowledge"""
        try:
            query = parameters.get("query", "").lower()
            
            if not query:
                return {"error": "No search query provided", "success": False}
            
            results = []
            
            for doc_hash, knowledge in self.knowledge_cache.items():
                score = 0
                
                # Check entities
                for entity in knowledge.get("entities", []):
                    if query in entity.lower():
                        score += 2
                
                # Check topics
                for topic in knowledge.get("topics", []):
                    if query in topic.lower():
                        score += 1
                
                # Check summary
                if query in knowledge.get("summary", "").lower():
                    score += 1
                
                if score > 0:
                    doc_info = self.processed_documents.get(doc_hash, {})
                    results.append({
                        "document_hash": doc_hash,
                        "source": doc_info.get("source", "Unknown"),
                        "title": doc_info.get("title", "No title"),
                        "score": score,
                        "summary": knowledge.get("summary", "")[:200]
                    })
            
            # Sort by relevance score
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return {
                "success": True,
                "results": results[:10],  # Top 10 results
                "total_found": len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Error searching knowledge: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_document_status(self, parameters: Dict) -> Dict:
        """Get status of processed documents"""
        try:
            return {
                "success": True,
                "total_documents": len(self.processed_documents),
                "knowledge_entries": len(self.knowledge_cache),
                "document_types": {
                    "pdf": len([d for d in self.processed_documents.values() if d.get("type") == "pdf"]),
                    "web_page": len([d for d in self.processed_documents.values() if d.get("type") == "web_page"])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting document status: {e}")
            return {"error": str(e), "success": False}
    
    async def shutdown(self):
        """Shutdown SYNAPSE agent"""
        self.logger.info("Shutting down SYNAPSE agent...")
        
        # Save knowledge cache to disk
        try:
            with open("knowledge_cache/synapse_cache.json", "w") as f:
                json.dump(self.knowledge_cache, f, indent=2)
            
            with open("processed_docs/synapse_docs.json", "w") as f:
                json.dump(self.processed_documents, f, indent=2)
                
            self.logger.info("Knowledge cache saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving knowledge cache: {e}")

# Create SYNAPSE agent instance
synapse_agent = SynapseAgent()

