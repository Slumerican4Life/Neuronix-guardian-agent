
import React, { useState, useEffect } from 'react';
import { memoryManager } from '../../services/memoryManager';
import { MemoryRecord, MemoryStats } from '../../types/memory';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Brain, Plus, Search, Activity, Zap } from 'lucide-react';

const MemoryDashboard: React.FC = () => {
  const [memories, setMemories] = useState<MemoryRecord[]>([]);
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newMemory, setNewMemory] = useState({
    title: '',
    content: '',
    emotion: 'neutral' as MemoryRecord['emotion_flag']
  });

  // Load memories and stats
  const refreshData = () => {
    setMemories(memoryManager.getAllMemories());
    setStats(memoryManager.getMemoryStats());
  };

  useEffect(() => {
    refreshData();
  }, []);

  // Create new memory
  const handleCreateMemory = async () => {
    if (!newMemory.title || !newMemory.content) return;

    await memoryManager.createMemory(
      newMemory.title,
      newMemory.content,
      newMemory.emotion
    );

    setNewMemory({ title: '', content: '', emotion: 'neutral' });
    setShowCreateForm(false);
    refreshData();
  };

  // Access memory (strengthens it)
  const handleAccessMemory = (memoryId: string) => {
    memoryManager.accessMemory(memoryId);
    refreshData();
  };

  // Filter memories based on search
  const filteredMemories = memories.filter(memory =>
    memory.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    memory.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    memory.context_tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Get emotion color
  const getEmotionColor = (emotion: string) => {
    const colors = {
      happy: 'bg-green-100 text-green-800',
      sad: 'bg-blue-100 text-blue-800',
      angry: 'bg-red-100 text-red-800',
      excited: 'bg-yellow-100 text-yellow-800',
      anxious: 'bg-purple-100 text-purple-800',
      curious: 'bg-indigo-100 text-indigo-800',
      neutral: 'bg-gray-100 text-gray-800'
    };
    return colors[emotion as keyof typeof colors] || colors.neutral;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Brain className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Lyra Memory System</h1>
            <p className="text-muted-foreground">Neuromorphic memory with emotional salience</p>
          </div>
        </div>
        <Button onClick={() => setShowCreateForm(!showCreateForm)} className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>New Memory</span>
        </Button>
      </div>

      {/* Memory Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Memories</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_memories}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Memories</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.active_memories}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Importance</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{(stats.average_importance * 100).toFixed(1)}%</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.recent_activity}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Create Memory Form */}
      {showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Memory</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={newMemory.title}
                onChange={(e) => setNewMemory({ ...newMemory, title: e.target.value })}
                placeholder="Memory title..."
              />
            </div>
            
            <div>
              <Label htmlFor="content">Content</Label>
              <textarea
                id="content"
                className="w-full h-24 px-3 py-2 border border-input rounded-md bg-background text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={newMemory.content}
                onChange={(e) => setNewMemory({ ...newMemory, content: e.target.value })}
                placeholder="Memory content..."
              />
            </div>
            
            <div>
              <Label htmlFor="emotion">Emotional Context</Label>
              <select
                id="emotion"
                className="w-full px-3 py-2 border border-input rounded-md bg-background text-sm"
                value={newMemory.emotion}
                onChange={(e) => setNewMemory({ ...newMemory, emotion: e.target.value as MemoryRecord['emotion_flag'] })}
              >
                <option value="neutral">Neutral</option>
                <option value="happy">Happy</option>
                <option value="sad">Sad</option>
                <option value="angry">Angry</option>
                <option value="excited">Excited</option>
                <option value="anxious">Anxious</option>
                <option value="curious">Curious</option>
              </select>
            </div>
            
            <div className="flex space-x-2">
              <Button onClick={handleCreateMemory}>Create Memory</Button>
              <Button variant="outline" onClick={() => setShowCreateForm(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search */}
      <div className="flex items-center space-x-2">
        <Search className="h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search memories..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="max-w-md"
        />
      </div>

      {/* Memory List */}
      <div className="space-y-4">
        {filteredMemories.length === 0 ? (
          <Card>
            <CardContent className="flex items-center justify-center h-32">
              <p className="text-muted-foreground">No memories found. Create your first memory to get started.</p>
            </CardContent>
          </Card>
        ) : (
          filteredMemories.map((memory) => (
            <Card 
              key={memory.id} 
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => handleAccessMemory(memory.id)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <CardTitle className="text-lg">{memory.title}</CardTitle>
                    <div className="flex items-center space-x-2">
                      <Badge className={getEmotionColor(memory.emotion_flag)}>
                        {memory.emotion_flag}
                      </Badge>
                      <Badge variant="outline">
                        Importance: {((memory as any).current_importance * 100).toFixed(1)}%
                      </Badge>
                      <Badge variant="outline">
                        Usage: {memory.usage_count}
                      </Badge>
                    </div>
                  </div>
                  <div className="text-right text-sm text-muted-foreground">
                    <div>Created: {new Date(memory.date_created).toLocaleDateString()}</div>
                    <div>Last accessed: {new Date(memory.last_accessed).toLocaleDateString()}</div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm mb-3">{memory.content}</p>
                {memory.context_tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {memory.context_tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default MemoryDashboard;
