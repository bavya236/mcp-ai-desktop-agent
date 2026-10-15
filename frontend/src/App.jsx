import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import QuickPromptBar from './components/QuickPromptBar';
import ChatArea from './components/ChatArea';
import FileExplorerPanel from './components/FileExplorerPanel';
import ToolCatalogModal from './components/ToolCatalogModal';
import ArchitectureDiagram from './components/ArchitectureDiagram';
import SettingsModal from './components/SettingsModal';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [targetDir, setTargetDir] = useState('sandbox/Downloads');
  const [systemInfo, setSystemInfo] = useState(null);
  const [isPopulating, setIsPopulating] = useState(false);

  // Modals state
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isToolsOpen, setIsToolsOpen] = useState(false);
  const [isArchOpen, setIsArchOpen] = useState(false);

  // LLM Config state
  const [config, setConfig] = useState(() => {
    try {
      const saved = localStorage.getItem('mcp_agent_config');
      return saved ? JSON.parse(saved) : { provider: 'builtin', apiKey: '', model: '' };
    } catch {
      return { provider: 'builtin', apiKey: '', model: '' };
    }
  });

  // Fetch initial system overview and auto-populate sandbox if needed
  useEffect(() => {
    fetch('/api/system')
      .then(res => res.json())
      .then(data => {
        setSystemInfo(data);
      })
      .catch(err => console.error("Error fetching system info:", err));
  }, []);

  const handleSaveConfig = (newConfig) => {
    setConfig(newConfig);
    try {
      localStorage.setItem('mcp_agent_config', JSON.stringify(newConfig));
    } catch (e) {
      console.error("Failed to save config to localStorage:", e);
    }
  };

  const handlePopulateSandbox = async () => {
    setIsPopulating(true);
    try {
      const res = await fetch('/api/sandbox/populate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (data.success) {
        setTargetDir('sandbox/Downloads');
      }
    } catch (err) {
      console.error("Failed to populate sandbox:", err);
    } finally {
      setIsPopulating(false);
    }
  };

  // Main Streaming Agent Execution
  const handleSendMessage = async (promptText) => {
    if (!promptText.trim() || isLoading) return;

    // Add user message
    const userMsg = { role: 'user', content: promptText };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    // Prepare assistant message container
    const assistantMsgIndex = messages.length + 1;
    const currentAssistantMsg = {
      role: 'assistant',
      content: '',
      thoughts: [],
      toolCalls: []
    };

    setMessages(prev => [...prev, currentAssistantMsg]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: promptText,
          target_directory: targetDir,
          provider: config.provider || 'builtin',
          api_key: config.apiKey,
          model: config.model,
          base_url: config.baseUrl
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned error status ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // keep trailing chunk

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.replace('data: ', '').trim();
            if (!jsonStr) continue;

            try {
              const event = JSON.parse(jsonStr);

              setMessages(prev => {
                const newArr = [...prev];
                const lastIndex = newArr.length - 1;
                const active = { ...newArr[lastIndex] };

                if (event.type === 'thought') {
                  active.thoughts = [...(active.thoughts || []), event.content];
                } else if (event.type === 'tool_start') {
                  active.toolCalls = [
                    ...(active.toolCalls || []),
                    {
                      tool: event.tool,
                      arguments: event.arguments,
                      status: 'running'
                    }
                  ];
                } else if (event.type === 'tool_result') {
                  // update matching tool call or last one
                  const tcs = [...(active.toolCalls || [])];
                  if (tcs.length > 0) {
                    const lastTc = { ...tcs[tcs.length - 1] };
                    lastTc.status = 'completed';
                    lastTc.result = event.result;
                    lastTc.duration_ms = event.duration_ms;
                    tcs[tcs.length - 1] = lastTc;
                    active.toolCalls = tcs;
                  }
                } else if (event.type === 'final_answer') {
                  active.content = event.content;
                } else if (event.type === 'error') {
                  active.content = (active.content || '') + `\n\n⚠️ **Notice:** ${event.content}`;
                }

                newArr[lastIndex] = active;
                return newArr;
              });

            } catch (err) {
              console.error("Error parsing SSE event:", err, jsonStr);
            }
          }
        }
      }
    } catch (err) {
      console.error("Chat streaming error:", err);
      setMessages(prev => {
        const newArr = [...prev];
        const lastIndex = newArr.length - 1;
        newArr[lastIndex] = {
          ...newArr[lastIndex],
          content: `❌ **Execution Error:** ${err.message}. Please ensure the backend server is running.`
        };
        return newArr;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#080C15] text-slate-100">
      
      {/* Top Navigation */}
      <Navbar
        systemInfo={systemInfo}
        targetDir={targetDir}
        setTargetDir={setTargetDir}
        onPopulateSandbox={handlePopulateSandbox}
        isPopulating={isPopulating}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenTools={() => setIsToolsOpen(true)}
        onOpenArch={() => setIsArchOpen(true)}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-5 flex flex-col gap-4">
        
        {/* Quick Action Prompt Chips */}
        <QuickPromptBar
          onSelectPrompt={handleSendMessage}
          disabled={isLoading}
        />

        {/* 2-Column Responsive Workspace */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 flex-1 items-start">
          
          {/* Left Column: Chat & Agent Execution Flow (7 cols) */}
          <div className="lg:col-span-8 flex flex-col">
            <ChatArea
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              onClearChat={handleClearChat}
            />
          </div>

          {/* Right Column: Live File Monitor & Explorer (4 cols) */}
          <div className="lg:col-span-4 flex flex-col">
            <FileExplorerPanel
              targetDir={targetDir}
              onSelectFileForPrompt={(fname) => handleSendMessage(`Analyze and summarize file: ${fname}`)}
            />
          </div>

        </div>

      </main>

      {/* Modals */}
      <ToolCatalogModal
        isOpen={isToolsOpen}
        onClose={() => setIsToolsOpen(false)}
      />

      <ArchitectureDiagram
        isOpen={isArchOpen}
        onClose={() => setIsArchOpen(false)}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        config={config}
        onSaveConfig={handleSaveConfig}
      />

    </div>
  );
}
