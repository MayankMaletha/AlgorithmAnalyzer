"""
Complete Algorithm Routes — Phase 2 with all algorithm categories.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from models.requests import SortRequest, SearchRequest, GraphRequest, DPRequest
from algorithms.sorting import SORTING_ALGORITHMS
from algorithms.searching import SEARCHING_ALGORITHMS
from algorithms.graph import GRAPH_ALGORITHMS
from algorithms.dp import DP_ALGORITHMS
from algorithms.tree import TREE_ALGORITHMS
from algorithms.string_algos import STRING_ALGORITHMS
from algorithms.window import WINDOW_ALGORITHMS
from utils.step_engine import AlgorithmResult

router = APIRouter()

ALGORITHM_META = {
    "bubble_sort":    {"category": "sorting", "time": "O(n²)", "space": "O(1)"},
    "selection_sort": {"category": "sorting", "time": "O(n²)", "space": "O(1)"},
    "insertion_sort": {"category": "sorting", "time": "O(n²)", "space": "O(1)"},
    "merge_sort":     {"category": "sorting", "time": "O(n log n)", "space": "O(n)"},
    "quick_sort":     {"category": "sorting", "time": "O(n log n) avg", "space": "O(log n)"},
    "heap_sort":      {"category": "sorting", "time": "O(n log n)", "space": "O(1)"},
    "linear_search":  {"category": "searching", "time": "O(n)", "space": "O(1)"},
    "binary_search":  {"category": "searching", "time": "O(log n)", "space": "O(1)"},
    "bfs":            {"category": "graph", "time": "O(V+E)", "space": "O(V)"},
    "dfs":            {"category": "graph", "time": "O(V+E)", "space": "O(V)"},
    "dijkstra":       {"category": "graph", "time": "O((V+E) log V)", "space": "O(V)"},
    "bellman_ford":   {"category": "graph", "time": "O(V×E)", "space": "O(V)"},
    "kruskal":        {"category": "graph", "time": "O(E log E)", "space": "O(V)"},
    "prim":           {"category": "graph", "time": "O((V+E) log V)", "space": "O(V)"},
    "fibonacci":      {"category": "dp", "time": "O(n)", "space": "O(n)"},
    "knapsack_01":    {"category": "dp", "time": "O(n×W)", "space": "O(n×W)"},
    "lcs":            {"category": "dp", "time": "O(m×n)", "space": "O(m×n)"},
    "lis":            {"category": "dp", "time": "O(n²)", "space": "O(n)"},
    "inorder_traversal":      {"category": "tree", "time": "O(n)", "space": "O(h)"},
    "preorder_traversal":     {"category": "tree", "time": "O(n)", "space": "O(h)"},
    "postorder_traversal":    {"category": "tree", "time": "O(n)", "space": "O(h)"},
    "level_order_traversal":  {"category": "tree", "time": "O(n)", "space": "O(n)"},
    "bst_insert":             {"category": "tree", "time": "O(h)", "space": "O(h)"},
    "lowest_common_ancestor": {"category": "tree", "time": "O(n)", "space": "O(h)"},
    "kmp_search":  {"category": "string", "time": "O(n+m)", "space": "O(m)"},
    "rabin_karp":  {"category": "string", "time": "O(n+m) avg", "space": "O(1)"},
    "z_algorithm": {"category": "string", "time": "O(n+m)", "space": "O(n+m)"},
    "max_subarray_sum":         {"category": "window", "time": "O(n)", "space": "O(1)"},
    "longest_unique_substring": {"category": "window", "time": "O(n)", "space": "O(k)"},
    "prefix_sum_range":         {"category": "window", "time": "O(n+q)", "space": "O(n)"},
    "subarray_sum_k":           {"category": "window", "time": "O(n)", "space": "O(n)"},
}


@router.get("/algorithm/list")
def list_algorithms():
    grouped = {}
    for name, meta in ALGORITHM_META.items():
        cat = meta["category"]
        grouped.setdefault(cat, []).append({"name": name, **meta})
    return {"algorithms": grouped, "total": len(ALGORITHM_META)}


@router.get("/algorithm/{name}/complexity")
def get_complexity(name: str):
    if name not in ALGORITHM_META:
        raise HTTPException(404, f"Algorithm '{name}' not found")
    return {"algorithm": name, **ALGORITHM_META[name]}


@router.post("/algorithm/run", response_model=AlgorithmResult)
def run_sorting(req: SortRequest):
    if req.algorithm not in SORTING_ALGORITHMS:
        raise HTTPException(400, f"Unknown sorting algorithm: '{req.algorithm}'")
    return SORTING_ALGORITHMS[req.algorithm](req.array)


@router.post("/search/run", response_model=AlgorithmResult)
def run_searching(req: SearchRequest):
    if req.algorithm not in SEARCHING_ALGORITHMS:
        raise HTTPException(400, f"Unknown search algorithm: '{req.algorithm}'")
    return SEARCHING_ALGORITHMS[req.algorithm](req.array, req.target)


@router.post("/graph/run", response_model=AlgorithmResult)
def run_graph(req: GraphRequest):
    algo = req.algorithm
    if algo in ("bfs", "dfs", "dijkstra", "prim"):
        if not req.graph:
            raise HTTPException(400, f"{algo} requires 'graph'")
        return GRAPH_ALGORITHMS[algo](req.graph, req.start or "0")
    elif algo == "bellman_ford":
        if not req.edges or req.num_vertices is None:
            raise HTTPException(400, "bellman_ford requires 'edges' and 'num_vertices'")
        return GRAPH_ALGORITHMS["bellman_ford"](req.edges, req.num_vertices, int(req.start or 0))
    elif algo == "kruskal":
        if not req.edges or req.num_vertices is None:
            raise HTTPException(400, "kruskal requires 'edges' and 'num_vertices'")
        return GRAPH_ALGORITHMS["kruskal"](req.edges, req.num_vertices)
    raise HTTPException(400, f"Unknown graph algorithm: '{algo}'")


@router.post("/dp/run", response_model=AlgorithmResult)
def run_dp(req: DPRequest):
    algo = req.algorithm
    if algo == "fibonacci":
        if req.n is None: raise HTTPException(400, "requires 'n'")
        return DP_ALGORITHMS["fibonacci"](req.n)
    elif algo == "knapsack_01":
        if not req.weights or not req.values or req.capacity is None:
            raise HTTPException(400, "requires 'weights', 'values', 'capacity'")
        return DP_ALGORITHMS["knapsack_01"](req.weights, req.values, req.capacity)
    elif algo == "lcs":
        if not req.s1 or not req.s2: raise HTTPException(400, "requires 's1' and 's2'")
        return DP_ALGORITHMS["lcs"](req.s1, req.s2)
    elif algo == "lis":
        if not req.array: raise HTTPException(400, "requires 'array'")
        return DP_ALGORITHMS["lis"](req.array)
    raise HTTPException(400, f"Unknown DP algorithm: '{algo}'")


class TreeRequest(BaseModel):
    algorithm: str
    tree: list
    insert_val: Optional[int] = None
    p: Optional[int] = None
    q: Optional[int] = None


@router.post("/tree/run", response_model=AlgorithmResult)
def run_tree(req: TreeRequest):
    algo = req.algorithm
    if algo in ("inorder_traversal", "preorder_traversal",
                "postorder_traversal", "level_order_traversal"):
        return TREE_ALGORITHMS[algo](req.tree)
    elif algo == "bst_insert":
        if req.insert_val is None: raise HTTPException(400, "requires 'insert_val'")
        return TREE_ALGORITHMS["bst_insert"](req.tree, req.insert_val)
    elif algo == "lowest_common_ancestor":
        if req.p is None or req.q is None: raise HTTPException(400, "requires 'p' and 'q'")
        return TREE_ALGORITHMS["lowest_common_ancestor"](req.tree, req.p, req.q)
    raise HTTPException(400, f"Unknown tree algorithm: '{algo}'")


class StringRequest(BaseModel):
    algorithm: str
    text: str
    pattern: str


@router.post("/string/run", response_model=AlgorithmResult)
def run_string(req: StringRequest):
    if req.algorithm not in STRING_ALGORITHMS:
        raise HTTPException(400, f"Unknown string algorithm: '{req.algorithm}'")
    return STRING_ALGORITHMS[req.algorithm](req.text, req.pattern)


class WindowRequest(BaseModel):
    algorithm: str
    array: Optional[list] = None
    string: Optional[str] = None
    k: Optional[int] = None
    queries: Optional[list] = None


@router.post("/window/run", response_model=AlgorithmResult)
def run_window(req: WindowRequest):
    algo = req.algorithm
    if algo == "max_subarray_sum":
        if not req.array or req.k is None: raise HTTPException(400, "requires 'array' and 'k'")
        return WINDOW_ALGORITHMS["max_subarray_sum"](req.array, req.k)
    elif algo == "longest_unique_substring":
        if not req.string: raise HTTPException(400, "requires 'string'")
        return WINDOW_ALGORITHMS["longest_unique_substring"](req.string)
    elif algo == "prefix_sum_range":
        if not req.array or not req.queries: raise HTTPException(400, "requires 'array' and 'queries'")
        return WINDOW_ALGORITHMS["prefix_sum_range"](req.array, req.queries)
    elif algo == "subarray_sum_k":
        if not req.array or req.k is None: raise HTTPException(400, "requires 'array' and 'k'")
        return WINDOW_ALGORITHMS["subarray_sum_k"](req.array, req.k)
    raise HTTPException(400, f"Unknown window algorithm: '{algo}'")