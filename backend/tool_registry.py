"""
MCP Tool Registry & Execution Engine.
Contains the direct Python implementations of all tools used by the MCP server and Desktop AI Agent.
"""

import os
import sys
import ast
import re
import time
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from .system_utils import resolve_path, is_safe_command, format_file_size, get_user_directories

# Try importing pypdf for PDF reading
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


def list_files(
    directory_path: str = "Downloads",
    pattern: str = "*",
    recursive: bool = False,
    max_depth: int = 2,
    include_hidden: bool = False
) -> Dict[str, Any]:
    """
    List files and directories within a given target directory.
    
    Args:
        directory_path: Target directory (e.g. 'Downloads', 'Documents', 'sandbox', or an absolute path).
        pattern: Glob pattern like '*.pdf', '*.py', or '*'.
        recursive: Whether to search recursively in subdirectories.
        max_depth: Maximum recursion depth when recursive is True.
        include_hidden: Whether to include hidden files (starting with .).
        
    Returns:
        Structured dictionary with directory metadata and item listing.
    """
    try:
        resolved = resolve_path(directory_path)
        if not resolved.exists():
            return {
                "success": False,
                "error": f"Directory not found: {directory_path} (resolved to {resolved})",
                "files": [],
                "directories": [],
                "count": 0
            }
        if not resolved.is_dir():
            return {
                "success": False,
                "error": f"Path is not a directory: {resolved}",
                "files": [],
                "directories": [],
                "count": 0
            }

        files_list = []
        dirs_list = []
        
        def process_entry(entry: Path, current_depth: int):
            if not include_hidden and entry.name.startswith("."):
                return
            try:
                stat = entry.stat()
                mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
                
                if entry.is_dir():
                    dirs_list.append({
                        "name": entry.name,
                        "path": str(entry.resolve()),
                        "relative_path": str(entry.relative_to(resolved)),
                        "type": "directory",
                        "modified": mod_time
                    })
                    if recursive and current_depth < max_depth:
                        for child in entry.iterdir():
                            process_entry(child, current_depth + 1)
                elif entry.is_file():
                    # check glob match
                    if entry.match(pattern):
                        files_list.append({
                            "name": entry.name,
                            "path": str(entry.resolve()),
                            "relative_path": str(entry.relative_to(resolved)),
                            "type": "file",
                            "extension": entry.suffix.lower(),
                            "size_bytes": stat.st_size,
                            "size_human": format_file_size(stat.st_size),
                            "modified": mod_time
                        })
            except (PermissionError, FileNotFoundError, OSError):
                pass

        if recursive:
            for item in resolved.iterdir():
                process_entry(item, current_depth=1)
        else:
            for item in resolved.glob(pattern):
                if not include_hidden and item.name.startswith("."):
                    continue
                try:
                    stat = item.stat()
                    mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime))
                    if item.is_dir():
                        dirs_list.append({
                            "name": item.name,
                            "path": str(item.resolve()),
                            "type": "directory",
                            "modified": mod_time
                        })
                    else:
                        files_list.append({
                            "name": item.name,
                            "path": str(item.resolve()),
                            "type": "file",
                            "extension": item.suffix.lower(),
                            "size_bytes": stat.st_size,
                            "size_human": format_file_size(stat.st_size),
                            "modified": mod_time
                        })
                except (PermissionError, FileNotFoundError, OSError):
                    pass

        return {
            "success": True,
            "target_directory": str(resolved),
            "files_count": len(files_list),
            "directories_count": len(dirs_list),
            "files": files_list,
            "directories": dirs_list
        }
    except Exception as e:
        return {"success": False, "error": str(e), "files": [], "directories": []}


def search_files(
    search_term: str,
    directory_path: str = ".",
    search_type: str = "both",  # "name", "content", "both"
    file_extension: Optional[str] = None,
    max_results: int = 30
) -> Dict[str, Any]:
    """
    Search for files by filename pattern or by searching file content (including inside PDFs and code).
    
    Args:
        search_term: The search keyword, query, or regex.
        directory_path: Starting directory for search.
        search_type: 'name' (filename only), 'content' (file body), or 'both'.
        file_extension: Optional filter like '.pdf', '.py', '.txt'.
        max_results: Maximum results to return.
    """
    try:
        resolved = resolve_path(directory_path)
        if not resolved.exists() or not resolved.is_dir():
            return {"success": False, "error": f"Invalid directory: {directory_path}", "matches": []}

        matches = []
        term_lower = search_term.lower()
        
        # Walk directory
        for root, dirs, files in os.walk(resolved):
            # Skip hidden and system folders
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", ".venv", "__pycache__", ".git"]]
            
            for f in files:
                if len(matches) >= max_results:
                    break
                if f.startswith("."):
                    continue
                    
                file_path = Path(root) / f
                ext = file_path.suffix.lower()
                
                if file_extension:
                    clean_ext = ("." + file_extension.lstrip(".")).lower()
                    if ext != clean_ext:
                        continue

                name_matched = term_lower in f.lower()
                content_matched = False
                matched_snippet = ""

                # If searching content
                if search_type in ["content", "both"] and not name_matched:
                    try:
                        if ext == ".pdf" and PYPDF_AVAILABLE:
                            # PDF search
                            reader = pypdf.PdfReader(str(file_path))
                            for page_idx, page in enumerate(reader.pages[:10]):
                                text = page.extract_text() or ""
                                if term_lower in text.lower():
                                    content_matched = True
                                    idx = text.lower().find(term_lower)
                                    start = max(0, idx - 60)
                                    end = min(len(text), idx + len(term_lower) + 60)
                                    matched_snippet = f"[Page {page_idx+1}] ...{text[start:end].replace(chr(10), ' ')}..."
                                    break
                        elif ext in [".py", ".txt", ".md", ".json", ".csv", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".sh", ".bat"]:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f_obj:
                                content = f_obj.read()
                                if term_lower in content.lower():
                                    content_matched = True
                                    idx = content.lower().find(term_lower)
                                    start = max(0, idx - 60)
                                    end = min(len(content), idx + len(term_lower) + 60)
                                    matched_snippet = f"...{content[start:end].replace(chr(10), ' ')}..."
                    except Exception:
                        pass

                if name_matched or content_matched:
                    try:
                        stat = file_path.stat()
                        matches.append({
                            "name": file_path.name,
                            "path": str(file_path.resolve()),
                            "relative_path": str(file_path.relative_to(resolved)),
                            "extension": ext,
                            "size_human": format_file_size(stat.st_size),
                            "match_reason": "Filename match" if name_matched else "Content match",
                            "snippet": matched_snippet
                        })
                    except Exception:
                        pass

        return {
            "success": True,
            "search_term": search_term,
            "directory": str(resolved),
            "total_matches": len(matches),
            "matches": matches
        }
    except Exception as e:
        return {"success": False, "error": str(e), "matches": []}


def read_file_content(
    file_path: str,
    max_chars: int = 15000,
    page_range: Optional[str] = None
) -> Dict[str, Any]:
    """
    Read content from a file. Automatically extracts text from PDFs, source code (.py, .js, etc.), markdown, text, etc.
    
    Args:
        file_path: Path to file.
        max_chars: Maximum characters to return to prevent overflowing context window.
        page_range: For PDFs, optional page string like '1-3' or '1'.
    """
    try:
        resolved = resolve_path(file_path)
        if not resolved.exists():
            return {"success": False, "error": f"File not found: {file_path} (resolved to {resolved})"}
        if resolved.is_dir():
            return {"success": False, "error": f"Target path is a directory, not a file: {resolved}"}

        ext = resolved.suffix.lower()
        stat = resolved.stat()
        file_info = {
            "name": resolved.name,
            "path": str(resolved),
            "extension": ext,
            "size_bytes": stat.st_size,
            "size_human": format_file_size(stat.st_size),
        }

        # PDF Reading Handler
        if ext == ".pdf":
            if not PYPDF_AVAILABLE:
                return {
                    "success": False,
                    "error": "pypdf library not installed. Please install pypdf to read PDF files.",
                    "file_info": file_info
                }
            
            reader = pypdf.PdfReader(str(resolved))
            total_pages = len(reader.pages)
            
            # Determine pages to extract
            pages_to_read = range(total_pages)
            if page_range:
                try:
                    if "-" in page_range:
                        start_p, end_p = map(int, page_range.split("-"))
                        pages_to_read = range(max(0, start_p - 1), min(total_pages, end_p))
                    else:
                        single_p = int(page_range) - 1
                        if 0 <= single_p < total_pages:
                            pages_to_read = [single_p]
                except ValueError:
                    pass

            extracted_text = []
            char_count = 0
            is_truncated = False

            for p_num in pages_to_read:
                p = reader.pages[p_num]
                page_text = p.extract_text() or ""
                header = f"\n--- [Page {p_num + 1} of {total_pages}] ---\n"
                extracted_text.append(header + page_text)
                char_count += len(page_text)
                if char_count >= max_chars:
                    is_truncated = True
                    extracted_text.append(f"\n...[Truncated after {max_chars} characters. Total PDF pages: {total_pages}]...")
                    break

            full_content = "".join(extracted_text)
            return {
                "success": True,
                "file_info": file_info,
                "content_type": "pdf",
                "total_pages": total_pages,
                "pages_read": len(pages_to_read),
                "is_truncated": is_truncated,
                "content": full_content
            }

        # Text / Code Handler
        encodings = ["utf-8", "latin-1", "cp1252", "ascii"]
        content = None
        for enc in encodings:
            try:
                with open(resolved, "r", encoding=enc) as f:
                    content = f.read()
                    break
            except UnicodeDecodeError:
                continue

        if content is None:
            return {
                "success": False,
                "error": "Binary or unreadable file format",
                "file_info": file_info
            }

        is_truncated = len(content) > max_chars
        truncated_content = content[:max_chars]
        if is_truncated:
            truncated_content += f"\n\n...[Truncated after {max_chars} characters of {len(content)} total]..."

        return {
            "success": True,
            "file_info": file_info,
            "content_type": "text/code",
            "line_count": len(content.splitlines()),
            "is_truncated": is_truncated,
            "content": truncated_content
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def create_folder(folder_path: str) -> Dict[str, Any]:
    """
    Create a new directory (and any necessary parent directories).
    
    Args:
        folder_path: Path for new folder (e.g. 'Downloads/Placement Prep' or 'C:/...').
    """
    try:
        resolved = resolve_path(folder_path)
        if resolved.exists():
            if resolved.is_dir():
                return {
                    "success": True,
                    "message": f"Folder already exists: {resolved}",
                    "path": str(resolved),
                    "created": False
                }
            else:
                return {
                    "success": False,
                    "error": f"A file with that name already exists at {resolved}"
                }

        resolved.mkdir(parents=True, exist_ok=True)
        return {
            "success": True,
            "message": f"Folder created successfully at {resolved}",
            "path": str(resolved),
            "created": True
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def move_file(source_path: str, destination_path: str, overwrite: bool = False) -> Dict[str, Any]:
    """
    Move a file or folder from source to destination.
    
    Args:
        source_path: Source file or directory path.
        destination_path: Destination path or destination directory.
        overwrite: Whether to overwrite existing file at destination.
    """
    try:
        src = resolve_path(source_path)
        if not src.exists():
            return {"success": False, "error": f"Source does not exist: {source_path} (resolved: {src})"}

        dest = resolve_path(destination_path)
        
        # If destination is an existing directory, move into it with same filename
        if dest.exists() and dest.is_dir():
            dest = dest / src.name

        # If dest exists and is a file
        if dest.exists() and not overwrite and dest != src:
            return {
                "success": False,
                "error": f"Destination file already exists: {dest}. Set overwrite=True to overwrite."
            }

        # Parent directory of dest must exist
        dest.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(src), str(dest))
        return {
            "success": True,
            "message": f"Successfully moved '{src.name}' to '{dest}'",
            "source": str(src),
            "destination": str(dest)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def copy_file(source_path: str, destination_path: str, overwrite: bool = False) -> Dict[str, Any]:
    """
    Copy a file or directory.
    """
    try:
        src = resolve_path(source_path)
        if not src.exists():
            return {"success": False, "error": f"Source does not exist: {source_path}"}

        dest = resolve_path(destination_path)
        if dest.exists() and dest.is_dir():
            dest = dest / src.name

        if dest.exists() and not overwrite:
            return {"success": False, "error": f"Destination already exists: {dest}"}

        dest.parent.mkdir(parents=True, exist_ok=True)

        if src.is_dir():
            shutil.copytree(str(src), str(dest), dirs_exist_ok=overwrite)
        else:
            shutil.copy2(str(src), str(dest))

        return {
            "success": True,
            "message": f"Successfully copied to '{dest}'",
            "source": str(src),
            "destination": str(dest)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def write_file(file_path: str, content: str, mode: str = "write") -> Dict[str, Any]:
    """
    Write or append text content to a file.
    
    Args:
        file_path: Target path.
        content: Text content to write.
        mode: 'write' (overwrite) or 'append'.
    """
    try:
        resolved = resolve_path(file_path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        
        write_mode = "a" if mode == "append" else "w"
        with open(resolved, write_mode, encoding="utf-8") as f:
            f.write(content)

        stat = resolved.stat()
        return {
            "success": True,
            "message": f"Successfully wrote {len(content)} characters to {resolved}",
            "path": str(resolved),
            "size_human": format_file_size(stat.st_size)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def inspect_code_algorithms(target_path: str = ".") -> Dict[str, Any]:
    """
    Analyzes Python source files in a directory or single file using AST and heuristic analysis
    to detect algorithms (Sorting algorithms: Quick Sort, Merge Sort, Bubble Sort, Heap Sort, Insertion Sort, etc.,
    and Search/Graph algorithms: Binary Search, BFS, DFS, Dijkstra, Dynamic Programming).
    
    Args:
        target_path: Path to a python file or directory containing python files.
    """
    try:
        resolved = resolve_path(target_path)
        if not resolved.exists():
            return {"success": False, "error": f"Target path does not exist: {target_path}"}

        py_files = []
        if resolved.is_file() and resolved.suffix.lower() == ".py":
            py_files = [resolved]
        elif resolved.is_dir():
            for root, dirs, files in os.walk(resolved):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", ".venv", "__pycache__"]]
                for f in files:
                    if f.endswith(".py"):
                        py_files.append(Path(root) / f)
        else:
            return {"success": False, "error": "Path is neither a .py file nor a directory"}

        detected_results = []
        
        # Algorithm signatures and patterns
        SORTING_PATTERNS = {
            "Bubble Sort": [r"bubble_?sort", r"for\s+.*\s+in\s+range\(.*\):\s*for\s+.*\s+in\s+range\(.*-.*\):.*>\s*.*:\s*.*,\s*.*=.*,\s*.*"],
            "Quick Sort": [r"quick_?sort", r"partition\(", r"pivot\s*=", r"\[\s*x\s+for\s+x\s+in\s+.*\s+if\s+x\s*<\s*pivot\s*\]"],
            "Merge Sort": [r"merge_?sort", r"def\s+merge\(", r"mid\s*=\s*len\(.*\)\s*//\s*2", r"left.*right.*while.*<.*and.*<.*:"],
            "Insertion Sort": [r"insertion_?sort", r"key\s*=\s*arr\[i\]", r"while\s+j\s*>=?\s*0\s+and\s+.*\s*>\s*key"],
            "Selection Sort": [r"selection_?sort", r"min_?idx\s*=", r"if\s+arr\[j\]\s*<\s*arr\[min_?idx\]"],
            "Heap Sort": [r"heap_?sort", r"heapify\(", r"heappop\(", r"heappush\("],
            "Counting / Radix Sort": [r"counting_?sort", r"radix_?sort", r"count\[.*\]\s*\+="],
            "Timsort / Builtin Sort": [r"\.sort\(", r"sorted\("]
        }

        SEARCH_PATTERNS = {
            "Binary Search": [r"binary_?search", r"low\s*<=\s*high", r"mid\s*=\s*\(?low\s*\+\s*high\)?\s*//\s*2"],
            "Breadth First Search (BFS)": [r"bfs\(", r"breadth_first", r"deque\(", r"popleft\("],
            "Depth First Search (DFS)": [r"dfs\(", r"depth_first", r"visited\.add\(", r"stack\.pop\("],
            "Dijkstra Shortest Path": [r"dijkstra", r"heapq\.heappush\(.*distance", r"dist\[.*\]\s*=\s*min"],
            "Dynamic Programming (Memoization/Tabulation)": [r"memo\s*=\s*\{\}", r"dp\s*=\s*\[.*\]\s*\*\s*", r"@lru_cache"]
        }

        for p in py_files:
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    code_str = f.read()

                # AST Parse to get function definitions
                func_names = []
                try:
                    tree = ast.parse(code_str)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            func_names.append(node.name)
                        elif isinstance(node, ast.ClassDef):
                            func_names.append(f"Class: {node.name}")
                except Exception:
                    pass

                found_sorting = []
                for algo, patterns in SORTING_PATTERNS.items():
                    for pat in patterns:
                        if re.search(pat, code_str, re.IGNORECASE):
                            found_sorting.append(algo)
                            break

                found_search = []
                for algo, patterns in SEARCH_PATTERNS.items():
                    for pat in patterns:
                        if re.search(pat, code_str, re.IGNORECASE):
                            found_search.append(algo)
                            break

                if found_sorting or found_search or func_names:
                    detected_results.append({
                        "file_name": p.name,
                        "file_path": str(p.resolve()),
                        "relative_path": str(p.relative_to(resolved)) if resolved.is_dir() else p.name,
                        "contains_sorting": len(found_sorting) > 0,
                        "sorting_algorithms": found_sorting,
                        "search_algorithms": found_search,
                        "functions_defined": func_names[:15],
                        "total_lines": len(code_str.splitlines())
                    })
            except Exception:
                pass

        return {
            "success": True,
            "target": str(resolved),
            "files_analyzed": len(py_files),
            "files_with_sorting": sum(1 for r in detected_results if r["contains_sorting"]),
            "results": detected_results
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def execute_terminal_command(command: str, working_directory: Optional[str] = None, timeout_seconds: int = 15) -> Dict[str, Any]:
    """
    Execute a shell command with safety guardrails.
    
    Args:
        command: Terminal command string.
        working_directory: Working directory to run command in.
        timeout_seconds: Maximum execution duration.
    """
    safe, reason = is_safe_command(command)
    if not safe:
        return {
            "success": False,
            "error": reason,
            "stdout": "",
            "stderr": "Safety policy violation"
        }

    try:
        cwd = resolve_path(working_directory) if working_directory else Path.cwd()
        if not cwd.exists() or not cwd.is_dir():
            cwd = Path.cwd()

        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds
        )

        return {
            "success": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": proc.stdout[:10000],
            "stderr": proc.stderr[:5000],
            "cwd": str(cwd)
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout_seconds} seconds",
            "stdout": "",
            "stderr": "Timeout expired"
        }
    except Exception as e:
        return {"success": False, "error": str(e), "stdout": "", "stderr": ""}


def get_system_overview() -> Dict[str, Any]:
    """
    Returns system environment details, user directories, and MCP status.
    """
    user_dirs = get_user_directories()
    return {
        "success": True,
        "platform": platform.system(),
        "platform_release": platform.release(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "user_directories": user_dirs,
        "pypdf_available": PYPDF_AVAILABLE,
        "tools_count": 9
    }


# Map of all registered tools with their schemas for MCP and LLM function calling
TOOL_DEFINITIONS = [
    {
        "name": "list_files",
        "description": "List files and subfolders in a target directory (e.g. 'Downloads', 'Documents', 'sandbox', or any directory path). Returns names, sizes, extensions, and timestamps.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory_path": {"type": "string", "description": "Target folder name or path (defaults to 'Downloads')"},
                "pattern": {"type": "string", "description": "Glob filter pattern (e.g. '*.pdf', '*.py', '*')"},
                "recursive": {"type": "boolean", "description": "Whether to list subfolders recursively"},
                "max_depth": {"type": "integer", "description": "Recursion depth limit (default 2)"}
            },
            "required": []
        }
    },
    {
        "name": "search_files",
        "description": "Search for files by filename keyword or grep within file contents (including PDFs, Python code, markdown, etc.).",
        "parameters": {
            "type": "object",
            "properties": {
                "search_term": {"type": "string", "description": "Search keyword or phrase to look for"},
                "directory_path": {"type": "string", "description": "Root directory to search inside (e.g. 'Downloads', 'Documents', '.')"},
                "search_type": {"type": "string", "enum": ["name", "content", "both"], "description": "Search in filenames, contents, or both"},
                "file_extension": {"type": "string", "description": "Optional file extension filter like '.pdf' or '.py'"}
            },
            "required": ["search_term"]
        }
    },
    {
        "name": "read_file_content",
        "description": "Read file text content. Automatically extracts text from PDF documents, source code (.py, .js, .json), markdown, and text files.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file to read (relative or absolute)"},
                "max_chars": {"type": "integer", "description": "Maximum characters to return (default 12000)"},
                "page_range": {"type": "string", "description": "For PDF files, specific pages e.g. '1-3' or '1'"}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "create_folder",
        "description": "Create a new folder or nested directory path (e.g. 'Downloads/Placement Prep' or 'Documents/Reports').",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "description": "Path of the folder to create"}
            },
            "required": ["folder_path"]
        }
    },
    {
        "name": "move_file",
        "description": "Move a file or folder from source path to destination path. Supports moving into directories.",
        "parameters": {
            "type": "object",
            "properties": {
                "source_path": {"type": "string", "description": "Path of file/folder to move"},
                "destination_path": {"type": "string", "description": "Target path or target folder"},
                "overwrite": {"type": "boolean", "description": "Whether to overwrite existing destination"}
            },
            "required": ["source_path", "destination_path"]
        }
    },
    {
        "name": "copy_file",
        "description": "Copy a file or directory to a new location.",
        "parameters": {
            "type": "object",
            "properties": {
                "source_path": {"type": "string", "description": "Source file path"},
                "destination_path": {"type": "string", "description": "Destination file path"},
                "overwrite": {"type": "boolean", "description": "Overwrite existing destination"}
            },
            "required": ["source_path", "destination_path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write or append text content to a file. Great for saving summaries, notes, or modified code.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Target file path"},
                "content": {"type": "string", "description": "Text content to write"},
                "mode": {"type": "string", "enum": ["write", "append"], "description": "Write mode"}
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "inspect_code_algorithms",
        "description": "Analyzes Python files in a directory or single file using AST parsing to detect sorting algorithms (QuickSort, MergeSort, BubbleSort, etc.) and search algorithms.",
        "parameters": {
            "type": "object",
            "properties": {
                "target_path": {"type": "string", "description": "Directory or .py file path to analyze (e.g. '.' or 'Downloads')"}
            },
            "required": []
        }
    },
    {
        "name": "execute_terminal_command",
        "description": "Execute a safe terminal/shell command and return stdout and stderr.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Command string to execute"},
                "working_directory": {"type": "string", "description": "Directory to execute command inside"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "get_system_overview",
        "description": "Get operating system details, user directories (Downloads, Documents, Desktop, Workspace), and environment status.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

def execute_tool_by_name(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool dynamically by name with arguments."""
    func_map = {
        "list_files": list_files,
        "search_files": search_files,
        "read_file_content": read_file_content,
        "create_folder": create_folder,
        "move_file": move_file,
        "copy_file": copy_file,
        "write_file": write_file,
        "inspect_code_algorithms": inspect_code_algorithms,
        "execute_terminal_command": execute_terminal_command,
        "get_system_overview": get_system_overview
    }
    
    if tool_name not in func_map:
        return {"success": False, "error": f"Unknown tool: '{tool_name}'"}
        
    func = func_map[tool_name]
    try:
        return func(**arguments)
    except TypeError as te:
        return {"success": False, "error": f"Invalid arguments for {tool_name}: {str(te)}"}
    except Exception as e:
        return {"success": False, "error": f"Error executing {tool_name}: {str(e)}"}
