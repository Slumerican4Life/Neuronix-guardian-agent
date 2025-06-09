
// Core memory system types for Lyra's neuromorphic architecture
export interface MemoryRecord {
  id: string;
  user_id: string;
  title: string;
  content: string;
  embedding?: number[]; // Vector for semantic search
  importance_score: number; // 0-1 scale
  emotion_flag: 'happy' | 'sad' | 'angry' | 'neutral' | 'excited' | 'anxious' | 'curious';
  date_created: string;
  last_accessed: string;
  usage_count: number;
  decay_rate: number; // 0-1 scale
  context_tags: string[];
  source_type: 'user_input' | 'system_generated' | 'tool_output' | 'conversation';
  write_method: 'manual' | 'automatic' | 'importance_detected';
  dream_state: boolean;
}

export interface MemoryStats {
  total_memories: number;
  active_memories: number;
  decayed_memories: number;
  average_importance: number;
  emotional_distribution: Record<string, number>;
  recent_activity: number;
}

export interface MemoryQuery {
  content?: string;
  emotion?: string;
  context_tags?: string[];
  min_importance?: number;
  limit?: number;
}
