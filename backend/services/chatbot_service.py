"""
Chatbot Service
- Uses Gemini (or falls back to keyword-based logic if no API key)
- Detects algorithm intent in any user message
- Returns structured response with optional visualizer suggestions
"""

import os
import re
from typing import Optional

# ─────────────────── ALGORITHM KNOWLEDGE BASE ─────────────────────────

ALGO_KB = {
    # id: { name, category, keywords[] }
    "bubble_sort":    {"name": "Bubble Sort",    "category": "sorting",   "keywords": ["bubble", "bubble sort", "simple sort", "swap adjacent"]},
    "selection_sort": {"name": "Selection Sort", "category": "sorting",   "keywords": ["selection sort", "select minimum", "find minimum"]},
    "insertion_sort": {"name": "Insertion Sort", "category": "sorting",   "keywords": ["insertion sort", "insert", "cards sorting"]},
    "merge_sort":     {"name": "Merge Sort",     "category": "sorting",   "keywords": ["merge sort", "divide and conquer sort", "merge"]},
    "quick_sort":     {"name": "Quick Sort",     "category": "sorting",   "keywords": ["quick sort", "quicksort", "pivot", "partition"]},
    "heap_sort":      {"name": "Heap Sort",      "category": "sorting",   "keywords": ["heap sort", "heapsort", "heap", "heapify"]},
    "linear_search":  {"name": "Linear Search",  "category": "searching", "keywords": ["linear search", "sequential search", "scan array"]},
    "binary_search":  {"name": "Binary Search",  "category": "searching", "keywords": ["binary search", "binary", "sorted array search", "log n search"]},
    "bfs":            {"name": "BFS",             "category": "graph",     "keywords": ["bfs", "breadth first", "breadth-first", "level order graph", "shortest path unweighted"]},
    "dfs":            {"name": "DFS",             "category": "graph",     "keywords": ["dfs", "depth first", "depth-first", "backtracking graph"]},
    "dijkstra":       {"name": "Dijkstra",        "category": "graph",     "keywords": ["dijkstra", "shortest path", "weighted shortest", "greedy path"]},
    "kruskal":        {"name": "Kruskal",         "category": "graph",     "keywords": ["kruskal", "minimum spanning tree", "mst", "union find"]},
    "prim":           {"name": "Prim",            "category": "graph",     "keywords": ["prim", "prim's algorithm", "minimum spanning tree", "mst"]},
    "fibonacci":      {"name": "Fibonacci",       "category": "dp",        "keywords": ["fibonacci", "fib", "fibonacci sequence", "memoization fibonacci"]},
    "knapsack_01":    {"name": "0/1 Knapsack",    "category": "dp",        "keywords": ["knapsack", "0/1 knapsack", "0 1 knapsack", "bag problem"]},
    "lcs":            {"name": "LCS",             "category": "dp",        "keywords": ["lcs", "longest common subsequence", "common subsequence"]},
    "lis":            {"name": "LIS",             "category": "dp",        "keywords": ["lis", "longest increasing subsequence", "increasing subsequence"]},
    "inorder_traversal":      {"name": "Inorder Traversal",     "category": "tree",   "keywords": ["inorder", "in-order", "left root right"]},
    "preorder_traversal":     {"name": "Preorder Traversal",    "category": "tree",   "keywords": ["preorder", "pre-order", "root left right"]},
    "postorder_traversal":    {"name": "Postorder Traversal",   "category": "tree",   "keywords": ["postorder", "post-order", "left right root"]},
    "level_order_traversal":  {"name": "Level Order Traversal", "category": "tree",   "keywords": ["level order", "bfs tree", "breadth first tree"]},
    "bst_insert":             {"name": "BST Insert",            "category": "tree",   "keywords": ["bst insert", "binary search tree insert", "insert bst"]},
    "lowest_common_ancestor": {"name": "LCA",                   "category": "tree",   "keywords": ["lca", "lowest common ancestor", "common ancestor"]},
    "kmp_search":    {"name": "KMP",         "category": "string", "keywords": ["kmp", "knuth morris pratt", "pattern matching", "lps"]},
    "rabin_karp":    {"name": "Rabin-Karp",  "category": "string", "keywords": ["rabin karp", "rolling hash", "hash pattern"]},
    "z_algorithm":   {"name": "Z Algorithm", "category": "string", "keywords": ["z algorithm", "z function", "z array"]},
    "max_subarray_sum":         {"name": "Max Subarray Sum",  "category": "window", "keywords": ["max subarray", "maximum subarray", "sliding window max", "kadane"]},
    "longest_unique_substring": {"name": "Longest Unique",    "category": "window", "keywords": ["longest unique", "no repeating characters", "unique substring"]},
    "subarray_sum_k":           {"name": "Subarray Sum K",    "category": "window", "keywords": ["subarray sum k", "sum equals k", "prefix sum"]},
}

GENERAL_ALGO_KEYWORDS = [
    "sort", "search", "graph", "tree", "dynamic programming", "dp",
    "algorithm", "complexity", "time complexity", "big o", "recursion",
    "traversal", "path", "string matching", "sliding window", "two pointer",
    "hash", "greedy", "backtrack", "divide", "conquer"
]


def detect_algorithms(text: str) -> list[dict]:
    """Return list of algorithm suggestions matching the user's message."""
    lower = text.lower()
    matched = []
    seen = set()
    for algo_id, info in ALGO_KB.items():
        if algo_id in seen:
            continue
        for kw in info["keywords"]:
            if kw in lower:
                matched.append({"id": algo_id, "name": info["name"], "category": info["category"]})
                seen.add(algo_id)
                break
    return matched


def is_algo_related(text: str) -> bool:
    lower = text.lower()
    if detect_algorithms(text):
        return True
    return any(kw in lower for kw in GENERAL_ALGO_KEYWORDS)


# ─────────────────── GEMINI INTEGRATION ──────────────────────────────

def _build_system_prompt() -> str:
    algo_list = "\n".join(
        f"  - {info['name']} ({info['category']}): id={aid}"
        for aid, info in ALGO_KB.items()
    )
    return f"""You are AlgoBot — an expert computer science tutor embedded in an interactive Algorithm Visualizer app.

You help users understand algorithms, data structures, complexity analysis, coding interview prep, and computer science concepts.

Available algorithms in the visualizer:
{algo_list}

Guidelines:
- Be concise, friendly, and educational.
- Use simple language. Include examples when helpful.
- When a user asks about any algorithm that exists in the visualizer, mention they can visualize it.
- When explaining complexity, use Big-O notation clearly.
- For code examples, use Python.
- Never refuse algorithm or CS questions.
- Keep responses under 300 words unless a detailed explanation is explicitly requested.
"""


async def chat_with_gemini(message: str, history: list[dict]) -> str:
    """Call Gemini API with conversation history. Returns the reply text."""
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=_build_system_prompt())

    # Build Gemini history format
    gemini_history = []
    for msg in history[-10:]:    # last 10 messages for context window
        gemini_history.append({
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [msg["content"]],
        })

    chat = model.start_chat(history=gemini_history[:-1] if gemini_history else [])
    response = chat.send_message(message)
    return response.text


# ─────────────────── FALLBACK KEYWORD RESPONDER ───────────────────────

KEYWORD_RESPONSES = {
    "bubble sort":    "Bubble Sort compares adjacent elements and swaps them if out of order. Time: O(n²), Space: O(1). Great for learning but slow on large arrays.",
    "merge sort":     "Merge Sort divides the array in half, sorts each half, then merges. Time: O(n log n), Space: O(n). Stable and efficient!",
    "quick sort":     "Quick Sort picks a pivot and partitions the array. Average O(n log n), worst O(n²). Very fast in practice due to cache locality.",
    "dijkstra":       "Dijkstra's algorithm finds shortest paths from a source node to all other nodes in a weighted graph. Time: O((V+E) log V) with a priority queue.",
    "bfs":            "Breadth-First Search explores neighbors level by level. Great for shortest path in unweighted graphs. Time: O(V+E), Space: O(V).",
    "dfs":            "Depth-First Search explores as deep as possible before backtracking. Used for cycle detection, topological sort. Time: O(V+E).",
    "binary search":  "Binary Search finds an element in a sorted array by repeatedly halving the search space. Time: O(log n). The array MUST be sorted!",
    "dynamic programming": "Dynamic Programming solves problems by breaking them into subproblems and storing results (memoization/tabulation) to avoid recomputation.",
    "fibonacci":      "Fibonacci with DP stores previously computed values. Reduces time from O(2ⁿ) naive recursion to O(n) with O(n) space.",
    "kmp":            "KMP (Knuth-Morris-Pratt) searches for a pattern in a string in O(n+m) time using a failure function (LPS array) to skip redundant comparisons.",
}

def keyword_fallback_response(message: str) -> str:
    lower = message.lower()
    for kw, resp in KEYWORD_RESPONSES.items():
        if kw in lower:
            return resp
    if is_algo_related(message):
        return (
            "That's a great CS question! I'd love to help. "
            "For the best experience, set your GEMINI_API_KEY in the backend to enable full AI responses. "
            "In the meantime, try clicking an algorithm in the sidebar to see it visualized step by step!"
        )
    return (
        "I'm AlgoBot, your algorithm tutor! Ask me about sorting, searching, graphs, dynamic programming, "
        "trees, string algorithms, or any CS concept. I can also suggest algorithms to visualize!"
    )


# ─────────────────── MAIN ENTRY POINT ────────────────────────────────

async def process_chat(message: str, history: list[dict]) -> dict:
    """
    Main chatbot handler.
    Returns: { reply, suggestions, is_algo_related }
    """
    suggestions = detect_algorithms(message)
    algo_related = is_algo_related(message)

    # Try Gemini first, fall back to keyword matching
    try:
        reply = await chat_with_gemini(message, history)
    except Exception:
        reply = keyword_fallback_response(message)

    # If Gemini replied but we detected algorithms, append a suggestion nudge
    if suggestions and "visualize" not in reply.lower() and "sidebar" not in reply.lower():
        names = ", ".join(s["name"] for s in suggestions[:3])
        reply += f"\n\n💡 You can visualize **{names}** step-by-step in the visualizer panel!"

    return {
        "reply": reply,
        "suggestions": suggestions[:5],
        "is_algo_related": algo_related,
    }