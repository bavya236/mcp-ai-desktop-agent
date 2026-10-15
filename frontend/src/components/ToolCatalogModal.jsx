import React, { useState, useEffect } from 'react';
import { 
  Wrench, 
  X, 
  Play, 
  CheckCircle, 
  AlertCircle, 
  Code, 
  Clock, 
  FileText, 
  FolderPlus, 
  ArrowRight, 
  Terminal, 
  Cpu, 
  Code2 
} from 'lucide-react';

export default function ToolCatalogModal({ isOpen, onClose }) {
  const [tools, setTools] = useState([]);
  const [selectedTool, setSelectedTool] = useState(null);
  const [paramsInput, setParamsInput] = useState("{}");
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetch('/api/tools')
        .then(res => res.json())
        .then(data => {
          setTools(data.tools || []);
          if (data.tools?.length > 0 && !selectedTool) {
            handleSelectTool(data.tools[0]);
          }
        })
        .catch(err => console.error("Error fetching tools:", err));
    }
  }, [isOpen]);

  const handleSelectTool = (tool) => {
    setSelectedTool(tool);
    setExecutionResult(null);

    // Generate sample JSON args based on properties
    const sampleArgs = {};
    if (tool.parameters?.properties) {
      for (const [key, prop] of Object.entries(tool.parameters.properties)) {
        if (key === 'directory_path') sampleArgs[key] = "sandbox/Downloads";
        else if (key === 'pattern') sampleArgs[key] = "*.pdf";
        else if (key === 'search_term') sampleArgs[key] = "interview";
        else if (key === 'file_path') sampleArgs[key] = "sandbox/Downloads/Google_SWE_Interview_Questions_2026.pdf";
        else if (key === 'folder_path') sampleArgs[key] = "sandbox/Downloads/Placement Prep";
        else if (key === 'source_path') sampleArgs[key] = "sandbox/Downloads/Google_SWE_Interview_Questions_2026.pdf";
        else if (key === 'destination_path') sampleArgs[key] = "sandbox/Downloads/Placement Prep/";
        else if (key === 'target_path') sampleArgs[key] = "sandbox/Downloads";
        else if (key === 'command') sampleArgs[key] = "dir";
        else if (prop.type === 'string') sampleArgs[key] = "";
        else if (prop.type === 'boolean') sampleArgs[key] = false;
        else if (prop.type === 'integer') sampleArgs[key] = 2;
      }
    }
    setParamsInput(JSON.stringify(sampleArgs, null, 2));
  };

  const handleExecute = async () => {
    if (!selectedTool) return;
    setExecuting(true);
    setExecutionResult(null);

    try {
      let parsedArgs = {};
      try {
        parsedArgs = JSON.parse(paramsInput);
      } catch (e) {
        alert("Invalid JSON parameters format");
        setExecuting(false);
        return;
      }

      const t0 = performance.now();
      const res = await fetch('/api/tools/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_name: selectedTool.name,
          arguments: parsedArgs
        })
      });
      const data = await res.json();
      const duration = Math.round(performance.now() - t0);

      setExecutionResult({
        duration_ms: duration,
        data: data
      });
    } catch (err) {
      setExecutionResult({
        error: err.message
      });
    } finally {
      setExecuting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
      <div className="w-full max-w-4xl bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              <Wrench className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">
                MCP Tool Registry & Live Tester
              </h2>
              <p className="text-[11px] text-slate-400">
                Model Context Protocol (JSON-RPC 2.0 Standard Specifications)
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body (2 columns) */}
        <div className="flex-1 grid grid-cols-1 md:grid-cols-3 overflow-hidden">
          
          {/* Left: Tools List */}
          <div className="border-r border-slate-800 p-3 overflow-y-auto space-y-1.5 bg-slate-950/40">
            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 px-2 block mb-1">
              Registered Tools ({tools.length})
            </span>
            {tools.map((t) => (
              <button
                key={t.name}
                onClick={() => handleSelectTool(t)}
                className={`w-full text-left p-2.5 rounded-xl border text-xs transition-all flex flex-col gap-0.5 ${
                  selectedTool?.name === t.name
                    ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-sm'
                    : 'bg-slate-900/60 border-slate-800/80 text-slate-300 hover:bg-slate-800'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono font-semibold text-indigo-300">
                    {t.name}()
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-1">
                  {t.description}
                </p>
              </button>
            ))}
          </div>

          {/* Right: Tool Details & Test Runner */}
          <div className="col-span-2 p-5 overflow-y-auto space-y-4 bg-slate-900/60">
            {selectedTool ? (
              <>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 font-mono text-xs font-bold border border-indigo-500/30">
                      {selectedTool.name}
                    </span>
                    <span className="text-xs text-slate-400">
                      MCP Tool Endpoint
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {selectedTool.description}
                  </p>
                </div>

                {/* Parameters Editor */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                      <Code className="w-3.5 h-3.5 text-indigo-400" />
                      Execution Parameters (JSON):
                    </label>
                    <span className="text-[10px] text-slate-500 font-mono">
                      Editable schema values
                    </span>
                  </div>
                  <textarea
                    value={paramsInput}
                    onChange={(e) => setParamsInput(e.target.value)}
                    rows={6}
                    className="w-full p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-indigo-300 focus:outline-none focus:border-indigo-500 transition-all"
                  />
                </div>

                {/* Execute Button */}
                <div className="flex items-center justify-between pt-1">
                  <button
                    onClick={handleExecute}
                    disabled={executing}
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-emerald-600/20 transition-all disabled:opacity-50"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    {executing ? "Executing Tool..." : "Execute MCP Tool Live"}
                  </button>

                  {executionResult?.duration_ms && (
                    <span className="text-xs text-emerald-400 font-mono flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" />
                      Executed in {executionResult.duration_ms}ms
                    </span>
                  )}
                </div>

                {/* Live Output */}
                {executionResult && (
                  <div className="space-y-1.5 pt-2">
                    <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                      Live Response Observation:
                    </span>
                    <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-300/90 overflow-x-auto max-h-56 leading-relaxed">
                      {JSON.stringify(executionResult.data || executionResult.error, null, 2)}
                    </pre>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center p-8 text-slate-500 text-xs">
                Select a tool on the left to inspect its schema and test it live.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
