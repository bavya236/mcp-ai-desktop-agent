import React from 'react';
import { FileText, FolderPlus, Code2, Terminal, Sparkles } from 'lucide-react';

export default function QuickPromptBar({ onSelectPrompt, disabled }) {
  const prompts = [
    {
      id: 1,
      icon: FileText,
      color: "from-blue-500/20 to-indigo-500/20 text-blue-400 border-blue-500/30 hover:border-blue-400",
      title: "Summarize Important PDFs",
      prompt: "Find all PDFs in my Downloads folder and summarize the important ones."
    },
    {
      id: 2,
      icon: FolderPlus,
      color: "from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-500/30 hover:border-emerald-400",
      title: "Organize Placement Prep",
      prompt: "Create a folder called Placement Prep and move all my interview PDFs into it."
    },
    {
      id: 3,
      icon: Code2,
      color: "from-purple-500/20 to-pink-500/20 text-purple-400 border-purple-500/30 hover:border-purple-400",
      title: "Detect Sorting Algorithms",
      prompt: "Find my Python files and tell me which ones contain sorting algorithms."
    },
    {
      id: 4,
      icon: Terminal,
      color: "from-amber-500/20 to-orange-500/20 text-amber-400 border-amber-500/30 hover:border-amber-400",
      title: "System & Disk Overview",
      prompt: "Get a complete system overview and list all files in the current folder."
    }
  ];

  return (
    <div className="w-full mb-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          Quick Test Prompts (Interactive Scenarios)
        </span>
        <span className="text-[11px] text-slate-500 hidden sm:inline">
          Click any prompt to execute live MCP tools
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        {prompts.map((p) => {
          const Icon = p.icon;
          return (
            <button
              key={p.id}
              disabled={disabled}
              onClick={() => onSelectPrompt(p.prompt)}
              className={`flex flex-col items-start p-3 rounded-xl bg-gradient-to-br ${p.color} border transition-all text-left group hover:scale-[1.02] active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <div className="flex items-center gap-2 mb-1">
                <Icon className="w-4 h-4 shrink-0 transition-transform group-hover:scale-110" />
                <span className="text-xs font-semibold text-slate-200 group-hover:text-white">
                  {p.title}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                "{p.prompt}"
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
