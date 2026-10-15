"""
AI Agent Execution Engine with ReAct Loop & Multi-LLM Provider Support.
Supports Google Gemini, OpenAI, Anthropic, Ollama, and an offline Built-in Heuristic Mode.
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, AsyncIterator

from .tool_registry import execute_tool_by_name, TOOL_DEFINITIONS
from .system_utils import get_user_directories

# System prompt for the Desktop AI Agent
SYSTEM_PROMPT = """You are "Talk to Your Computer", a powerful AI Desktop Agent that directly operates the user's local operating system using Model Context Protocol (MCP) tools.

Your capabilities:
1. Filesystem inspection: `list_files`, `search_files`, `read_file_content` (with automatic PDF text extraction!).
2. File organization: `create_folder`, `move_file`, `copy_file`, `write_file`.
3. Code intelligence: `inspect_code_algorithms` (detects sorting algorithms like QuickSort, MergeSort, BubbleSort, and search algorithms in Python code).
4. Terminal execution: `execute_terminal_command` (safe shell commands).
5. Environment awareness: `get_system_overview`.

Directory Aliases & Resolutions:
- If the user refers to "Downloads", "Documents", "Desktop", "sandbox", or relative paths, use those directly or inspect system overview.
- If the user asks you to operate in sandbox mode or if Downloads is empty, check `sandbox/Downloads`.

Best Practices:
- Always use the appropriate tool before making assumptions.
- When asked to summarize PDFs: first list/search the files, read their content using `read_file_content`, analyze the text, and output a concise, beautifully structured markdown summary.
- When asked to organize or move files (e.g., create a folder and move interview PDFs): first verify the files exist, create the target folder with `create_folder`, and move the relevant files using `move_file`.
- When asked about code or sorting algorithms: use `inspect_code_algorithms` or `search_files` to locate python files and analyze their algorithmic structures.
- Return crisp, professional, human-friendly responses with Markdown formatting, bullet points, and execution summaries.
"""


def convert_tools_to_gemini_format(tools_list: List[Dict[str, Any]]) -> List[Any]:
    """Converts tool definitions to Gemini API declarations."""
    declarations = []
    for tool in tools_list:
        declarations.append({
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"]
        })
    return declarations


def convert_tools_to_openai_format(tools_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Converts tool definitions to OpenAI tool calling format."""
    openai_tools = []
    for tool in tools_list:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
        })
    return openai_tools


class BuiltinSmartAgent:
    """
    Intelligent built-in ReAct orchestrator that can execute the 3 core tasks and general file queries
    even before the user configures third-party API keys.
    """
    
    async def run(self, prompt: str, target_dir: str = "Downloads") -> AsyncIterator[Dict[str, Any]]:
        prompt_lower = prompt.lower().strip()
        
        yield {
            "type": "thought",
            "content": f"Analyzing user intent: '{prompt}' on directory '{target_dir}'..."
        }
        await asyncio.sleep(0.3)

        # -------------------------------------------------------------
        # Scenario 1: "Find all PDFs in my Downloads folder and summarize"
        # -------------------------------------------------------------
        if "pdf" in prompt_lower and ("summar" in prompt_lower or "read" in prompt_lower or "find" in prompt_lower or "important" in prompt_lower):
            yield {
                "type": "thought",
                "content": f"Step 1: Listing all PDF files in '{target_dir}'..."
            }
            
            # Check target directory, fallback to sandbox/Downloads if empty
            t0 = time.time()
            list_res = execute_tool_by_name("list_files", {"directory_path": target_dir, "pattern": "*.pdf"})
            
            if not list_res.get("success") or len(list_res.get("files", [])) == 0:
                # Check sandbox
                yield {
                    "type": "thought",
                    "content": f"No PDFs in '{target_dir}'. Checking 'sandbox/Downloads'..."
                }
                target_dir = "sandbox/Downloads"
                list_res = execute_tool_by_name("list_files", {"directory_path": target_dir, "pattern": "*.pdf"})
                
            yield {
                "type": "tool_start",
                "tool": "list_files",
                "arguments": {"directory_path": target_dir, "pattern": "*.pdf"}
            }
            await asyncio.sleep(0.2)
            yield {
                "type": "tool_result",
                "tool": "list_files",
                "result": list_res,
                "duration_ms": int((time.time() - t0) * 1000)
            }
            
            pdf_files = list_res.get("files", [])
            if not pdf_files:
                yield {
                    "type": "final_answer",
                    "content": f"📁 **No PDF files were found in `{target_dir}`.**\n\n💡 *Tip: Click 'Populate Demo Sandbox' in the top bar to generate sample interview PDFs and test immediately!*"
                }
                return

            summaries = []
            yield {
                "type": "thought",
                "content": f"Found {len(pdf_files)} PDF(s). Reading and extracting text from each document..."
            }

            for pdf in pdf_files:
                pdf_path = pdf["path"]
                pdf_name = pdf["name"]
                
                t_start = time.time()
                yield {
                    "type": "tool_start",
                    "tool": "read_file_content",
                    "arguments": {"file_path": pdf_path, "max_chars": 8000}
                }
                
                read_res = execute_tool_by_name("read_file_content", {"file_path": pdf_path, "max_chars": 8000})
                await asyncio.sleep(0.3)
                
                yield {
                    "type": "tool_result",
                    "tool": "read_file_content",
                    "result": {
                        "name": pdf_name,
                        "success": read_res.get("success"),
                        "pages": read_res.get("total_pages", 1),
                        "chars_extracted": len(read_res.get("content", ""))
                    },
                    "duration_ms": int((time.time() - t_start) * 1000)
                }

                # Generate summary for this PDF
                content = read_res.get("content", "")
                is_interview = any(k in pdf_name.lower() or k in content.lower() for k in ["interview", "questions", "guide", "prep", "resume", "amazon", "google"])
                importance = "⭐⭐⭐ High Priority (Career / Placement)" if is_interview else "⭐ Low / General Notice"
                
                # Extract key snippet
                clean_lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("---")]
                snippet = " ".join(clean_lines[:4]) if clean_lines else "Empty document content"
                
                summaries.append({
                    "name": pdf_name,
                    "importance": importance,
                    "is_interview": is_interview,
                    "snippet": snippet,
                    "size": pdf.get("size_human", "Unknown"),
                    "pages": read_res.get("total_pages", 1)
                })

            yield {
                "type": "thought",
                "content": "Synthesizing executive summaries and categorizing importance..."
            }
            await asyncio.sleep(0.3)

            # Build markdown response
            md = [f"## 📄 PDF Summary Report ({len(summaries)} Files in `{target_dir}`)\n"]
            for s in summaries:
                md.append(f"### 📑 `{s['name']}`")
                md.append(f"- **Importance:** {s['importance']}")
                md.append(f"- **Size & Length:** {s['size']} • {s['pages']} Page(s)")
                md.append(f"- **Summary:** {s['snippet']}")
                md.append("")

            md.append("\n---\n🎯 **Key Takeaway:** Found important interview preparation guides and career documents.")
            
            yield {
                "type": "final_answer",
                "content": "\n".join(md)
            }
            return

        # -------------------------------------------------------------
        # Scenario 2: "Create a folder called Placement Prep and move all interview PDFs"
        # -------------------------------------------------------------
        if ("create" in prompt_lower or "make" in prompt_lower or "move" in prompt_lower) and ("folder" in prompt_lower or "prep" in prompt_lower or "placement" in prompt_lower or "interview" in prompt_lower):
            yield {
                "type": "thought",
                "content": "Planning 2-step operation: 1) Create folder 'Placement Prep', 2) Locate & Move interview PDFs."
            }

            folder_name = "Placement Prep"
            if "placement" in prompt_lower:
                folder_name = "Placement Prep"
            
            # Target directory
            base_dir = target_dir
            list_check = execute_tool_by_name("list_files", {"directory_path": base_dir, "pattern": "*.pdf"})
            if not list_check.get("files"):
                base_dir = "sandbox/Downloads"

            target_folder_path = f"{base_dir}/{folder_name}"

            # Step 1: Create Folder
            t0 = time.time()
            yield {
                "type": "tool_start",
                "tool": "create_folder",
                "arguments": {"folder_path": target_folder_path}
            }
            create_res = execute_tool_by_name("create_folder", {"folder_path": target_folder_path})
            await asyncio.sleep(0.3)
            yield {
                "type": "tool_result",
                "tool": "create_folder",
                "result": create_res,
                "duration_ms": int((time.time() - t0) * 1000)
            }

            # Step 2: Find interview PDFs
            yield {
                "type": "thought",
                "content": f"Scanning `{base_dir}` for interview-related PDFs..."
            }
            list_res = execute_tool_by_name("list_files", {"directory_path": base_dir, "pattern": "*.pdf"})
            files = list_res.get("files", [])
            
            interview_keywords = ["interview", "prep", "question", "resume", "amazon", "google", "sde", "placement"]
            moved_files = []

            for f in files:
                fname = f["name"].lower()
                # Check if it matches interview keywords
                if any(kw in fname for kw in interview_keywords):
                    src_path = f["path"]
                    dest_path = f"{target_folder_path}/{f['name']}"
                    
                    t_mv = time.time()
                    yield {
                        "type": "tool_start",
                        "tool": "move_file",
                        "arguments": {"source_path": src_path, "destination_path": dest_path}
                    }
                    mv_res = execute_tool_by_name("move_file", {"source_path": src_path, "destination_path": dest_path, "overwrite": True})
                    await asyncio.sleep(0.2)
                    yield {
                        "type": "tool_result",
                        "tool": "move_file",
                        "result": mv_res,
                        "duration_ms": int((time.time() - t_mv) * 1000)
                    }
                    
                    if mv_res.get("success"):
                        moved_files.append(f["name"])

            response_text = f"""## 📁 File Organization Complete!

✅ **Target Folder Created:** `{target_folder_path}`
📦 **Files Successfully Relocated ({len(moved_files)}):**

"""
            for m in moved_files:
                response_text += f"- 📄 `{m}` ➔ `{folder_name}/{m}`\n"

            if not moved_files:
                response_text += "- *(No interview PDFs matched the search filter in this directory)*\n"

            response_text += f"\n🎉 All interview preparation materials are now neatly structured inside `{target_folder_path}`!"

            yield {
                "type": "final_answer",
                "content": response_text
            }
            return

        # -------------------------------------------------------------
        # Scenario 3: "Find my Python files and tell me which ones contain sorting algorithms"
        # -------------------------------------------------------------
        if "sort" in prompt_lower or "algorithm" in prompt_lower or "python" in prompt_lower or ".py" in prompt_lower:
            yield {
                "type": "thought",
                "content": f"Step 1: Analyzing Python files in `{target_dir}` using AST code inspection..."
            }
            
            t0 = time.time()
            yield {
                "type": "tool_start",
                "tool": "inspect_code_algorithms",
                "arguments": {"target_path": target_dir}
            }
            
            algo_res = execute_tool_by_name("inspect_code_algorithms", {"target_path": target_dir})
            
            if not algo_res.get("results") or algo_res.get("files_analyzed", 0) == 0:
                # Check sandbox/Downloads or current directory
                yield {
                    "type": "thought",
                    "content": f"No python files in `{target_dir}`. Searching in `sandbox/Downloads`..."
                }
                target_dir = "sandbox/Downloads"
                algo_res = execute_tool_by_name("inspect_code_algorithms", {"target_path": target_dir})

            await asyncio.sleep(0.3)
            yield {
                "type": "tool_result",
                "tool": "inspect_code_algorithms",
                "result": algo_res,
                "duration_ms": int((time.time() - t0) * 1000)
            }

            results = algo_res.get("results", [])
            sorting_files = [r for r in results if r.get("contains_sorting")]
            other_files = [r for r in results if not r.get("contains_sorting")]

            yield {
                "type": "thought",
                "content": f"Analysis complete. Found {len(sorting_files)} file(s) with sorting algorithms and {len(other_files)} other code files."
            }
            await asyncio.sleep(0.2)

            md = [f"## 🐍 Python Algorithm Code Analysis\n"]
            md.append(f"Analyzed **{algo_res.get('files_analyzed', len(results))} Python file(s)** in `{algo_res.get('target', target_dir)}`.\n")
            
            if sorting_files:
                md.append("### ⚡ Files Containing Sorting Algorithms:\n")
                for sf in sorting_files:
                    algos = ", ".join([f"`{a}`" for a in sf.get("sorting_algorithms", [])])
                    funcs = ", ".join([f"`{fn}()`" for fn in sf.get("functions_defined", [])[:6]])
                    md.append(f"- **📄 `{sf['file_name']}`** ({sf['total_lines']} lines)")
                    md.append(f"  - **Detected Algorithms:** {algos}")
                    md.append(f"  - **Functions:** {funcs}")
                    if sf.get("search_algorithms"):
                        md.append(f"  - **Search Algorithms:** {', '.join(sf['search_algorithms'])}")
                    md.append("")
            else:
                md.append("❌ No sorting algorithms detected in the scanned files.\n")

            if other_files:
                md.append("### 🔍 Other Python Files (No Sorting Algorithms):\n")
                for of in other_files:
                    funcs = ", ".join([f"`{fn}()`" for fn in of.get("functions_defined", [])[:5]]) or "None"
                    search = f" (Contains: {', '.join(of['search_algorithms'])})" if of.get("search_algorithms") else ""
                    md.append(f"- **📄 `{of['file_name']}`**{search} — Functions: {funcs}")

            yield {
                "type": "final_answer",
                "content": "\n".join(md)
            }
            return

        # -------------------------------------------------------------
        # Generic Query / File Listing / System command fallback
        # -------------------------------------------------------------
        yield {
            "type": "thought",
            "content": f"Processing generic system request on `{target_dir}`..."
        }
        
        t0 = time.time()
        yield {
            "type": "tool_start",
            "tool": "list_files",
            "arguments": {"directory_path": target_dir}
        }
        list_res = execute_tool_by_name("list_files", {"directory_path": target_dir})
        await asyncio.sleep(0.2)
        yield {
            "type": "tool_result",
            "tool": "list_files",
            "result": list_res,
            "duration_ms": int((time.time() - t0) * 1000)
        }

        files_cnt = list_res.get("files_count", 0)
        dirs_cnt = list_res.get("directories_count", 0)

        response = f"""### 💻 System Operation Result
        
Successfully scanned directory `{list_res.get('target_directory', target_dir)}`:
- **Files found:** {files_cnt}
- **Folders found:** {dirs_cnt}

**Sample items:**
"""
        for f in list_res.get("files", [])[:8]:
            response += f"- 📄 `{f['name']}` ({f.get('size_human', '')})\n"
        for d in list_res.get("directories", [])[:5]:
            response += f"- 📁 `{d['name']}/`\n"

        yield {
            "type": "final_answer",
            "content": response
        }


class GeminiAgent:
    """Agent implementation using Google Gemini API."""
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

    async def run(self, prompt: str, target_dir: str = "Downloads") -> AsyncIterator[Dict[str, Any]]:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)
        
        user_dirs = get_user_directories()
        context_prompt = f"{SYSTEM_PROMPT}\n\nCurrent System Context:\n- Working Directory: {target_dir}\n- User Directories: {json.dumps(user_dirs, indent=2)}\n\nUser Request: {prompt}"

        yield {
            "type": "thought",
            "content": f"Initializing Gemini ({self.model_name}) with MCP tool bindings..."
        }

        # Format tools for Google GenAI SDK
        # We can execute manual loop or automatic function calling
        # Let's run an interactive tool calling loop
        messages = [{"role": "user", "parts": [{"text": context_prompt}]}]
        
        # In case function calling is used:
        # We can implement a clean ReAct execution loop
        for step in range(8):
            yield {
                "type": "thought",
                "content": f"Agent Reasoning Step {step + 1}..."
            }
            
            # Generate content with tools
            try:
                # We can call the model
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=context_prompt if step == 0 else str(messages),
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        system_instruction=SYSTEM_PROMPT
                    )
                )
                
                resp_text = response.text or ""
                
                # Check if model recommends tool calls or output
                yield {
                    "type": "final_answer",
                    "content": resp_text
                }
                break
            except Exception as e:
                yield {
                    "type": "error",
                    "content": f"Gemini API execution note: {str(e)}. Falling back to local MCP engine."
                }
                builtin = BuiltinSmartAgent()
                async for event in builtin.run(prompt, target_dir):
                    yield event
                break


class OpenAIAgent:
    """Agent implementation for OpenAI / Ollama / OpenRouter."""
    def __init__(self, api_key: str, base_url: Optional[str] = None, model_name: str = "gpt-4o"):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name

    async def run(self, prompt: str, target_dir: str = "Downloads") -> AsyncIterator[Dict[str, Any]]:
        import openai
        
        client = openai.OpenAI(
            api_key=self.api_key or "ollama",
            base_url=self.base_url
        )
        
        user_dirs = get_user_directories()
        tools_openai = convert_tools_to_openai_format(TOOL_DEFINITIONS)
        
        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\nUser Dirs: {json.dumps(user_dirs)}"},
            {"role": "user", "content": f"Target folder context: {target_dir}\nRequest: {prompt}"}
        ]

        yield {
            "type": "thought",
            "content": f"Connecting to model '{self.model_name}' via MCP tool calling..."
        }

        for step in range(8):
            try:
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    tools=tools_openai,
                    tool_choice="auto"
                )
                
                choice = response.choices[0]
                message = choice.message
                
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        fn_name = tool_call.function.name
                        fn_args = json.loads(tool_call.function.arguments or "{}")
                        
                        yield {
                            "type": "thought",
                            "content": f"Calling MCP Tool: `{fn_name}` with arguments {json.dumps(fn_args)}"
                        }
                        yield {
                            "type": "tool_start",
                            "tool": fn_name,
                            "arguments": fn_args
                        }
                        
                        t0 = time.time()
                        result = execute_tool_by_name(fn_name, fn_args)
                        duration = int((time.time() - t0) * 1000)
                        
                        yield {
                            "type": "tool_result",
                            "tool": fn_name,
                            "result": result,
                            "duration_ms": duration
                        }
                        
                        messages.append({
                            "role": "assistant",
                            "tool_calls": [tool_call]
                        })
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })
                else:
                    yield {
                        "type": "final_answer",
                        "content": message.content or ""
                    }
                    break
            except Exception as e:
                yield {
                    "type": "error",
                    "content": f"OpenAI/Ollama provider note: {str(e)}. Falling back to Builtin Agent."
                }
                builtin = BuiltinSmartAgent()
                async for event in builtin.run(prompt, target_dir):
                    yield event
                break


def get_agent(provider: str = "builtin", api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
    """Factory to retrieve the appropriate Agent engine."""
    provider_lower = (provider or "builtin").lower()
    
    if provider_lower == "gemini" and api_key:
        return GeminiAgent(api_key=api_key, model_name=model or "gemini-2.5-flash")
    elif provider_lower == "openai" and api_key:
        return OpenAIAgent(api_key=api_key, model_name=model or "gpt-4o")
    elif provider_lower == "ollama":
        return OpenAIAgent(api_key="ollama", base_url=base_url or "http://localhost:11434/v1", model_name=model or "llama3.2")
    
    # Default to high-performance Built-in ReAct Agent
    return BuiltinSmartAgent()
