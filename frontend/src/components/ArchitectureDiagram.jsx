import React from 'react';
import { Layers, X, Sparkles, Cpu, HardDrive, Terminal, Search, ArrowRight, ShieldCheck, Zap } from 'lucide-react';

export default function ArchitectureDiagram({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="w-full max-w-4xl bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">
                MCP Agent System Architecture & Interview Guide
              </h2>
              <p className="text-[11px] text-slate-400">
                Model Context Protocol (JSON-RPC 2.0) vs Traditional RAG
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-300">
          
          {/* Visual ASCII / Modern Architecture Box */}
          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 font-mono text-center">
            <span className="text-[10px] text-indigo-400 uppercase font-bold tracking-widest block mb-3">
              END-TO-END DATA & TOOL EXECUTION FLOW
            </span>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-left">
              {/* Box 1 */}
              <div className="p-3 rounded-xl bg-slate-900/90 border border-indigo-500/30 flex flex-col items-center text-center">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center mb-2">
                  🎙️
                </div>
                <span className="font-bold text-slate-200">1. User Request</span>
                <span className="text-[10px] text-slate-400 mt-1">
                  Voice / Text Input: <br/>
                  <em>"Find PDFs & summarize"</em>
                </span>
              </div>

              {/* Box 2 */}
              <div className="p-3 rounded-xl bg-slate-900/90 border border-purple-500/30 flex flex-col items-center text-center">
                <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center mb-2">
                  🧠
                </div>
                <span className="font-bold text-slate-200">2. LLM ReAct Loop</span>
                <span className="text-[10px] text-slate-400 mt-1">
                  Gemini / OpenAI / Fast Agent decides tool plan & parameters
                </span>
              </div>

              {/* Box 3 */}
              <div className="p-3 rounded-xl bg-slate-900/90 border border-cyan-500/30 flex flex-col items-center text-center">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center mb-2">
                  ⚡
                </div>
                <span className="font-bold text-slate-200">3. FastMCP Server</span>
                <span className="text-[10px] text-slate-400 mt-1">
                  Standardized JSON-RPC 2.0 interface exposing tool contracts
                </span>
              </div>

              {/* Box 4 */}
              <div className="p-3 rounded-xl bg-slate-900/90 border border-emerald-500/30 flex flex-col items-center text-center">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-2">
                  💻
                </div>
                <span className="font-bold text-slate-200">4. Local OS Tools</span>
                <span className="text-[10px] text-slate-400 mt-1">
                  Filesystem, PDF reader, AST Python analyzer, Shell terminal
                </span>
              </div>
            </div>
          </div>

          {/* Key Comparisons: Why MCP vs RAG? */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            
            <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/30 space-y-2">
              <div className="flex items-center gap-2 text-indigo-300 font-bold text-sm">
                <Zap className="w-4 h-4 text-indigo-400" />
                Why MCP Tool Calling (Agentic Execution)?
              </div>
              <ul className="space-y-1.5 text-slate-300 list-disc list-inside leading-relaxed text-[11px]">
                <li><strong>Bi-directional Action:</strong> Not just reading, but performing state-changing OS actions (creating folders, moving files, executing scripts).</li>
                <li><strong>Dynamic Multi-Step Planning:</strong> Agent reasons iteratively (e.g. Find PDFs ➔ Read Content ➔ Categorize ➔ Create Folder ➔ Move files).</li>
                <li><strong>Open Protocol Standard:</strong> Same MCP server works across Claude Desktop, Cursor, and custom web frontends.</li>
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
              <div className="flex items-center gap-2 text-amber-300 font-bold text-sm">
                <ShieldCheck className="w-4 h-4 text-amber-400" />
                Security & Guardrails Implemented
              </div>
              <ul className="space-y-1.5 text-slate-400 list-disc list-inside leading-relaxed text-[11px]">
                <li><strong>Path Sandboxing:</strong> Safe resolution prevents escaping designated user scopes.</li>
                <li><strong>Destructive Command Filtering:</strong> Dangerous shell commands (`rmdir /s /q`, `format`, `dd`) are strictly blocked.</li>
                <li><strong>Context Window Protection:</strong> Smart character & page clamping prevents token blowup on large PDFs.</li>
              </ul>
            </div>

          </div>

          {/* Interview Talking Points */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <h3 className="font-bold text-white text-xs flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              Top Interview Talking Points
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-[11px] text-slate-300">
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <strong className="text-indigo-300 block mb-1">1. Model Context Protocol</strong>
                <p className="text-slate-400">Explain how MCP separates LLM reasoning from tool execution using standardized JSON-RPC 2.0 schemas.</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <strong className="text-purple-300 block mb-1">2. AST Code Analysis</strong>
                <p className="text-slate-400">Highlight how the Python AST parser analyzes function ASTs and detects algorithmic patterns without running untrusted code.</p>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                <strong className="text-emerald-300 block mb-1">3. ReAct Feedback Loop</strong>
                <p className="text-slate-400">Describe the Thought ➔ Action ➔ Observation cycle that enables self-correction and multi-step desktop workflows.</p>
              </div>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-slate-800 bg-slate-950 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500"
          >
            Got It
          </button>
        </div>

      </div>
    </div>
  );
}
