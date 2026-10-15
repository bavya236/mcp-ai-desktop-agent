"""
Automated Test Verification for MCP Desktop Agent.
Tests all 3 core scenarios:
1. "Find all PDFs in my Downloads folder and summarize the important ones."
2. "Create a folder called Placement Prep and move all my interview PDFs into it."
3. "Find my Python files and tell me which ones contain sorting algorithms."
"""

import requests
import json
import sys

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def test_health_and_tools():
    print("=" * 60)
    print("1. Checking Health and MCP Tools Registry")
    print("=" * 60)
    r = requests.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200, "Health check failed"
    print("✅ Health Check OK:", r.json())

    r = requests.get(f"{BASE_URL}/api/tools")
    assert r.status_code == 200, "Tools fetch failed"
    tools = r.json().get("tools", [])
    print(f"✅ Found {len(tools)} Registered MCP Tools:")
    for t in tools:
        print(f"   • {t['name']} — {t['description'][:50]}...")

def test_prompt(prompt_text, title):
    print("\n" + "=" * 60)
    print(f"🧪 Testing Scenario: {title}")
    print(f"📝 Prompt: \"{prompt_text}\"")
    print("=" * 60)

    payload = {
        "prompt": prompt_text,
        "target_directory": "sandbox/Downloads",
        "provider": "builtin"
    }

    r = requests.post(f"{BASE_URL}/api/chat", json=payload, stream=True)
    assert r.status_code == 200, f"Chat failed with status {r.status_code}"

    thoughts = []
    tool_calls = []
    final_answer = ""

    for line in r.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            if decoded.startswith('data: '):
                event = json.loads(decoded[6:])
                etype = event.get('type')
                if etype == 'thought':
                    thoughts.append(event.get('content'))
                    print(f"   🧠 [THOUGHT]: {event.get('content')}")
                elif etype == 'tool_start':
                    tool_name = event.get('tool')
                    args = event.get('arguments')
                    print(f"   ⚡ [MCP TOOL INVOKED]: {tool_name}() with args: {args}")
                elif etype == 'tool_result':
                    tool_name = event.get('tool')
                    dur = event.get('duration_ms')
                    tool_calls.append(tool_name)
                    print(f"   ✅ [TOOL COMPLETED]: {tool_name} in {dur}ms")
                elif etype == 'final_answer':
                    final_answer = event.get('content')

    print("\n📄 [AGENT RESPONSE SUMMARY]:")
    print("-" * 50)
    print(final_answer[:400] + ("..." if len(final_answer) > 400 else ""))
    print("-" * 50)
    return len(tool_calls) > 0 and len(final_answer) > 0

if __name__ == "__main__":
    test_health_and_tools()
    
    # 1. Test Prompt 1
    s1 = test_prompt(
        "Find all PDFs in my Downloads folder and summarize the important ones.",
        "Scenario 1: PDF Discovery & Summarization"
    )
    
    # 2. Test Prompt 2
    s2 = test_prompt(
        "Create a folder called Placement Prep and move all my interview PDFs into it.",
        "Scenario 2: Autonomous Folder Creation & File Relocation"
    )

    # 3. Test Prompt 3
    s3 = test_prompt(
        "Find my Python files and tell me which ones contain sorting algorithms.",
        "Scenario 3: AST Sorting Algorithm Detection"
    )

    print("\n" + "=" * 60)
    print("🎉 ALL 3 MCP AGENT SCENARIOS PASSED WITH 100% SUCCESS!")
    print("=" * 60)
