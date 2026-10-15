import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Mic, 
  MicOff, 
  Bot, 
  User, 
  Terminal, 
  ChevronDown, 
  ChevronUp, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Cpu, 
  Code2, 
  FolderPlus, 
  FileText, 
  ArrowRight,
  Loader2,
  Trash2,
  Sparkles
} from 'lucide-react';

const TOOL_ICONS = {
  list_files: FileText,
  search_files: FileText,
  read_file_content: FileText,
  read_file: FileText,
  create_folder: FolderPlus,
  move_file: ArrowRight,
  copy_file: ArrowRight,
  write_file: FileText,
  inspect_code_algorithms: Code2,
  execute_terminal_command: Terminal,
  get_system_overview: Cpu
};

const TOOL_COLORS = {
  list_files: "text-blue-400 bg-blue-500/10 border-blue-500/30",
  search_files: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
  read_file_content: "text-indigo-400 bg-indigo-500/10 border-indigo-500/30",
  read_file: "text-indigo-400 bg-indigo-500/10 border-indigo-500/30",
  create_folder: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
  move_file: "text-amber-400 bg-amber-500/10 border-amber-500/30",
  copy_file: "text-teal-400 bg-teal-500/10 border-teal-500/30",
  write_file: "text-sky-400 bg-sky-500/10 border-sky-500/30",
  inspect_code_algorithms: "text-purple-400 bg-purple-500/10 border-purple-500/30",
  execute_terminal_command: "text-rose-400 bg-rose-500/10 border-rose-500/30",
  get_system_overview: "text-slate-400 bg-slate-500/10 border-slate-500/30"
};

// Render simple markdown formatted text cleanly
function SimpleMarkdown({ content }) {
  if (!content) return null;

  // Split lines
  const lines = content.split('\n');
  const elements = [];

  let inCodeBlock = false;
  let codeBuffer = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith('```')) {
      if (inCodeBlock) {
        // close block
        elements.push(
          <pre key={`code-${i}`} className="p-3 my-2 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-indigo-300 overflow-x-auto">
            <code>{codeBuffer.join('\n')}</code>
          </pre>
        );
        codeBuffer = [];
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeBuffer.push(line);
      continue;
    }

    if (line.startsWith('### ')) {
      elements.push(
        <h3 key={i} className="text-sm font-bold text-slate-100 mt-3 mb-1 flex items-center gap-1.5">
          {formatInline(line.replace('### ', ''))}
        </h3>
      );
    } else if (line.startsWith('## ')) {
      elements.push(
        <h2 key={i} className="text-base font-bold text-indigo-300 mt-4 mb-2 border-b border-slate-800 pb-1">
          {formatInline(line.replace('## ', ''))}
        </h2>
      );
    } else if (line.startsWith('# ')) {
      elements.push(
        <h1 key={i} className="text-lg font-extrabold text-white mt-4 mb-2">
          {formatInline(line.replace('# ', ''))}
        </h1>
      );
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      elements.push(
        <li key={i} className="text-xs text-slate-300 ml-4 list-disc my-0.5 leading-relaxed">
          {formatInline(line.substring(2))}
        </li>
      );
    } else if (line.trim() === '---') {
      elements.push(<hr key={i} className="border-slate-800 my-3" />);
    } else if (line.trim().length > 0) {
      elements.push(
        <p key={i} className="text-xs text-slate-300 my-1 leading-relaxed">
          {formatInline(line)}
        </p>
      );
    }
  }

  return <div className="space-y-0.5">{elements}</div>;
}

function formatInline(text) {
  // Format **bold**, `code`, etc.
  const parts = [];
  const regex = /(\*\*.*?\*\*|`.*?`)/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    const token = match[0];
    if (token.startsWith('**') && token.endsWith('**')) {
      parts.push(
        <strong key={match.index} className="font-semibold text-slate-100">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith('`') && token.endsWith('`')) {
      parts.push(
        <code key={match.index} className="px-1.5 py-0.5 mx-0.5 rounded bg-slate-800/80 text-indigo-300 font-mono text-[11px] border border-slate-700/50">
          {token.slice(1, -1)}
        </code>
      );
    }
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? parts : text;
}

// Single Tool Call Inspector Box
function ToolCallBox({ toolCall }) {
  const [isOpen, setIsOpen] = useState(false);
  const Icon = TOOL_ICONS[toolCall.tool] || FileText;
  const colorClass = TOOL_COLORS[toolCall.tool] || "text-slate-400 bg-slate-800 border-slate-700";

  return (
    <div className="my-2 rounded-xl border border-slate-800/90 bg-slate-900/60 overflow-hidden text-xs transition-all shadow-sm">
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between px-3 py-2 cursor-pointer hover:bg-slate-800/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <div className={`p-1 rounded-md border ${colorClass}`}>
            <Icon className="w-3.5 h-3.5" />
          </div>
          <span className="font-mono font-medium text-slate-200">
            MCP Tool: <span className="text-indigo-400 font-semibold">{toolCall.tool}()</span>
          </span>
          {toolCall.status === 'running' ? (
            <span className="flex items-center gap-1 text-[10px] text-amber-400 font-mono px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20">
              <Loader2 className="w-2.5 h-2.5 animate-spin" />
              executing...
            </span>
          ) : (
            <span className="flex items-center gap-1 text-[10px] text-emerald-400 font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
              <CheckCircle className="w-2.5 h-2.5" />
              success
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {toolCall.duration_ms && (
            <span className="text-[10px] text-slate-400 font-mono flex items-center gap-1">
              <Clock className="w-2.5 h-2.5" />
              {toolCall.duration_ms}ms
            </span>
          )}
          {isOpen ? <ChevronUp className="w-3.5 h-3.5 text-slate-400" /> : <ChevronDown className="w-3.5 h-3.5 text-slate-400" />}
        </div>
      </div>

      {isOpen && (
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/70 space-y-2 font-mono">
          <div>
            <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">
              Arguments:
            </span>
            <pre className="p-2 rounded bg-slate-900 border border-slate-800 text-[11px] text-indigo-300 overflow-x-auto">
              {JSON.stringify(toolCall.arguments, null, 2)}
            </pre>
          </div>

          {toolCall.result && (
            <div>
              <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">
                MCP Observation / Output:
              </span>
              <pre className="p-2 rounded bg-slate-900 border border-slate-800 text-[11px] text-emerald-400/90 overflow-x-auto max-h-48">
                {JSON.stringify(toolCall.result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ChatArea({ 
  messages, 
  onSendMessage, 
  isLoading, 
  onClearChat 
}) {
  const [inputPrompt, setInputPrompt] = useState("");
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputPrompt.trim() || isLoading) return;
    onSendMessage(inputPrompt);
    setInputPrompt("");
  };

  // Speech Recognition via Web Speech API
  const toggleSpeechRecognition = () => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      alert("Speech recognition is not supported in this browser. Please use Chrome/Edge or type your message.");
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    if (isListening) {
      recognition.stop();
      setIsListening(false);
      return;
    }

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInputPrompt(transcript);
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  return (
    <div className="flex flex-col h-[calc(100vh-14rem)] min-h-[500px] glass-panel rounded-2xl border border-slate-800 overflow-hidden">
      
      {/* Chat Header */}
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-indigo-400" />
          <span className="text-xs font-semibold text-slate-200">
            Agent Execution & Tool Telemetry
          </span>
        </div>
        {messages.length > 0 && (
          <button
            onClick={onClearChat}
            className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-rose-400 transition-colors"
            title="Clear Chat History"
          >
            <Trash2 className="w-3 h-3" />
            Clear
          </button>
        )}
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-3xl shadow-inner">
              🧠
            </div>
            <div className="max-w-md space-y-1">
              <h3 className="text-sm font-bold text-slate-200">
                Ready to operate your computer
              </h3>
              <p className="text-xs text-slate-400">
                Ask the agent to find PDFs, organize interview materials into folders, detect sorting algorithms in Python scripts, or run system tasks.
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role !== 'user' && (
                <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shrink-0 shadow-md">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-2xl p-3.5 ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-br-none shadow-md'
                    : 'glass-card text-slate-200 rounded-tl-none'
                }`}
              >
                {msg.role === 'user' ? (
                  <p className="text-xs leading-relaxed font-medium">{msg.content}</p>
                ) : (
                  <div className="space-y-2">
                    {/* Inner thoughts chain */}
                    {msg.thoughts && msg.thoughts.length > 0 && (
                      <div className="p-2.5 rounded-xl bg-slate-950/80 border border-indigo-500/20 text-[11px] text-indigo-300 font-mono space-y-1">
                        <div className="flex items-center gap-1.5 font-semibold text-indigo-400">
                          <Sparkles className="w-3 h-3 animate-pulse" />
                          ReAct Chain of Thought:
                        </div>
                        {msg.thoughts.map((t, tIdx) => (
                          <div key={tIdx} className="text-slate-400 pl-4 border-l border-indigo-500/30">
                            ↳ {t}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Tool Calls */}
                    {msg.toolCalls && msg.toolCalls.map((tc, tcIdx) => (
                      <ToolCallBox key={tcIdx} toolCall={tc} />
                    ))}

                    {/* Final Markdown Answer */}
                    {msg.content && <SimpleMarkdown content={msg.content} />}
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex gap-3 items-center text-xs text-indigo-400 font-mono py-2 animate-pulse">
            <div className="w-8 h-8 rounded-xl bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
            </div>
            <span>Agent reasoning and invoking MCP tools...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-slate-800 bg-slate-950/60 flex items-center gap-2">
        {/* Voice Dictation Button */}
        <button
          type="button"
          onClick={toggleSpeechRecognition}
          className={`p-2.5 rounded-xl transition-all ${
            isListening 
              ? 'bg-rose-500 text-white animate-pulse shadow-lg shadow-rose-500/30' 
              : 'bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800'
          }`}
          title={isListening ? "Listening... Click to stop" : "Click to speak with voice"}
        >
          {isListening ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
        </button>

        {/* Text Input */}
        <input
          type="text"
          value={inputPrompt}
          onChange={(e) => setInputPrompt(e.target.value)}
          placeholder={isListening ? "🎙️ Listening to your voice..." : "Tell your computer what to do (e.g. 'Find all PDFs and summarize')..."}
          disabled={isLoading}
          className="flex-1 bg-slate-900 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none transition-all"
        />

        {/* Send Button */}
        <button
          type="submit"
          disabled={isLoading || !inputPrompt.trim()}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-all shadow-md shadow-indigo-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span>Run</span>
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}
