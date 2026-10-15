"""
Sample Test Data Generator for MCP Desktop Agent.
Generates realistic PDF files and Python algorithm files in a sandbox directory
so you can immediately test and demo all 3 prompt scenarios!
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

try:
    import pypdf
    from pypdf import PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


def create_simple_pdf(output_path: Path, title: str, paragraphs: list[str]):
    """
    Creates a valid PDF document with text stream content.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # We can write a clean, standard compliant PDF byte stream directly
    # or using pypdf / raw PDF specification
    lines_content = [f"BT /F1 16 Tf 50 750 Td ({title}) Tj ET"]
    y_pos = 710
    
    for para in paragraphs:
        # split into manageable lines
        words = para.split()
        current_line = []
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 75:
                line_str = " ".join(current_line[:-1]).replace("(", "\\(").replace(")", "\\)")
                lines_content.append(f"BT /F1 11 Tf 50 {y_pos} Td ({line_str}) Tj ET")
                y_pos -= 16
                current_line = [word]
                if y_pos < 60:
                    break
        if current_line and y_pos >= 60:
            line_str = " ".join(current_line).replace("(", "\\(").replace(")", "\\)")
            lines_content.append(f"BT /F1 11 Tf 50 {y_pos} Td ({line_str}) Tj ET")
            y_pos -= 24
            
    stream_data = "\n".join(lines_content).encode("latin-1", "ignore")
    stream_len = len(stream_data)
    
    pdf_template = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length {stream_len} >>
stream
""".encode("latin-1") + stream_data + f"""
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000234 00000 n 
0000000{234 + stream_len + 35:03d} 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
{234 + stream_len + 110}
%%EOF
""".encode("latin-1")

    with open(output_path, "wb") as f:
        f.write(pdf_template)


SAMPLE_PYTHON_FILES = {
    "sorting_algorithms_collection.py": '''"""
Sorting Algorithms Implementation and Benchmarks
Contains: Quick Sort, Merge Sort, and Bubble Sort
"""
import random
import time

def bubble_sort(arr):
    """Classic Bubble Sort algorithm - O(n^2)"""
    n = len(arr)
    arr = list(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def quick_sort(arr):
    """Divide and Conquer Quick Sort - O(n log n) average"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def merge_sort(arr):
    """Stable Merge Sort algorithm - O(n log n)"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged

if __name__ == "__main__":
    test_data = [random.randint(1, 1000) for _ in range(50)]
    print("Bubble sorted:", bubble_sort(test_data[:10]))
    print("Quick sorted:", quick_sort(test_data[:10]))
    print("Merge sorted:", merge_sort(test_data[:10]))
''',

    "heap_and_insertion_sort.py": '''"""
Heap Sort and Insertion Sort algorithms.
"""
def insertion_sort(arr):
    """In-place Insertion Sort - O(n^2)"""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

def heap_sort(arr):
    """Heap Sort using binary heap - O(n log n)"""
    import heapq
    heap = list(arr)
    heapq.heapify(heap)
    return [heapq.heappop(heap) for _ in range(len(heap))]
''',

    "binary_search_rotated.py": '''"""
Search in Rotated Sorted Array algorithm.
"""
def search_in_rotated_array(nums, target):
    """Modified Binary Search - O(log n) time complexity"""
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = (low + high) // 2
        if nums[mid] == target:
            return mid
        # Left half is sorted
        if nums[low] <= nums[mid]:
            if nums[low] <= target < nums[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:
            if nums[mid] < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1
    return -1
''',

    "user_auth_service.py": '''"""
Web Authentication Service (No Sorting Algorithms here)
"""
from datetime import datetime, timedelta
import hashlib

class AuthService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.users_db = {}
        
    def hash_password(self, password: str) -> str:
        return hashlib.sha256((password + self.secret_key).encode()).hexdigest()
        
    def register_user(self, username: str, password: str) -> bool:
        if username in self.users_db:
            return False
        self.users_db[username] = self.hash_password(password)
        return True
        
    def authenticate(self, username: str, password: str) -> bool:
        stored = self.users_db.get(username)
        return stored == self.hash_password(password)
'''
}


def populate_sandbox(target_directory: str = "sandbox/Downloads") -> Dict[str, Any]:
    """
    Populates the target folder with test PDFs, Python scripts, and notes.
    """
    dest_dir = Path(target_directory).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    
    # 1. Create Interview & Placement PDFs
    create_simple_pdf(
        dest_dir / "Google_SWE_Interview_Questions_2026.pdf",
        "Google SWE Interview Guide 2026",
        [
            "Topic: Data Structures, Algorithms, and System Design.",
            "Key Focus Areas: Dynamic Programming, Graph Traversals (BFS, DFS, Dijkstra), Topological Sort, and Trie implementations.",
            "System Design: Designing rate limiters, distributed caching with Redis, URL shortener scaling, and consistent hashing.",
            "Behavioral: Googleyness, collaboration under tight deadlines, and resolving technical disagreements."
        ]
    )
    created_files.append("Google_SWE_Interview_Questions_2026.pdf")

    create_simple_pdf(
        dest_dir / "Amazon_Leadership_Principles_Interview_Prep.pdf",
        "Amazon SDE Interview & 16 Leadership Principles",
        [
            "Core Principles: Customer Obsession, Ownership, Bias for Action, Deliver Results, Invent and Simplify.",
            "Coding Interview Patterns: Two Pointers, Sliding Window, Monotonic Stack, Interval Merging, Heap / PriorityQueue.",
            "System Design: High-throughput order fulfillment system, DynamoDB single-table design, and idempotency in payments."
        ]
    )
    created_files.append("Amazon_Leadership_Principles_Interview_Prep.pdf")

    create_simple_pdf(
        dest_dir / "Senior_FullStack_Engineer_Resume.pdf",
        "Resume - Full Stack Software Engineer",
        [
            "Experience: 4+ years building high-scale distributed systems, Model Context Protocol (MCP) agents, React, and Python FastAPI.",
            "Projects: AI Desktop Automation Agent using MCP tools and ReAct reasoning loop.",
            "Education: B.Tech in Computer Science and Engineering. GPA: 3.9/4.0."
        ]
    )
    created_files.append("Senior_FullStack_Engineer_Resume.pdf")

    # 2. Non-interview PDF
    create_simple_pdf(
        dest_dir / "Apartment_Electricity_Bill_March2026.pdf",
        "Monthly Utility Bill - March 2026",
        [
            "Account Number: 994821034. Due Date: April 15, 2026.",
            "Total Consumption: 320 kWh. Total Amount Payable: $48.50.",
            "Status: Unpaid. Please pay before the due date to avoid late fees."
        ]
    )
    created_files.append("Apartment_Electricity_Bill_March2026.pdf")

    # 3. Create Python code files
    code_dir = dest_dir / "python_code_samples"
    code_dir.mkdir(parents=True, exist_ok=True)
    
    for fname, code_content in SAMPLE_PYTHON_FILES.items():
        p = code_dir / fname
        with open(p, "w", encoding="utf-8") as f:
            f.write(code_content)
        created_files.append(f"python_code_samples/{fname}")

    # 4. Create sample notes
    notes_path = dest_dir / "daily_todo_notes.txt"
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write("1. Practice QuickSort and MergeSort on LeetCode\n2. Review MCP protocol specifications\n3. Polish Placement Prep folder\n")
    created_files.append("daily_todo_notes.txt")

    return {
        "success": True,
        "message": f"Successfully generated {len(created_files)} sample files in '{dest_dir}'",
        "directory": str(dest_dir),
        "created_files": created_files
    }


if __name__ == "__main__":
    res = populate_sandbox("sandbox/Downloads")
    print("Populated:", res)
