"""
Standard Model Context Protocol (MCP) Server for Desktop Automation.
Exposes filesystem, search, PDF reading, code analysis, and terminal tools.

Can be run directly via stdio (for Claude Desktop, Cursor, Antigravity)
or imported into the Desktop Agent web runtime.
"""

import sys
import os
from pathlib import Path

# Add parent directory to sys.path so imports work cleanly
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP

from backend.tool_registry import (
    list_files as core_list_files,
    search_files as core_search_files,
    read_file_content as core_read_file_content,
    create_folder as core_create_folder,
    move_file as core_move_file,
    copy_file as core_copy_file,
    write_file as core_write_file,
    inspect_code_algorithms as core_inspect_code_algorithms,
    execute_terminal_command as core_execute_terminal_command,
    get_system_overview as core_get_system_overview,
    TOOL_DEFINITIONS
)

# Initialize FastMCP Server
mcp = FastMCP("DesktopAutomationMCP")


@mcp.tool()
def list_files(
    directory_path: str = "Downloads",
    pattern: str = "*",
    recursive: bool = False,
    max_depth: int = 2
) -> str:
    """
    List files and folders in a target directory (e.g. 'Downloads', 'Documents', 'sandbox', or an absolute path).
    """
    import json
    res = core_list_files(directory_path, pattern, recursive, max_depth)
    return json.dumps(res, indent=2)


@mcp.tool()
def search_files(
    search_term: str,
    directory_path: str = ".",
    search_type: str = "both",
    file_extension: str = ""
) -> str:
    """
    Search for files by name keyword or grep contents (including PDFs, Python code, text).
    """
    import json
    ext = file_extension if file_extension else None
    res = core_search_files(search_term, directory_path, search_type, ext)
    return json.dumps(res, indent=2)


@mcp.tool()
def read_file(
    file_path: str,
    max_chars: int = 12000,
    page_range: str = ""
) -> str:
    """
    Read file text content. Automatically extracts text from PDF documents, python source code, markdown, etc.
    """
    import json
    pr = page_range if page_range else None
    res = core_read_file_content(file_path, max_chars, pr)
    return json.dumps(res, indent=2)


@mcp.tool()
def create_folder(folder_path: str) -> str:
    """
    Create a new folder or nested directory (e.g. 'Downloads/Placement Prep' or 'Documents/Archive').
    """
    import json
    res = core_create_folder(folder_path)
    return json.dumps(res, indent=2)


@mcp.tool()
def move_file(source_path: str, destination_path: str, overwrite: bool = False) -> str:
    """
    Move a file or folder to a new destination folder or path.
    """
    import json
    res = core_move_file(source_path, destination_path, overwrite)
    return json.dumps(res, indent=2)


@mcp.tool()
def copy_file(source_path: str, destination_path: str, overwrite: bool = False) -> str:
    """
    Copy a file or directory to a target path.
    """
    import json
    res = core_copy_file(source_path, destination_path, overwrite)
    return json.dumps(res, indent=2)


@mcp.tool()
def write_file(file_path: str, content: str, mode: str = "write") -> str:
    """
    Write or append text content to a file (great for saving summaries, notes, or code).
    """
    import json
    res = core_write_file(file_path, content, mode)
    return json.dumps(res, indent=2)


@mcp.tool()
def inspect_code_algorithms(target_path: str = ".") -> str:
    """
    Analyzes Python files using AST parsing to detect sorting algorithms (QuickSort, MergeSort, BubbleSort, HeapSort, etc.) and search algorithms.
    """
    import json
    res = core_inspect_code_algorithms(target_path)
    return json.dumps(res, indent=2)


@mcp.tool()
def execute_terminal_command(command: str, working_directory: str = ".") -> str:
    """
    Execute a safe shell command and return stdout/stderr.
    """
    import json
    res = core_execute_terminal_command(command, working_directory)
    return json.dumps(res, indent=2)


@mcp.tool()
def get_system_overview() -> str:
    """
    Get operating system details, user directories, and environment status.
    """
    import json
    res = core_get_system_overview()
    return json.dumps(res, indent=2)


if __name__ == "__main__":
    # When run directly, starts the standard MCP stdio server
    mcp.run(transport="stdio")
