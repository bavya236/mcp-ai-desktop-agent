import React from 'react';
import { 
  Bot, 
  FolderSync, 
  Settings, 
  Sparkles, 
  Wrench, 
  Layers, 
  CheckCircle2, 
  HardDrive,
  FolderOpen
} from 'lucide-react';
import confetti from 'canvas-confetti';

export default function Navbar({ 
  systemInfo, 
  targetDir, 
  setTargetDir, 
  onPopulateSandbox, 
  isPopulating, 
  onOpenSettings,
  onOpenTools,
  onOpenArch,
  activeTab,
  setActiveTab
}) {
  const triggerConfetti = () => {
    confetti({
      particleCount: 50,
      spread: 60,
      origin: { y: 0.1 }
    });
  };

  const handlePopulate = async () => {
    await onPopulateSandbox();
    triggerConfetti();
  };

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 shadow-lg shadow-indigo-500/25">
            <span className="text-xl">🧠</span>
            <span className="absolute -bottom-0.5 -right-0.5 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-1.5">
                Talk to Your Computer
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  MCP Agent
                </span>
              </h1>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Model Context Protocol • Autonomous OS Automation
            </p>
          </div>
        </div>

        {/* Directory Selector & Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          
          {/* Target Folder Selector */}
          <div className="flex items-center gap-1.5 bg-slate-900/90 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300">
            <FolderOpen className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-400 hidden md:inline">Target:</span>
            <select
              value={targetDir}
              onChange={(e) => setTargetDir(e.target.value)}
              className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer"
            >
              <option value="sandbox/Downloads" className="bg-slate-900 text-slate-200">🧪 Demo Sandbox (Downloads)</option>
              <option value="Downloads" className="bg-slate-900 text-slate-200">📥 Real Downloads</option>
              <option value="Documents" className="bg-slate-900 text-slate-200">📄 Real Documents</option>
              <option value="Desktop" className="bg-slate-900 text-slate-200">🖥️ Real Desktop</option>
              <option value="." className="bg-slate-900 text-slate-200">📁 Workspace Root</option>
            </select>
          </div>

          {/* Populate Sandbox Button */}
          <button
            onClick={handlePopulate}
            disabled={isPopulating}
            title="Generate sample interview PDFs and Python files for instant demo"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-gradient-to-r from-amber-500/20 to-orange-500/20 hover:from-amber-500/30 hover:to-orange-500/30 text-amber-300 border border-amber-500/40 transition-all shadow-sm"
          >
            <Sparkles className={`w-3.5 h-3.5 ${isPopulating ? 'animate-spin' : 'text-amber-400'}`} />
            <span className="hidden sm:inline">{isPopulating ? 'Generating...' : 'Populate Sandbox'}</span>
          </button>

          {/* MCP Tools Button */}
          <button
            onClick={onOpenTools}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 hover:border-slate-700 transition-all"
          >
            <Wrench className="w-3.5 h-3.5 text-indigo-400" />
            <span className="hidden md:inline">MCP Tools</span>
            <span className="px-1.5 py-0.2 rounded text-[10px] bg-indigo-500/20 text-indigo-300 font-mono">
              9
            </span>
          </button>

          {/* Architecture / How it works */}
          <button
            onClick={onOpenArch}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 hover:border-slate-700 transition-all"
            title="View MCP Architecture Diagram"
          >
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden lg:inline">Architecture</span>
          </button>

          {/* Settings Button */}
          <button
            onClick={onOpenSettings}
            className="p-2 rounded-lg text-slate-400 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-800 transition-all"
            title="Configure LLM & API Keys"
          >
            <Settings className="w-4 h-4" />
          </button>

        </div>
      </div>
    </header>
  );
}
