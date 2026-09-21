import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { MessageCircle, Send, X, ChevronDown, ChevronUp, Loader2, Sparkles } from 'lucide-react';
import { Job } from '@/types';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatbotSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  currentJob?: Job | null;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://nexerabackend.onrender.com/api';

export function ChatbotSidebar({ isOpen, onToggle, currentJob }: ChatbotSidebarProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedPrompts, setSuggestedPrompts] = useState<string[]>([
    "Why is this job a good fit for me?",
    "Give me resume tips for this job",
    "Generate a custom resume tailored to this job",
    "Write a cover letter for this job",
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Reset chat when job changes
  useEffect(() => {
    if (currentJob) {
      setMessages([{
        role: 'assistant',
        content: `I see that you're asking about this **${currentJob.job_title}** role at **${currentJob.company_name}**. What would you like to know?`
      }]);
    }
  }, [currentJob?.id]);

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: ChatMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          message: text,
          job_context: currentJob ? {
            job_title: currentJob.job_title,
            company_name: currentJob.company_name,
            location: currentJob.location,
            job_description: currentJob.job_description,
            match_score: currentJob.match_score,
            source: currentJob.source,
          } : null,
          conversation_history: messages,
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
        if (data.suggested_prompts) {
          setSuggestedPrompts(data.suggested_prompts);
        }
      } else {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: 'Sorry, I encountered an error. Please try again.' 
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Connection error. Please check your internet and try again.' 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full shadow-lg flex items-center justify-center text-white hover:scale-110 transition-transform z-50"
      >
        <MessageCircle className="w-6 h-6" />
      </button>
    );
  }

  return (
    <div className="fixed right-0 top-0 h-full w-80 bg-card border-l border-border shadow-2xl flex flex-col z-50">
      {/* Header */}
      <div className="p-4 border-b border-border bg-gradient-to-r from-emerald-500/10 to-teal-500/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">Clawd</h3>
              <p className="text-xs text-muted-foreground">Your AI Copilot</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onToggle}>
            <X className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* Welcome / Context */}
      {currentJob && (
        <div className="p-3 bg-muted/50 border-b border-border">
          <p className="text-xs text-muted-foreground">Currently viewing:</p>
          <p className="text-sm font-medium text-foreground line-clamp-1">{currentJob.job_title}</p>
          <p className="text-xs text-muted-foreground">{currentJob.company_name}</p>
        </div>
      )}

      {/* Tasks I can help with */}
      <div className="p-3 border-b border-border">
        <p className="text-xs font-medium text-muted-foreground mb-2">Tasks I can assist you with:</p>
        <div className="space-y-1 text-xs">
          <div className="flex items-center gap-2 text-muted-foreground">
            <span className="text-yellow-500">🎯</span> Adjust current preference
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <span className="text-yellow-500">⭐</span> Top Match jobs
          </div>
          <div className="flex items-center gap-2 text-muted-foreground">
            <span className="text-emerald-500">💬</span> Ask Clawd
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !currentJob && (
          <div className="text-center text-muted-foreground py-8">
            <Sparkles className="w-12 h-12 mx-auto mb-4 text-emerald-500/50" />
            <p className="text-sm">Welcome back!</p>
            <p className="text-xs mt-1">Click on a job to get AI insights</p>
          </div>
        )}
        
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[90%] rounded-2xl px-4 py-2 text-sm ${
                msg.role === 'user'
                  ? 'bg-emerald-500 text-white rounded-br-md'
                  : 'bg-muted text-foreground rounded-bl-md'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-muted rounded-2xl rounded-bl-md px-4 py-2">
              <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompts */}
      {suggestedPrompts.length > 0 && messages.length > 0 && (
        <div className="px-4 py-2 border-t border-border">
          <div className="flex flex-wrap gap-2">
            {suggestedPrompts.slice(0, 3).map((prompt, i) => (
              <button
                key={i}
                onClick={() => sendMessage(prompt)}
                className="text-xs px-3 py-1.5 bg-muted hover:bg-muted/80 rounded-full text-muted-foreground hover:text-foreground transition-colors"
              >
                {prompt.length > 30 ? prompt.slice(0, 30) + '...' : prompt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-border bg-card">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything..."
            className="flex-1 bg-muted border-0 focus-visible:ring-1 focus-visible:ring-emerald-500"
            disabled={isLoading}
          />
          <Button
            onClick={() => sendMessage(input)}
            disabled={isLoading || !input.trim()}
            size="icon"
            className="bg-emerald-500 hover:bg-emerald-600"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
