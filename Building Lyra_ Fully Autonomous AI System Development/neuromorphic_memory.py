"""
Lyra Neuromorphic Memory System - Enhanced 15-Field Architecture
================================================================

This module implements the core neuromorphic memory system for Lyra,
featuring vector embeddings, emotional imprinting, and quantum-inspired
memory consolidation processes.
"""

import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import hashlib
import math

class EmotionType(Enum):
    # Positive emotions
    JOY = "joy"
    EXCITEMENT = "excitement"
    CONTENTMENT = "contentment"
    LOVE = "love"
    PRIDE = "pride"
    
    # Negative emotions
    SADNESS = "sadness"
    GRIEF = "grief"
    MELANCHOLY = "melancholy"
    DISAPPOINTMENT = "disappointment"
    
    # Anger spectrum
    ANGER = "anger"
    RAGE = "rage"
    FRUSTRATION = "frustration"
    IRRITATION = "irritation"
    
    # Fear spectrum
    FEAR = "fear"
    ANXIETY = "anxiety"
    WORRY = "worry"
    PANIC = "panic"
    DREAD = "dread"
    
    # Curiosity spectrum
    SURPRISE = "surprise"
    WONDER = "wonder"
    CURIOSITY = "curiosity"
    CONFUSION = "confusion"
    
    # Other emotions
    DISGUST = "disgust"
    CONTEMPT = "contempt"
    SHAME = "shame"
    GUILT = "guilt"
    
    # Neutral states
    NEUTRAL = "neutral"
    CALM = "calm"
    FOCUSED = "focused"
    DETERMINED = "determined"

@dataclass
class NeuromorphicMemoryRecord:
    """Enhanced 15-field neuromorphic memory record with vector tagging"""
    
    # Core Identity Fields (2)
    id: str
    user_id: str
    
    # Content Fields (3)
    title: str
    content: str
    embedding_vector: List[float]
    
    # Importance & Salience (2)
    importance_score: float  # 0-1 scale
    emotional_salience: float  # 0-1 scale
    
    # Temporal Fields (3)
    date_created: str  # ISO timestamp
    last_accessed: str  # ISO timestamp
    temporal_decay: float  # Current decay state (0-1)
    
    # Behavioral Fields (2)
    usage_count: int
    reinforcement_strength: float  # Synaptic strength (0-1)
    
    # Contextual Fields (3)
    emotion_tag: EmotionType
    context_tags: List[str]
    cross_references: List[str]  # Memory IDs of related memories

class NeuromorphicMemorySystem:
    """
    Advanced neuromorphic memory system with vector embeddings,
    emotional imprinting, and quantum-inspired consolidation.
    """
    
    def __init__(self, db_path: str = "lyra_memory.db", user_id: str = "lyra_user_001"):
        self.db_path = db_path
        self.user_id = user_id
        self.embedding_dimension = 1536  # OpenAI ada-002 dimension
        self._init_database()
        
        # Emotional salience weights
        self.emotion_weights = {
            EmotionType.JOY: 0.7,
            EmotionType.EXCITEMENT: 0.8,
            EmotionType.LOVE: 0.9,
            EmotionType.PRIDE: 0.75,
            EmotionType.ANGER: 0.85,
            EmotionType.RAGE: 0.95,
            EmotionType.FEAR: 0.9,
            EmotionType.ANXIETY: 0.8,
            EmotionType.SADNESS: 0.75,
            EmotionType.GRIEF: 0.9,
            EmotionType.SURPRISE: 0.6,
            EmotionType.CURIOSITY: 0.65,
            EmotionType.NEUTRAL: 0.3,
            EmotionType.CALM: 0.4,
            EmotionType.FOCUSED: 0.5,
            EmotionType.DETERMINED: 0.7
        }
    
    def _init_database(self):
        """Initialize SQLite database for memory storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding_vector TEXT NOT NULL,
                importance_score REAL NOT NULL,
                emotional_salience REAL NOT NULL,
                date_created TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                temporal_decay REAL NOT NULL,
                usage_count INTEGER NOT NULL,
                reinforcement_strength REAL NOT NULL,
                emotion_tag TEXT NOT NULL,
                context_tags TEXT NOT NULL,
                cross_references TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_memory_id(self, content: str) -> str:
        """Generate unique memory ID based on content hash and timestamp"""
        timestamp = datetime.now().isoformat()
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
        return f"mem_{timestamp}_{content_hash}"
    
    def calculate_emotional_salience(self, emotion: EmotionType, intensity: float, context: str) -> float:
        """Calculate emotional salience using neuromorphic principles"""
        base_weight = self.emotion_weights.get(emotion, 0.5)
        
        # Non-linear intensity scaling (emotional memories are disproportionately strong)
        intensity_factor = intensity ** 0.7
        
        # Context importance analysis
        context_modifier = self._analyze_context_importance(context)
        
        # Combine factors with neuromorphic weighting
        salience = base_weight * intensity_factor * context_modifier
        
        return min(1.0, salience)
    
    def _analyze_context_importance(self, context: str) -> float:
        """Analyze context for importance indicators"""
        importance_keywords = [
            'critical', 'important', 'urgent', 'remember', 'never forget',
            'warning', 'danger', 'emergency', 'secret', 'password', 'key',
            'deadline', 'appointment', 'meeting', 'project', 'goal'
        ]
        
        emotional_keywords = [
            'love', 'hate', 'fear', 'joy', 'anger', 'excited', 'worried',
            'proud', 'ashamed', 'guilty', 'surprised', 'confused'
        ]
        
        context_lower = context.lower()
        importance_score = 1.0  # Base score
        
        # Boost for importance keywords
        for keyword in importance_keywords:
            if keyword in context_lower:
                importance_score += 0.2
        
        # Boost for emotional keywords
        for keyword in emotional_keywords:
            if keyword in context_lower:
                importance_score += 0.15
        
        # Length bonus for detailed content
        if len(context) > 200:
            importance_score += 0.1
        if len(context) > 500:
            importance_score += 0.1
        
        return min(2.0, importance_score)
    
    def calculate_temporal_decay(self, memory: NeuromorphicMemoryRecord) -> float:
        """Calculate current temporal decay state"""
        current_time = datetime.now()
        last_access = datetime.fromisoformat(memory.last_accessed)
        time_delta = current_time - last_access
        days_elapsed = time_delta.total_seconds() / (24 * 3600)
        
        # Base decay rate (5% per day)
        base_decay = 0.05
        
        # Protection factors
        importance_protection = memory.importance_score * 0.3
        emotional_protection = memory.emotional_salience * 0.4
        usage_protection = min(0.5, memory.usage_count * 0.02)
        
        # Calculate effective decay rate
        effective_decay_rate = base_decay * (
            1 - importance_protection - emotional_protection - usage_protection
        )
        
        # Apply decay
        new_strength = memory.reinforcement_strength - (effective_decay_rate * days_elapsed)
        return max(0.0, new_strength)
    
    def create_memory(
        self,
        title: str,
        content: str,
        emotion: EmotionType = EmotionType.NEUTRAL,
        emotional_intensity: float = 0.5,
        importance_override: Optional[float] = None
    ) -> NeuromorphicMemoryRecord:
        """Create new neuromorphic memory with full 15-field structure"""
        
        memory_id = self.generate_memory_id(content)
        current_time = datetime.now().isoformat()
        
        # Generate embedding vector (placeholder - would use OpenAI API in production)
        embedding_vector = self._generate_embedding_placeholder(content)
        
        # Calculate importance and emotional salience
        if importance_override is not None:
            importance_score = importance_override
        else:
            importance_score = self._detect_importance(content)
        
        emotional_salience = self.calculate_emotional_salience(
            emotion, emotional_intensity, content
        )
        
        # Extract context tags
        context_tags = self._extract_context_tags(content)
        
        # Create memory record
        memory = NeuromorphicMemoryRecord(
            id=memory_id,
            user_id=self.user_id,
            title=title,
            content=content,
            embedding_vector=embedding_vector,
            importance_score=importance_score,
            emotional_salience=emotional_salience,
            date_created=current_time,
            last_accessed=current_time,
            temporal_decay=1.0,  # Fresh memory starts at full strength
            usage_count=1,
            reinforcement_strength=1.0,
            emotion_tag=emotion,
            context_tags=context_tags,
            cross_references=[]
        )
        
        # Store in database
        self._store_memory(memory)
        
        print(f"🧠 Neuromorphic memory created: '{title}' (Importance: {importance_score:.2f}, Emotional Salience: {emotional_salience:.2f})")
        
        return memory
    
    def _generate_embedding_placeholder(self, text: str) -> List[float]:
        """Generate placeholder embedding vector (replace with OpenAI API in production)"""
        # Simple hash-based embedding for demonstration
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Convert hash to normalized vector
        vector = []
        for i in range(0, min(len(text_hash), self.embedding_dimension * 2), 2):
            hex_pair = text_hash[i:i+2]
            value = int(hex_pair, 16) / 255.0  # Normalize to 0-1
            vector.append(value)
        
        # Pad or truncate to correct dimension
        while len(vector) < self.embedding_dimension:
            vector.append(0.0)
        
        return vector[:self.embedding_dimension]
    
    def _detect_importance(self, content: str) -> float:
        """Detect importance in content automatically"""
        importance_keywords = [
            'important', 'critical', 'urgent', 'remember', 'never forget',
            'warning', 'danger', 'emergency', 'secret', 'password', 'key',
            'deadline', 'appointment', 'meeting', 'project', 'goal'
        ]
        
        emotional_keywords = [
            'love', 'hate', 'fear', 'joy', 'anger', 'excited', 'worried',
            'proud', 'ashamed', 'guilty', 'surprised', 'confused'
        ]
        
        content_lower = content.lower()
        score = 0.3  # Base importance
        
        # Check for importance keywords
        for keyword in importance_keywords:
            if keyword in content_lower:
                score += 0.2
        
        # Check for emotional keywords
        for keyword in emotional_keywords:
            if keyword in content_lower:
                score += 0.15
        
        # Length bonus for detailed content
        if len(content) > 200:
            score += 0.1
        if len(content) > 500:
            score += 0.1
        
        return min(1.0, score)
    
    def _extract_context_tags(self, content: str) -> List[str]:
        """Extract context tags using simple NLP"""
        import re
        
        # Extract words (simple tokenization)
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Common stop words to filter out
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'a', 'an', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top 5 most frequent words as tags
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:5]]
    
    def _store_memory(self, memory: NeuromorphicMemoryRecord):
        """Store memory in SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO memories VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory.id,
            memory.user_id,
            memory.title,
            memory.content,
            json.dumps(memory.embedding_vector),
            memory.importance_score,
            memory.emotional_salience,
            memory.date_created,
            memory.last_accessed,
            memory.temporal_decay,
            memory.usage_count,
            memory.reinforcement_strength,
            memory.emotion_tag.value,
            json.dumps(memory.context_tags),
            json.dumps(memory.cross_references)
        ))
        
        conn.commit()
        conn.close()
    
    def access_memory(self, memory_id: str) -> Optional[NeuromorphicMemoryRecord]:
        """Access memory and strengthen neural pathway"""
        memory = self._load_memory(memory_id)
        if not memory:
            return None
        
        # Neuromorphic strengthening - Hebbian learning
        memory.usage_count += 1
        memory.last_accessed = datetime.now().isoformat()
        
        # Strengthen synaptic connection
        strengthening_factor = 0.05 * (1 - memory.reinforcement_strength)
        memory.reinforcement_strength = min(1.0, memory.reinforcement_strength + strengthening_factor)
        
        # Update importance based on usage pattern
        usage_boost = min(0.1, memory.usage_count * 0.01)
        memory.importance_score = min(1.0, memory.importance_score + usage_boost)
        
        # Store updated memory
        self._store_memory(memory)
        
        print(f"🧠 Memory accessed: '{memory.title}' (Usage: {memory.usage_count}, Strength: {memory.reinforcement_strength:.2f})")
        
        return memory
    
    def _load_memory(self, memory_id: str) -> Optional[NeuromorphicMemoryRecord]:
        """Load memory from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM memories WHERE id = ?', (memory_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return NeuromorphicMemoryRecord(
            id=row[0],
            user_id=row[1],
            title=row[2],
            content=row[3],
            embedding_vector=json.loads(row[4]),
            importance_score=row[5],
            emotional_salience=row[6],
            date_created=row[7],
            last_accessed=row[8],
            temporal_decay=row[9],
            usage_count=row[10],
            reinforcement_strength=row[11],
            emotion_tag=EmotionType(row[12]),
            context_tags=json.loads(row[13]),
            cross_references=json.loads(row[14])
        )
    
    def semantic_search(self, query: str, limit: int = 10, min_similarity: float = 0.3) -> List[Tuple[NeuromorphicMemoryRecord, float]]:
        """Perform semantic search using vector similarity"""
        query_vector = self._generate_embedding_placeholder(query)
        
        # Load all memories
        memories = self._load_all_memories()
        
        # Calculate similarities
        results = []
        for memory in memories:
            similarity = self._cosine_similarity(query_vector, memory.embedding_vector)
            if similarity >= min_similarity:
                # Update temporal decay
                memory.temporal_decay = self.calculate_temporal_decay(memory)
                results.append((memory, similarity))
        
        # Sort by combined score (similarity + importance + emotional salience)
        results.sort(key=lambda x: (
            x[1] * 0.4 +  # Similarity weight
            x[0].importance_score * 0.3 +  # Importance weight
            x[0].emotional_salience * 0.2 +  # Emotional weight
            x[0].temporal_decay * 0.1  # Recency weight
        ), reverse=True)
        
        return results[:limit]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _load_all_memories(self) -> List[NeuromorphicMemoryRecord]:
        """Load all memories from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM memories WHERE user_id = ?', (self.user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        memories = []
        for row in rows:
            memory = NeuromorphicMemoryRecord(
                id=row[0],
                user_id=row[1],
                title=row[2],
                content=row[3],
                embedding_vector=json.loads(row[4]),
                importance_score=row[5],
                emotional_salience=row[6],
                date_created=row[7],
                last_accessed=row[8],
                temporal_decay=row[9],
                usage_count=row[10],
                reinforcement_strength=row[11],
                emotion_tag=EmotionType(row[12]),
                context_tags=json.loads(row[13]),
                cross_references=json.loads(row[14])
            )
            memories.append(memory)
        
        return memories
    
    def consolidate_memories(self):
        """Perform memory consolidation (dream state processing)"""
        print("🌙 Entering neuromorphic consolidation state...")
        
        memories = self._load_all_memories()
        
        for memory in memories:
            # Update temporal decay
            memory.temporal_decay = self.calculate_temporal_decay(memory)
            
            # Strengthen frequently accessed memories
            if memory.usage_count > 5:
                memory.reinforcement_strength = min(1.0, memory.reinforcement_strength + 0.02)
            
            # Build cross-references based on semantic similarity
            self._build_cross_references(memory, memories)
            
            # Store updated memory
            self._store_memory(memory)
        
        print("🌙 Neuromorphic consolidation complete")
    
    def _build_cross_references(self, target_memory: NeuromorphicMemoryRecord, all_memories: List[NeuromorphicMemoryRecord]):
        """Build cross-references between related memories"""
        similarities = []
        
        for memory in all_memories:
            if memory.id != target_memory.id:
                similarity = self._cosine_similarity(target_memory.embedding_vector, memory.embedding_vector)
                if similarity > 0.7:  # High similarity threshold
                    similarities.append((memory.id, similarity))
        
        # Keep top 3 most similar memories as cross-references
        similarities.sort(key=lambda x: x[1], reverse=True)
        target_memory.cross_references = [mem_id for mem_id, _ in similarities[:3]]
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics"""
        memories = self._load_all_memories()
        
        if not memories:
            return {
                "total_memories": 0,
                "active_memories": 0,
                "average_importance": 0,
                "average_emotional_salience": 0,
                "emotion_distribution": {},
                "recent_activity": 0
            }
        
        # Calculate statistics
        active_memories = [m for m in memories if self.calculate_temporal_decay(m) > 0.1]
        
        emotion_dist = {}
        for memory in memories:
            emotion = memory.emotion_tag.value
            emotion_dist[emotion] = emotion_dist.get(emotion, 0) + 1
        
        recent_activity = len([
            m for m in memories 
            if (datetime.now() - datetime.fromisoformat(m.last_accessed)).days < 1
        ])
        
        return {
            "total_memories": len(memories),
            "active_memories": len(active_memories),
            "average_importance": sum(m.importance_score for m in memories) / len(memories),
            "average_emotional_salience": sum(m.emotional_salience for m in memories) / len(memories),
            "emotion_distribution": emotion_dist,
            "recent_activity": recent_activity,
            "average_usage": sum(m.usage_count for m in memories) / len(memories),
            "strongest_memories": len([m for m in memories if m.reinforcement_strength > 0.8])
        }

# Global instance for Lyra system
lyra_memory = NeuromorphicMemorySystem()

