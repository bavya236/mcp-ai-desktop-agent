"""
System Utilities for MCP AI Desktop Agent.
Handles safe path resolution, user directory detection, and safety safeguards.
"""

import os
import sys
import platform
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List

# Get standard user directories across Windows / macOS / Linux
def get_user_directories() -> Dict[str, str]:
    home = Path.home()
    
    # Common user directories
    dirs = {
        "home": str(home),
        "downloads": str(home / "Downloads"),
        "documents": str(home / "Documents"),
        "desktop": str(home / "Desktop"),
        "pictures": str(home / "Pictures"),
        "videos": str(home / "Videos"),
        "music": str(home / "Music"),
        "workspace": str(Path.cwd().resolve()),
        "sandbox": str((Path.cwd() / "sandbox").resolve())
    }
    
    # Ensure Windows path casing / existing checks
    for key, path_str in list(dirs.items()):
        p = Path(path_str)
        if not p.exists() and key not in ["sandbox", "workspace"]:
            # fallback or leave as is
            pass
            
    return dirs

def resolve_path(path_str: str, base_dir: Optional[str] = None) -> Path:
    """
    Intelligently resolves paths including shortcuts like:
    - 'Downloads', 'downloads', '~/Downloads'
    - 'Documents', 'desktop', 'sandbox'
    - relative paths to base_dir or current working directory
    - absolute Windows / POSIX paths
    """
    if not path_str or not path_str.strip():
        return Path.cwd().resolve()
        
    cleaned = path_str.strip().strip('"\'')
    
    # Check for known folder aliases
    user_dirs = get_user_directories()
    alias_lower = cleaned.lower().rstrip("/\\")
    
    if alias_lower in ["downloads", "download", "~/downloads"]:
        return Path(user_dirs["downloads"]).resolve()
    elif alias_lower in ["documents", "document", "~/documents", "docs"]:
        return Path(user_dirs["documents"]).resolve()
    elif alias_lower in ["desktop", "~/desktop"]:
        return Path(user_dirs["desktop"]).resolve()
    elif alias_lower in ["sandbox", "~/sandbox", "./sandbox"]:
        return Path(user_dirs["sandbox"]).resolve()
    elif alias_lower in ["home", "~"]:
        return Path(user_dirs["home"]).resolve()
    elif alias_lower in ["workspace", ".", "./"]:
        return Path.cwd().resolve()
        
    # Check if starts with alias like 'Downloads/something' or 'sandbox/...'
    for alias in ["downloads", "documents", "desktop", "sandbox", "home"]:
        prefix = alias + "/"
        prefix_win = alias + "\\"
        if cleaned.lower().startswith(prefix) or cleaned.lower().startswith(prefix_win):
            remainder = cleaned[len(prefix):]
            return (Path(user_dirs[alias]) / remainder).resolve()

    # Expand tilde ~
    expanded = os.path.expanduser(cleaned)
    p = Path(expanded)
    
    if p.is_absolute():
        return p.resolve()
        
    if base_dir:
        base = Path(base_dir).resolve()
        return (base / p).resolve()
        
    return (Path.cwd() / p).resolve()

# Dangerous patterns filter for execution / deletion safety
DANGEROUS_COMMANDS = [
    "format ", "del /f /s /q c:", "rmdir /s /q c:", "rm -rf /", 
    "mkfs", "dd if=", ":(){ :|:& };:", "drop database", "sudo rm",
    "> /dev/sda", "chmod -r 777 /", "powershell -c remove-item -recurse c:\\"
]

def is_safe_command(command: str) -> tuple[bool, str]:
    cmd_lower = command.lower().strip()
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in cmd_lower:
            return False, f"Command blocked by safety guardrail: contains dangerous pattern '{dangerous}'"
    return True, "Safe"

def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
