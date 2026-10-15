"""
FastAPI Server for MCP AI Desktop Agent.
Provides REST and Streaming SSE endpoints for the frontend desktop dashboard.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from backend.tool_registry import (
    TOOL_DEFINITIONS,
    execute_tool_by_name,
    get_system_overview,
    list_files
)
from backend.agent_engine import get_agent
from backend.sample_data_gen import populate_sandbox
from backend.system_utils import get_user_directories, resolve_path

app = FastAPI(
    title="Talk to Your Computer - MCP AI Desktop Agent",
    description="Operate your computer via Model Context Protocol (MCP) tools and AI agent reasoning.",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str
    target_directory: str = "Downloads"
    provider: str = "builtin"  # "builtin", "gemini", "openai", "ollama"
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None


class ToolExecuteRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "mcp-desktop-agent"}


@app.get("/api/system")
async def system_status():
    """Returns system status, directory paths, and available tools."""
    overview = get_system_overview()
    return overview


@app.get("/api/tools")
async def get_tools():
    """Returns the full list of MCP tool definitions and schemas."""
    return {
        "count": len(TOOL_DEFINITIONS),
        "tools": TOOL_DEFINITIONS
    }


@app.post("/api/tools/execute")
async def execute_tool(req: ToolExecuteRequest):
    """Directly execute any MCP tool."""
    res = execute_tool_by_name(req.tool_name, req.arguments)
    return res


@app.get("/api/files/browse")
async def browse_files(directory: str = "Downloads", pattern: str = "*"):
    """Browse files in a directory for the frontend file explorer."""
    res = list_files(directory_path=directory, pattern=pattern, recursive=False)
    return res


@app.post("/api/sandbox/populate")
async def populate_sandbox_endpoint(target: str = "sandbox/Downloads"):
    """Generates realistic sample interview PDFs and Python sorting code files."""
    res = populate_sandbox(target)
    return res


@app.post("/api/chat")
async def chat_stream(req: ChatRequest):
    """
    Streaming agent endpoint. Emits SSE stream of thoughts, tool calls, and final response.
    """
    agent = get_agent(
        provider=req.provider,
        api_key=req.api_key,
        model=req.model,
        base_url=req.base_url
    )

    async def event_generator():
        try:
            async for event in agent.run(req.prompt, req.target_directory):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            error_event = {"type": "error", "content": f"Agent error: {str(e)}"}
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


if __name__ == "__main__":
    import uvicorn
    # Make sure sample sandbox exists initially
    sandbox_path = Path("sandbox/Downloads")
    if not sandbox_path.exists() or len(list(sandbox_path.iterdir())) == 0:
        populate_sandbox("sandbox/Downloads")
        
    print("\n🚀 Starting MCP AI Desktop Agent Backend on http://localhost:8000")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
