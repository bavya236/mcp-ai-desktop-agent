# 🧠 Talk to Your Computer — MCP AI Desktop Agent

> **An autonomous Desktop AI Agent powered by the Model Context Protocol (MCP).**
> Directly operate your computer via voice or natural language instructions: organize files, extract & summarize PDFs, detect algorithms in code, and run safe shell commands.

![MCP Desktop Agent Banner](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6366f1?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS_v4-38B2AC?style=for-the-badge&logo=tailwind_css&logoColor=white)

---

## 🌟 Key Capabilities

1. **📄 PDF Discovery & Smart Summarization:**
   - Automatically searches designated directories (e.g. `Downloads`, `Documents`, `sandbox`).
   - Extracts text streams from binary PDF files using `pypdf`.
   - Synthesizes executive summaries with importance classification (e.g. Interview Guides vs Bills).

2. **📁 Autonomous File Organization:**
   - *"Create a folder called Placement Prep and move all my interview PDFs into it."*
   - Multi-step reasoning: plans folder creation, identifies candidate files, moves files safely, and verifies results.

3. **🐍 Static AST Algorithm Inspection:**
   - *"Find my Python files and tell me which ones contain sorting algorithms."*
   - Uses Python AST analysis to detect QuickSort, MergeSort, BubbleSort, HeapSort, and Search algorithms without executing untrusted code.

4. **⚡ Model Context Protocol (MCP) Standard Compliance:**
   - Implements a standalone FastMCP server over JSON-RPC 2.0.
   - Fully compatible with **Claude Desktop**, **Cursor IDE**, and custom Agent runtimes.

5. **🎙️ Voice Dictation & Futuristic Glassmorphism GUI:**
   - Web Speech API integration for speech-to-text.
   - Real-time ReAct loop visualization: live tool invocations, duration benchmarks (`ms`), argument inspectors, and observation outputs.
   - Live Sandbox file explorer with in-app file previewer.

---

## 🚀 Quick Start (1-Click Run)

### 1. Prerequisites
- Python 3.10+
- Node.js 18+

### 2. Launch Everything (Backend + Frontend + Sandbox)
```bash
python start.py
```
This will:
1. Automatically populate the demo sandbox with sample interview PDFs and Python files.
2. Start the FastAPI backend on `http://localhost:8000`.
3. Start the Vite React frontend on `http://localhost:5173`.
4. Open your browser to the agent dashboard!

---

## 🛠️ Manual Execution (Alternative)

### Backend:
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies (if not done)
pip install -r backend/requirements.txt

# Run FastAPI backend
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## 🔌 Connecting to Claude Desktop / Cursor IDE

Add the following to your Claude Desktop config file (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "desktop-automation": {
      "command": "python",
      "args": [
        "c:/Users/bavya/OneDrive/Documents/mcp_new/backend/mcp_server.py"
      ]
    }
  }
}
```

---

## 📂 Project Structure

```
mcp_new/
├── backend/
│   ├── app.py                   # FastAPI REST & SSE Streaming server
│   ├── mcp_server.py            # Standalone FastMCP Server (stdio)
│   ├── agent_engine.py          # Multi-turn ReAct Agent (Gemini/OpenAI/Builtin)
│   ├── tool_registry.py         # Concrete MCP tool functions & schemas
│   ├── system_utils.py          # Safe path resolution & security checks
│   ├── sample_data_gen.py       # 1-click test file & PDF generator
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx               # Header & folder switcher
│   │   │   ├── QuickPromptBar.jsx       # 1-click test prompt scenarios
│   │   │   ├── ChatArea.jsx             # Voice/Text chat & live tool cards
│   │   │   ├── FileExplorerPanel.jsx    # Live directory monitor & file previewer
│   │   │   ├── ToolCatalogModal.jsx     # MCP tool registry & tester
│   │   │   ├── ArchitectureDiagram.jsx  # System architecture & interview guide
│   │   │   └── SettingsModal.jsx        # LLM provider & API key config
│   │   ├── App.jsx                      # Main dashboard controller
│   │   └── index.css                    # Glassmorphism & design system
│   └── package.json
├── claude_desktop_config.json   # Ready-to-use MCP configuration
├── INTERVIEW_TALKING_POINTS.md  # Detailed interview Q&A and architecture guide
├── start.py                     # 1-click launcher
└── README.md
```

---

## 🏆 Interview Wow Factors

- **MCP Protocol Implementation:** Demonstrates deep understanding of open agent protocols, tool calling schemas, and JSON-RPC 2.0.
- **Dynamic ReAct Feedback Loop:** Real-time thought planning, tool execution, and error recovery.
- **Safe Static Code Analysis:** Analyzes source code using AST patterns rather than unsafe execution.
- **Full-Stack Polish:** Beautiful glassmorphism UI, real-time SSE streaming, voice dictation, and zero-setup demo sandbox.
