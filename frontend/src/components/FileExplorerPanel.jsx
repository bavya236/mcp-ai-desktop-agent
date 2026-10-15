import React, { useState, useEffect } from 'react';
import { 
  Folder, 
  FolderOpen, 
  FileText, 
  FileCode, 
  RefreshCw, 
  Eye, 
  X, 
  FileCheck, 
  HardDrive,
  ChevronRight,
  Sparkles,
  Search
} from 'lucide-react';

export default function FileExplorerPanel({ targetDir, onSelectFileForPrompt }) {
  const [fileData, setFileData] = useState({ files: [], directories: [] });
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPreview, setSelectedPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [searchFilter, setSearchFilter] = useState("");

  const fetchFiles = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`/api/files/browse?directory=${encodeURIComponent(targetDir)}`);
      const data = await res.json();
      if (data.success) {
        setFileData(data);
      }
    } catch (err) {
      console.error("Failed to browse files:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
    const interval = setInterval(fetchFiles, 4000); // Poll for live desktop updates
    return () => clearInterval(interval);
  }, [targetDir]);

  const handlePreview = async (filePath) => {
    setPreviewLoading(true);
    setSelectedPreview({ path: filePath, content: "Loading file content..." });
    try {
      const res = await fetch('/api/tools/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_name: 'read_file_content',
          arguments: { file_path: filePath, max_chars: 6000 }
        })
      });
      const data = await res.json();
      if (data.success) {
        setSelectedPreview({
          path: filePath,
          content: data.content,
          info: data.file_info,
          pages: data.total_pages
        });
      } else {
        setSelectedPreview({ path: filePath, content: `Error: ${data.error}` });
      }
    } catch (err) {
      setSelectedPreview({ path: filePath, content: `Failed to read file: ${err.message}` });
    } finally {
      setPreviewLoading(false);
    }
  };

  const filteredFiles = fileData.files.filter(f => 
    f.name.toLowerCase().includes(searchFilter.toLowerCase())
  );
  const filteredDirs = fileData.directories.filter(d => 
    d.name.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <div className="flex flex-col h-[calc(100vh-14rem)] min-h-[500px] glass-panel rounded-2xl border border-slate-800 overflow-hidden">
      
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
        <div className="flex items-center gap-2">
          <HardDrive className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-semibold text-slate-200 truncate max-w-[200px]" title={fileData.target_directory || targetDir}>
            Live Directory: {targetDir}
          </span>
        </div>

        <button
          onClick={fetchFiles}
          disabled={isLoading}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white bg-slate-900 hover:bg-slate-800 border border-slate-800 transition-all"
          title="Refresh Directory"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-emerald-400' : ''}`} />
        </button>
      </div>

      {/* Search filter */}
      <div className="p-2 border-b border-slate-800/80 bg-slate-950/20">
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-500" />
          <input
            type="text"
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            placeholder="Filter files..."
            className="w-full bg-slate-900/80 border border-slate-800/80 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Files List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        {/* Directories */}
        {filteredDirs.map((d, i) => (
          <div
            key={`dir-${i}`}
            className="flex items-center justify-between p-2 rounded-xl bg-slate-900/40 hover:bg-slate-800/60 border border-slate-800/60 text-xs transition-all group cursor-pointer"
          >
            <div className="flex items-center gap-2 truncate">
              <Folder className="w-4 h-4 text-amber-400 shrink-0 group-hover:scale-110 transition-transform" />
              <span className="font-semibold text-slate-200 truncate">{d.name}</span>
            </div>
            <span className="text-[10px] text-slate-500 font-mono">Folder</span>
          </div>
        ))}

        {/* Files */}
        {filteredFiles.map((f, i) => {
          const isPdf = f.extension === '.pdf';
          const isPy = f.extension === '.py';

          return (
            <div
              key={`file-${i}`}
              className="flex items-center justify-between p-2 rounded-xl bg-slate-900/30 hover:bg-slate-800/70 border border-slate-800/40 text-xs transition-all group"
            >
              <div className="flex items-center gap-2 truncate flex-1 mr-2">
                {isPdf ? (
                  <FileText className="w-4 h-4 text-rose-400 shrink-0 group-hover:scale-110 transition-transform" />
                ) : isPy ? (
                  <FileCode className="w-4 h-4 text-purple-400 shrink-0 group-hover:scale-110 transition-transform" />
                ) : (
                  <FileCheck className="w-4 h-4 text-blue-400 shrink-0" />
                )}
                
                <div className="truncate">
                  <p className="font-medium text-slate-200 truncate group-hover:text-white">
                    {f.name}
                  </p>
                  <p className="text-[10px] text-slate-500 font-mono">
                    {f.size_human} • {f.modified?.split(' ')[0]}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100">
                <button
                  onClick={() => handlePreview(f.path)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-indigo-300 hover:bg-indigo-500/20 transition-colors"
                  title="Preview File Content"
                >
                  <Eye className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          );
        })}

        {filteredDirs.length === 0 && filteredFiles.length === 0 && (
          <div className="p-6 text-center text-slate-500 text-xs space-y-2">
            <p>No files found in this directory.</p>
            <p className="text-[11px] text-indigo-400">
              Tip: Click "Populate Sandbox" in the navbar to add test interview files!
            </p>
          </div>
        )}
      </div>

      {/* Directory Summary Footer */}
      <div className="px-4 py-2 border-t border-slate-800 bg-slate-950/40 text-[11px] text-slate-400 flex items-center justify-between font-mono">
        <span>{fileData.files_count || 0} Files</span>
        <span>{fileData.directories_count || 0} Folders</span>
      </div>

      {/* Modal Preview Drawer */}
      {selectedPreview && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="w-full max-w-2xl bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
            <div className="px-4 py-3 border-b border-slate-800 flex items-center justify-between bg-slate-950">
              <div className="flex items-center gap-2 truncate">
                <Eye className="w-4 h-4 text-indigo-400" />
                <span className="text-xs font-mono font-bold text-slate-200 truncate">
                  {selectedPreview.info?.name || selectedPreview.path}
                </span>
                {selectedPreview.pages && (
                  <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-mono">
                    {selectedPreview.pages} Page(s)
                  </span>
                )}
              </div>
              <button
                onClick={() => setSelectedPreview(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-4 flex-1 overflow-y-auto font-mono text-xs text-slate-300 bg-slate-950/80 whitespace-pre-wrap leading-relaxed">
              {previewLoading ? "Extracting content..." : selectedPreview.content}
            </div>

            <div className="px-4 py-2.5 border-t border-slate-800 bg-slate-950 text-right">
              <button
                onClick={() => setSelectedPreview(null)}
                className="px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-medium hover:bg-indigo-500"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
