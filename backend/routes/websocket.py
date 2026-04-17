"""
WebSocket Routes - Stream algorithm steps in real-time.
Connect: ws://localhost:8000/ws/algorithm

Send message:
{
  "type": "sort",
  "algorithm": "bubble_sort",
  "array": [5, 3, 8, 1, 2],
  "delay_ms": 300
}

Server streams one Step JSON per message, then sends a "done" signal.
"""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from algorithms.sorting import SORTING_ALGORITHMS
from algorithms.searching import SEARCHING_ALGORITHMS
from algorithms.graph import GRAPH_ALGORITHMS
from algorithms.dp import DP_ALGORITHMS
from algorithms.tree import TREE_ALGORITHMS
from algorithms.window import WINDOW_ALGORITHMS
from algorithms.string_algos import STRING_ALGORITHMS

router = APIRouter()


def run_algorithm(payload: dict):
    """Dispatch to the right algorithm and return AlgorithmResult."""
    algo_type = payload.get("type", "sort")
    algo_name = payload["algorithm"]

    if algo_type == "sort":
        arr = payload["array"]
        if algo_name not in SORTING_ALGORITHMS:
            raise ValueError(f"Unknown sort algorithm: {algo_name}")
        return SORTING_ALGORITHMS[algo_name](arr)

    elif algo_type == "search":
        arr, target = payload["array"], payload["target"]
        if algo_name not in SEARCHING_ALGORITHMS:
            raise ValueError(f"Unknown search algorithm: {algo_name}")
        return SEARCHING_ALGORITHMS[algo_name](arr, target)

    elif algo_type == "graph":
        if algo_name in ("bfs", "dfs", "dijkstra", "prim"):
            return GRAPH_ALGORITHMS[algo_name](payload["graph"], payload.get("start", "0"))
        elif algo_name == "bellman_ford":
            return GRAPH_ALGORITHMS["bellman_ford"](
                payload["edges"], payload["num_vertices"], int(payload.get("start", 0)))
        elif algo_name == "kruskal":
            return GRAPH_ALGORITHMS["kruskal"](payload["edges"], payload["num_vertices"])

    elif algo_type == "dp":
        if algo_name == "fibonacci":
            return DP_ALGORITHMS["fibonacci"](payload["n"])
        elif algo_name == "knapsack_01":
            return DP_ALGORITHMS["knapsack_01"](
                payload["weights"], payload["values"], payload["capacity"])
        elif algo_name == "lcs":
            return DP_ALGORITHMS["lcs"](payload["s1"], payload["s2"])
        elif algo_name == "lis":
            return DP_ALGORITHMS["lis"](payload["array"])
        
    elif algo_type == "tree":
        if algo_name not in TREE_ALGORITHMS:
            raise ValueError(f"Unknown tree algorithm: {algo_name}")

        func = TREE_ALGORITHMS[algo_name]

        if algo_name == "bst_insert":
            return func(payload["tree"], payload["insert_val"])

        elif algo_name == "lowest_common_ancestor":
            return func(payload["tree"], payload["p"], payload["q"])

        else:
            return func(payload["tree"])
        
    elif algo_type == "window":
        if algo_name not in WINDOW_ALGORITHMS:
            raise ValueError(f"Unknown window algorithm: {algo_name}")

        func = WINDOW_ALGORITHMS[algo_name]

        if algo_name == "max_subarray_sum":
            return func(payload["array"], payload["k"])

        elif algo_name == "longest_unique_substring":
            return func(payload["string"])

        elif algo_name == "prefix_sum_range":
            return func(payload["array"], payload["queries"])

        elif algo_name == "subarray_sum_k":
            return func(payload["array"], payload["k"])
        
    elif algo_type == "string":
        if algo_name not in STRING_ALGORITHMS:
            raise ValueError(f"Unknown string algorithm: {algo_name}")

        func = STRING_ALGORITHMS[algo_name]

        return func(payload["text"], payload["pattern"])

    raise ValueError(f"Unknown algorithm type/name: {algo_type}/{algo_name}")


@router.websocket("/ws/algorithm")
async def websocket_algorithm(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            delay_ms = payload.get("delay_ms", 200)
            delay_s = max(0, min(delay_ms, 2000)) / 1000   # clamp 0-2s

            try:
                result = run_algorithm(payload)
            except (ValueError, KeyError) as e:
                await websocket.send_json({"type": "error", "message": str(e)})
                continue

            # Send metadata first
            await websocket.send_json({
                "type": "start",
                "algorithm": result.algorithm,
                "total_steps": result.total_steps,
                "complexity": result.complexity,
            })

            # Stream steps with delay
            for i, step in enumerate(result.steps):
                await websocket.send_json({
                    "type": "step",
                    "step_index": i,
                    "total_steps": result.total_steps,
                    "data": step.model_dump(),
                })
                if delay_s > 0:
                    await asyncio.sleep(delay_s)

            # Signal completion
            await websocket.send_json({
                "type": "done",
                "algorithm": result.algorithm,
                "total_steps": result.total_steps,
            })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass