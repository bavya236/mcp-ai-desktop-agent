import React, { useState, useEffect } from 'react';
import { Settings, X, Key, Cpu, ShieldCheck, Sparkles, Server } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose, config, onSaveConfig }) {
  const [provider, setProvider] = useState(config.provider || 'builtin');
  const [apiKey, setApiKey] = useState(config.apiKey || '');
  const [model, setModel] = useState(config.model || '');
  const [baseUrl, setBaseUrl] = useState(config.baseUrl || '');
  const [showKey, setShowKey] = useState(false);

  useEffect(() => {
    setProvider(config.provider || 'builtin');
    setApiKey(config.apiKey || '');
    setModel(config.model || '');
    setBaseUrl(config.baseUrl || '');
  }, [config, isOpen]);

  const handleSave = () => {
    onSaveConfig({
      provider,
      apiKey,
      model,
      baseUrl
    });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        
        {/* Header */}
        <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              <Settings className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">
                Agent & LLM Provider Settings
              </h2>
              <p className="text-[11px] text-slate-400">
                Choose between Built-in Engine, Gemini, OpenAI, or Ollama
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
        <div className="p-5 space-y-4 text-xs text-slate-300">
          
          {/* Provider Selection */}
          <div className="space-y-1.5">
            <label className="font-semibold text-slate-200 block">
              LLM Reasoning Engine:
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => { setProvider('builtin'); setModel(''); }}
                className={`p-3 rounded-xl border text-left transition-all ${
                  provider === 'builtin'
                    ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-sm'
                    : 'bg-slate-950/60 border-slate-800 hover:bg-slate-800 text-slate-400'
                }`}
              >
                <div className="font-bold flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                  Built-in Engine
                </div>
                <p className="text-[10px] text-slate-400 mt-1">
                  Offline • Instant • Zero API key needed
                </p>
              </button>

              <button
                type="button"
                onClick={() => { setProvider('gemini'); setModel('gemini-2.5-flash'); }}
                className={`p-3 rounded-xl border text-left transition-all ${
                  provider === 'gemini'
                    ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-sm'
                    : 'bg-slate-950/60 border-slate-800 hover:bg-slate-800 text-slate-400'
                }`}
              >
                <div className="font-bold flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                  Google Gemini
                </div>
                <p className="text-[10px] text-slate-400 mt-1">
                  gemini-2.5-flash / gemini-2.0
                </p>
              </button>

              <button
                type="button"
                onClick={() => { setProvider('openai'); setModel('gpt-4o'); }}
                className={`p-3 rounded-xl border text-left transition-all ${
                  provider === 'openai'
                    ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-sm'
                    : 'bg-slate-950/60 border-slate-800 hover:bg-slate-800 text-slate-400'
                }`}
              >
                <div className="font-bold flex items-center gap-1.5">
                  <Server className="w-3.5 h-3.5 text-emerald-400" />
                  OpenAI
                </div>
                <p className="text-[10px] text-slate-400 mt-1">
                  gpt-4o / gpt-4o-mini
                </p>
              </button>

              <button
                type="button"
                onClick={() => { setProvider('ollama'); setModel('llama3.2'); setBaseUrl('http://localhost:11434/v1'); }}
                className={`p-3 rounded-xl border text-left transition-all ${
                  provider === 'ollama'
                    ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-sm'
                    : 'bg-slate-950/60 border-slate-800 hover:bg-slate-800 text-slate-400'
                }`}
              >
                <div className="font-bold flex items-center gap-1.5">
                  🦙 Ollama Local
                </div>
                <p className="text-[10px] text-slate-400 mt-1">
                  llama3.2 / deepseek-r1
                </p>
              </button>
            </div>
          </div>

          {/* Conditional API Key Input */}
          {provider !== 'builtin' && (
            <div className="space-y-3 pt-2">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  {provider === 'gemini' ? 'Google Gemini API Key:' : provider === 'openai' ? 'OpenAI API Key:' : 'API Key (Optional for Ollama):'}
                </label>
                <div className="relative">
                  <input
                    type={showKey ? 'text' : 'password'}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder={provider === 'gemini' ? 'AIzaSy...' : 'sk-...'}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowKey(!showKey)}
                    className="absolute right-2.5 top-2.5 text-[10px] text-slate-400 hover:text-white"
                  >
                    {showKey ? 'Hide' : 'Show'}
                  </button>
                </div>
              </div>

              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">
                  Model Identifier:
                </label>
                <input
                  type="text"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  placeholder={provider === 'gemini' ? 'gemini-2.5-flash' : provider === 'openai' ? 'gpt-4o' : 'llama3.2'}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>

              {provider === 'ollama' && (
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">
                    Base URL:
                  </label>
                  <input
                    type="text"
                    value={baseUrl}
                    onChange={(e) => setBaseUrl(e.target.value)}
                    placeholder="http://localhost:11434/v1"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-mono"
                  />
                </div>
              )}
            </div>
          )}

          {/* Privacy Note */}
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
            <span>
              All API keys and configurations are stored securely on your local machine and used exclusively for your direct MCP agent tool executions.
            </span>
          </div>

        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-slate-800 bg-slate-950 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-3 py-1.5 rounded-xl border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-900 text-xs"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-1.5 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500 transition-all shadow-md shadow-indigo-600/20"
          >
            Save Settings
          </button>
        </div>

      </div>
    </div>
  );
}
