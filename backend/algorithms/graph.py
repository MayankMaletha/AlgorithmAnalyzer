"""
Graph Algorithms
Input: adjacency list { "0": [[1,4],[2,1]], "1": [[3,1]], ... } 
       or edge list [[u, v, weight], ...]
"""

from collections import deque
import heapq
from utils.step_engine import Step, AlgorithmResult, StepType


def _graph_step(step_type, visited, distances, active_nodes, active_edges, array_snapshot, desc, **extra):
    return Step(
        type=step_type,
        indices=active_nodes,
        array=array_snapshot,
        description=desc,
        extra={"visited": visited, "distances": distances,
               "active_edges": active_edges, **extra}
    )


# ─────────────────────────── BFS ────────────────────────────────────

def bfs(graph: dict, start: str) -> AlgorithmResult:
    steps: list[Step] = []
    visited = []
    queue = deque([start])
    seen = {start}
    node_list = list(graph.keys())

    steps.append(_graph_step(StepType.VISIT, visited, {}, [node_list.index(start)],
                              [], node_list, f"Start BFS from node {start}", queue=list(queue)))

    while queue:
        node = queue.popleft()
        visited.append(node)
        idx = node_list.index(node) if node in node_list else -1
        steps.append(_graph_step(StepType.VISIT, list(visited), {}, [idx],
                                  [], node_list, f"Visiting node {node}",
                                  current=node, queue=list(queue)))

        for neighbor_info in graph.get(node, []):
            neighbor = str(neighbor_info[0]) if isinstance(neighbor_info, list) else str(neighbor_info)
            n_idx = node_list.index(neighbor) if neighbor in node_list else -1
            steps.append(_graph_step(StepType.COMPARE, list(visited), {}, [idx, n_idx],
                                      [[node, neighbor]], node_list,
                                      f"Checking neighbor {neighbor} of {node}",
                                      edge=[node, neighbor]))
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
                steps.append(_graph_step(StepType.UPDATE, list(visited), {}, [n_idx],
                                          [[node, neighbor]], node_list,
                                          f"Enqueue {neighbor}", queue=list(queue)))

    steps.append(Step.complete(node_list, f"BFS complete. Order: {visited}",
                               traversal_order=visited))
    return AlgorithmResult(
        algorithm="bfs", steps=steps, total_steps=len(steps),
        input_data={"graph": graph, "start": start},
        complexity={"time": "O(V + E)", "space": "O(V)"}
    )


# ─────────────────────────── DFS ────────────────────────────────────

def dfs(graph: dict, start: str) -> AlgorithmResult:
    steps: list[Step] = []
    visited_order = []
    visited_set = set()
    node_list = list(graph.keys())

    def _dfs(node):
        visited_set.add(node)
        visited_order.append(node)
        idx = node_list.index(node) if node in node_list else -1
        steps.append(_graph_step(StepType.VISIT, list(visited_order), {}, [idx],
                                  [], node_list, f"Visiting node {node}", stack_depth=len(visited_order)))

        for neighbor_info in graph.get(node, []):
            neighbor = str(neighbor_info[0]) if isinstance(neighbor_info, list) else str(neighbor_info)
            n_idx = node_list.index(neighbor) if neighbor in node_list else -1
            steps.append(_graph_step(StepType.COMPARE, list(visited_order), {}, [idx, n_idx],
                                      [[node, neighbor]], node_list,
                                      f"Exploring edge {node} → {neighbor}"))
            if neighbor not in visited_set:
                _dfs(neighbor)

    _dfs(start)
    steps.append(Step.complete(node_list, f"DFS complete. Order: {visited_order}",
                               traversal_order=visited_order))
    return AlgorithmResult(
        algorithm="dfs", steps=steps, total_steps=len(steps),
        input_data={"graph": graph, "start": start},
        complexity={"time": "O(V + E)", "space": "O(V)"}
    )


# ─────────────────────────── DIJKSTRA ───────────────────────────────

def dijkstra(graph: dict, start: str) -> AlgorithmResult:
    steps: list[Step] = []
    INF = float("inf")
    node_list = list(graph.keys())
    dist = {node: INF for node in node_list}
    dist[start] = 0
    pq = [(0, start)]
    visited = []

    steps.append(_graph_step(StepType.UPDATE, [], dict(dist),
                              [node_list.index(start)], [], node_list,
                              f"Init distances. dist[{start}]=0, all others=∞"))

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.append(u)
        u_idx = node_list.index(u) if u in node_list else -1
        steps.append(_graph_step(StepType.VISIT, list(visited), dict(dist),
                                  [u_idx], [], node_list,
                                  f"Processing node {u} with dist={d}"))

        for neighbor_info in graph.get(u, []):
            v, w = str(neighbor_info[0]), neighbor_info[1]
            v_idx = node_list.index(v) if v in node_list else -1
            new_dist = dist[u] + w
            steps.append(_graph_step(StepType.COMPARE, list(visited), dict(dist),
                                      [u_idx, v_idx], [[u, v, w]], node_list,
                                      f"Relaxing edge {u}→{v}: {dist[u]}+{w}={new_dist} vs {dist[v]}",
                                      edge=[u, v, w]))
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(pq, (new_dist, v))
                steps.append(_graph_step(StepType.UPDATE, list(visited), dict(dist),
                                          [v_idx], [[u, v]], node_list,
                                          f"Updated dist[{v}] = {new_dist}"))

    steps.append(Step.complete(node_list, "Dijkstra complete", distances=dist))
    return AlgorithmResult(
        algorithm="dijkstra", steps=steps, total_steps=len(steps),
        input_data={"graph": graph, "start": start},
        complexity={"time": "O((V + E) log V)", "space": "O(V)"}
    )


# ─────────────────────────── BELLMAN-FORD ───────────────────────────

def bellman_ford(edges: list, num_vertices: int, start: int) -> AlgorithmResult:
    """edges: [[u, v, weight], ...]"""
    steps: list[Step] = []
    INF = float("inf")
    dist = [INF] * num_vertices
    dist[start] = 0
    node_list = list(range(num_vertices))

    steps.append(_graph_step(StepType.UPDATE, [], list(dist), [start],
                              [], node_list, f"Init dist[{start}]=0, all others=∞"))

    for i in range(num_vertices - 1):
        steps.append(_graph_step(StepType.HIGHLIGHT, [], list(dist), [],
                                  [], node_list, f"Relaxation pass {i+1}/{num_vertices-1}",
                                  pass_number=i+1))
        for u, v, w in edges:
            steps.append(_graph_step(StepType.COMPARE, [], list(dist), [u, v],
                                      [[u, v, w]], node_list,
                                      f"Edge ({u},{v},{w}): dist[{v}]={dist[v]} vs dist[{u}]+{w}={dist[u]+w if dist[u]!=INF else '∞'}"))
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                steps.append(_graph_step(StepType.UPDATE, [], list(dist), [v],
                                          [[u, v]], node_list,
                                          f"Relaxed dist[{v}] = {dist[v]}"))

    # Negative cycle check
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            steps.append(Step(type=StepType.HIGHLIGHT, indices=[u, v], array=node_list,
                               description="Negative cycle detected!", extra={"negative_cycle": True}))
            break

    steps.append(Step.complete(node_list, "Bellman-Ford complete", distances=dist))
    return AlgorithmResult(
        algorithm="bellman_ford", steps=steps, total_steps=len(steps),
        input_data={"edges": edges, "num_vertices": num_vertices, "start": start},
        complexity={"time": "O(V × E)", "space": "O(V)"}
    )


# ─────────────────────────── KRUSKAL ────────────────────────────────

def kruskal(edges: list, num_vertices: int) -> AlgorithmResult:
    """edges: [[u, v, weight], ...] — finds Minimum Spanning Tree"""
    steps: list[Step] = []
    parent = list(range(num_vertices))
    rank = [0] * num_vertices
    mst_edges = []
    node_list = list(range(num_vertices))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px == py: return False
        if rank[px] < rank[py]: px, py = py, px
        parent[py] = px
        if rank[px] == rank[py]: rank[px] += 1
        return True

    sorted_edges = sorted(edges, key=lambda e: e[2])
    steps.append(_graph_step(StepType.UPDATE, [], {}, [], [], node_list,
                              f"Edges sorted by weight: {[e[2] for e in sorted_edges]}"))

    for u, v, w in sorted_edges:
        steps.append(_graph_step(StepType.COMPARE, [], {}, [u, v], [[u, v, w]], node_list,
                                  f"Consider edge ({u},{v}) weight={w}. Same component? {find(u)==find(v)}"))
        if union(u, v):
            mst_edges.append([u, v, w])
            steps.append(_graph_step(StepType.SELECT, [], {}, [u, v], [[u, v, w]], node_list,
                                      f"Added edge ({u},{v}) weight={w} to MST",
                                      mst_edges=list(mst_edges)))
        else:
            steps.append(_graph_step(StepType.HIGHLIGHT, [], {}, [u, v], [[u, v, w]], node_list,
                                      f"Skipped edge ({u},{v}) — would create cycle"))

    mst_weight = sum(e[2] for e in mst_edges)
    steps.append(Step.complete(node_list, f"MST complete. Total weight={mst_weight}",
                               mst_edges=mst_edges, total_weight=mst_weight))
    return AlgorithmResult(
        algorithm="kruskal", steps=steps, total_steps=len(steps),
        input_data={"edges": edges, "num_vertices": num_vertices},
        complexity={"time": "O(E log E)", "space": "O(V)"}
    )


# ─────────────────────────── PRIM ───────────────────────────────────

def prim(graph: dict, start: str) -> AlgorithmResult:
    """graph: { "0": [[1,4],[2,1]], ... }"""
    steps: list[Step] = []
    node_list = list(graph.keys())
    in_mst = set()
    mst_edges = []
    pq = [(0, start, None)]   # (weight, node, parent)

    while pq:
        w, u, parent_node = heapq.heappop(pq)
        if u in in_mst:
            continue
        in_mst.add(u)
        u_idx = node_list.index(u) if u in node_list else -1

        if parent_node is not None:
            mst_edges.append([parent_node, u, w])
            steps.append(_graph_step(StepType.SELECT, list(in_mst), {}, [u_idx],
                                      [[parent_node, u, w]], node_list,
                                      f"Added {parent_node}→{u} (weight={w}) to MST",
                                      mst_edges=list(mst_edges)))
        else:
            steps.append(_graph_step(StepType.VISIT, list(in_mst), {}, [u_idx],
                                      [], node_list, f"Start from node {u}"))

        for neighbor_info in graph.get(u, []):
            v, edge_w = str(neighbor_info[0]), neighbor_info[1]
            if v not in in_mst:
                v_idx = node_list.index(v) if v in node_list else -1
                heapq.heappush(pq, (edge_w, v, u))
                steps.append(_graph_step(StepType.UPDATE, list(in_mst), {}, [v_idx],
                                          [[u, v, edge_w]], node_list,
                                          f"Enqueued edge {u}→{v} (weight={edge_w})"))

    mst_weight = sum(e[2] for e in mst_edges)
    steps.append(Step.complete(node_list, f"Prim's MST complete. Total weight={mst_weight}",
                               mst_edges=mst_edges, total_weight=mst_weight))
    return AlgorithmResult(
        algorithm="prim", steps=steps, total_steps=len(steps),
        input_data={"graph": graph, "start": start},
        complexity={"time": "O((V + E) log V)", "space": "O(V)"}
    )


GRAPH_ALGORITHMS = {
    "bfs": bfs,
    "dfs": dfs,
    "dijkstra": dijkstra,
    "bellman_ford": bellman_ford,
    "kruskal": kruskal,
    "prim": prim,
}