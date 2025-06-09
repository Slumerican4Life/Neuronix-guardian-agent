
import { MemoryRecord, MemoryStats, MemoryQuery } from '../types/memory';

// Neuromorphic Memory Manager - Core intelligence system for Lyra
export class MemoryManager {
  private memories: MemoryRecord[] = [];
  private currentUserId = 'lyra-user-001'; // Default user ID

  // Neuromorphic importance calculation based on multiple factors
  calculateImportance(
    emotionalWeight: number,
    usageFrequency: number,
    recency: number,
    crossConnections: number
  ): number {
    return Math.min(1, 
      (emotionalWeight * 0.3) + 
      (usageFrequency * 0.2) + 
      (recency * 0.2) + 
      (crossConnections * 0.3)
    );
  }

  // Memory decay simulation - memories fade without reinforcement
  calculateDecay(memory: MemoryRecord): number {
    const timeSinceAccess = Date.now() - new Date(memory.last_accessed).getTime();
    const daysSinceAccess = timeSinceAccess / (1000 * 60 * 60 * 24);
    const baseDamping = 0.05; // Base decay rate per day
    const usageProtection = Math.min(0.8, memory.usage_count * 0.1);
    const emotionalProtection = this.getEmotionalWeight(memory.emotion_flag) * 0.2;
    
    const effectiveDecay = baseDamping * (1 - usageProtection - emotionalProtection);
    return Math.max(0, memory.importance_score - (effectiveDecay * daysSinceAccess));
  }

  // Emotional salience weighting - emotions affect memory strength
  getEmotionalWeight(emotion: string): number {
    const emotionalWeights = {
      'happy': 0.7,
      'excited': 0.8,
      'anxious': 0.9,
      'angry': 0.85,
      'sad': 0.75,
      'curious': 0.6,
      'neutral': 0.3
    };
    return emotionalWeights[emotion as keyof typeof emotionalWeights] || 0.3;
  }

  // Detect importance in content automatically
  detectImportance(content: string): number {
    const importanceKeywords = [
      'important', 'critical', 'urgent', 'remember', 'never forget',
      'warning', 'danger', 'emergency', 'secret', 'password', 'key'
    ];
    
    const emotionalKeywords = [
      'love', 'hate', 'fear', 'joy', 'anger', 'excited', 'worried'
    ];

    let score = 0.3; // Base importance
    
    // Check for importance keywords
    importanceKeywords.forEach(keyword => {
      if (content.toLowerCase().includes(keyword)) {
        score += 0.2;
      }
    });

    // Check for emotional keywords
    emotionalKeywords.forEach(keyword => {
      if (content.toLowerCase().includes(keyword)) {
        score += 0.15;
      }
    });

    // Length bonus for detailed content
    if (content.length > 200) score += 0.1;
    if (content.length > 500) score += 0.1;

    return Math.min(1, score);
  }

  // Create new memory with neuromorphic properties
  async createMemory(
    title: string,
    content: string,
    emotion: MemoryRecord['emotion_flag'] = 'neutral',
    sourceType: MemoryRecord['source_type'] = 'user_input',
    writeMethod: MemoryRecord['write_method'] = 'manual'
  ): Promise<MemoryRecord> {
    const now = new Date().toISOString();
    const importance = this.detectImportance(content);
    const contextTags = this.extractContextTags(content);

    const memory: MemoryRecord = {
      id: `mem_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      user_id: this.currentUserId,
      title,
      content,
      importance_score: importance,
      emotion_flag: emotion,
      date_created: now,
      last_accessed: now,
      usage_count: 1,
      decay_rate: 0.05,
      context_tags: contextTags,
      source_type: sourceType,
      write_method: writeMethod,
      dream_state: false
    };

    this.memories.push(memory);
    console.log(`🧠 New memory created: "${title}" (Importance: ${importance.toFixed(2)})`);
    return memory;
  }

  // Extract context tags from content using simple NLP
  extractContextTags(content: string): string[] {
    const words = content.toLowerCase().match(/\b\w+\b/g) || [];
    const commonWords = new Set(['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'a', 'an']);
    
    const tags = words
      .filter(word => word.length > 3 && !commonWords.has(word))
      .reduce((acc: Record<string, number>, word) => {
        acc[word] = (acc[word] || 0) + 1;
        return acc;
      }, {});

    return Object.entries(tags)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([word]) => word);
  }

  // Retrieve memories with contextual relevance
  retrieveMemories(query: MemoryQuery): MemoryRecord[] {
    return this.memories
      .map(memory => ({
        ...memory,
        current_importance: this.calculateDecay(memory)
      }))
      .filter(memory => {
        if (query.min_importance && memory.current_importance < query.min_importance) return false;
        if (query.emotion && memory.emotion_flag !== query.emotion) return false;
        if (query.content && !memory.content.toLowerCase().includes(query.content.toLowerCase())) return false;
        if (query.context_tags && !query.context_tags.some(tag => memory.context_tags.includes(tag))) return false;
        return true;
      })
      .sort((a, b) => b.current_importance - a.current_importance)
      .slice(0, query.limit || 10);
  }

  // Access memory (strengthens pathway)
  accessMemory(memoryId: string): MemoryRecord | null {
    const memory = this.memories.find(m => m.id === memoryId);
    if (!memory) return null;

    // Neuromorphic strengthening - repeated access increases importance
    memory.usage_count += 1;
    memory.last_accessed = new Date().toISOString();
    memory.importance_score = Math.min(1, memory.importance_score + 0.05);

    console.log(`🧠 Memory accessed: "${memory.title}" (Usage: ${memory.usage_count})`);
    return memory;
  }

  // Get memory statistics for monitoring
  getMemoryStats(): MemoryStats {
    const activeMemories = this.memories.filter(m => this.calculateDecay(m) > 0.1);
    const emotionalDist = this.memories.reduce((acc, m) => {
      acc[m.emotion_flag] = (acc[m.emotion_flag] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      total_memories: this.memories.length,
      active_memories: activeMemories.length,
      decayed_memories: this.memories.length - activeMemories.length,
      average_importance: this.memories.reduce((sum, m) => sum + this.calculateDecay(m), 0) / this.memories.length || 0,
      emotional_distribution: emotionalDist,
      recent_activity: this.memories.filter(m => 
        Date.now() - new Date(m.last_accessed).getTime() < 24 * 60 * 60 * 1000
      ).length
    };
  }

  // Process memories during "dream state" - consolidation
  dreamStateProcessing(): void {
    console.log('🌙 Entering dream state - memory consolidation...');
    
    // Strengthen frequently accessed memories
    this.memories.forEach(memory => {
      if (memory.usage_count > 3) {
        memory.importance_score = Math.min(1, memory.importance_score + 0.02);
      }
    });

    // Mark processed memories
    this.memories.forEach(memory => {
      memory.dream_state = true;
    });

    console.log('🌙 Dream state processing complete');
  }

  // Get all memories for dashboard
  getAllMemories(): MemoryRecord[] {
    return this.memories.map(memory => ({
      ...memory,
      current_importance: this.calculateDecay(memory)
    }));
  }
}

// Singleton instance for global access
export const memoryManager = new MemoryManager();
