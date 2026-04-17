"""
Tree Algorithms
- Inorder, Preorder, Postorder, Level Order traversal
- BST Insert / Delete
- Lowest Common Ancestor
"""

from collections import deque
from utils.step_engine import Step, AlgorithmResult, StepType


class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def _build_tree(values: list) -> TreeNode:
    """Build tree from level-order list (None = missing node)."""
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root


def _tree_to_list(root: TreeNode) -> list:
    """Serialize tree back to level-order list."""
    if not root:
        return []
    result, queue = [], deque([root])
    while queue:
        node = queue.popleft()
        if node:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append(None)
    while result and result[-1] is None:
        result.pop()
    return result


def _tree_step(step_type, visited, current_node, tree_state, desc, **extra):
    return Step(
        type=step_type, indices=[], array=tree_state,
        description=desc,
        extra={"visited": visited, "current": current_node, **extra}
    )


# ──────────────────── INORDER ────────────────────────────────────────

def inorder_traversal(values: list) -> AlgorithmResult:
    steps: list[Step] = []
    root = _build_tree(values)
    visited = []

    def inorder(node):
        if not node:
            return
        inorder(node.left)
        visited.append(node.val)
        steps.append(_tree_step(StepType.VISIT, list(visited), node.val,
                                 _tree_to_list(root),
                                 f"Visit node {node.val} (Left → Root → Right)",
                                 traversal="inorder"))
        inorder(node.right)

    inorder(root)
    steps.append(Step.complete(_tree_to_list(root),
                               f"Inorder: {visited}", result=visited))
    return AlgorithmResult(
        algorithm="inorder_traversal", steps=steps, total_steps=len(steps),
        input_data={"tree": values},
        complexity={"time": "O(n)", "space": "O(h)"}
    )


# ──────────────────── PREORDER ────────────────────────────────────────

def preorder_traversal(values: list) -> AlgorithmResult:
    steps: list[Step] = []
    root = _build_tree(values)
    visited = []

    def preorder(node):
        if not node:
            return
        visited.append(node.val)
        steps.append(_tree_step(StepType.VISIT, list(visited), node.val,
                                 _tree_to_list(root),
                                 f"Visit node {node.val} (Root → Left → Right)",
                                 traversal="preorder"))
        preorder(node.left)
        preorder(node.right)

    preorder(root)
    steps.append(Step.complete(_tree_to_list(root),
                               f"Preorder: {visited}", result=visited))
    return AlgorithmResult(
        algorithm="preorder_traversal", steps=steps, total_steps=len(steps),
        input_data={"tree": values},
        complexity={"time": "O(n)", "space": "O(h)"}
    )


# ──────────────────── POSTORDER ───────────────────────────────────────

def postorder_traversal(values: list) -> AlgorithmResult:
    steps: list[Step] = []
    root = _build_tree(values)
    visited = []

    def postorder(node):
        if not node:
            return
        postorder(node.left)
        postorder(node.right)
        visited.append(node.val)
        steps.append(_tree_step(StepType.VISIT, list(visited), node.val,
                                 _tree_to_list(root),
                                 f"Visit node {node.val} (Left → Right → Root)",
                                 traversal="postorder"))

    postorder(root)
    steps.append(Step.complete(_tree_to_list(root),
                               f"Postorder: {visited}", result=visited))
    return AlgorithmResult(
        algorithm="postorder_traversal", steps=steps, total_steps=len(steps),
        input_data={"tree": values},
        complexity={"time": "O(n)", "space": "O(h)"}
    )


# ──────────────────── LEVEL ORDER ─────────────────────────────────────

def level_order_traversal(values: list) -> AlgorithmResult:
    steps: list[Step] = []
    root = _build_tree(values)
    if not root:
        return AlgorithmResult(algorithm="level_order_traversal", steps=[], total_steps=0,
                               input_data={"tree": values}, complexity={"time": "O(n)", "space": "O(n)"})

    visited = []
    queue = deque([root])
    level = 0

    while queue:
        level_size = len(queue)
        level_nodes = []
        for _ in range(level_size):
            node = queue.popleft()
            visited.append(node.val)
            level_nodes.append(node.val)
            steps.append(_tree_step(StepType.VISIT, list(visited), node.val,
                                     _tree_to_list(root),
                                     f"Level {level}: visiting {node.val}",
                                     level=level, level_nodes=level_nodes))
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        level += 1

    steps.append(Step.complete(_tree_to_list(root),
                               f"Level order: {visited}", result=visited))
    return AlgorithmResult(
        algorithm="level_order_traversal", steps=steps, total_steps=len(steps),
        input_data={"tree": values},
        complexity={"time": "O(n)", "space": "O(n)"}
    )


# ──────────────────── BST INSERT ──────────────────────────────────────

def bst_insert(values: list, insert_val: int) -> AlgorithmResult:
    steps: list[Step] = []
    root = _build_tree(values)

    def insert(node, val):
        if node is None:
            new_node = TreeNode(val)
            steps.append(_tree_step(StepType.INSERT, [], val,
                                     _tree_to_list(root),
                                     f"Inserted {val} as new node",
                                     inserted=val))
            return new_node
        steps.append(_tree_step(StepType.COMPARE, [], node.val,
                                 _tree_to_list(root),
                                 f"Compare {val} with {node.val}: go {'left' if val < node.val else 'right'}",
                                 comparing=(val, node.val)))
        if val < node.val:
            node.left = insert(node.left, val)
        else:
            node.right = insert(node.right, val)
        return node

    root = insert(root, insert_val)
    steps.append(Step.complete(_tree_to_list(root),
                               f"BST Insert {insert_val} complete",
                               result=_tree_to_list(root)))
    return AlgorithmResult(
        algorithm="bst_insert", steps=steps, total_steps=len(steps),
        input_data={"tree": values, "insert_val": insert_val},
        complexity={"time": "O(h)", "space": "O(h)"}
    )


# ──────────────────── LCA ────────────────────────────────────────────

def lowest_common_ancestor(values: list, p: int, q: int) -> AlgorithmResult:
    steps: list[Step] = []
    root = _build_tree(values)

    def lca(node, p, q):
        if node is None:
            return None
        steps.append(_tree_step(StepType.VISIT, [], node.val,
                                 _tree_to_list(root),
                                 f"Checking node {node.val} for LCA({p},{q})",
                                 searching=(p, q)))
        if node.val == p or node.val == q:
            steps.append(_tree_step(StepType.FOUND, [], node.val,
                                     _tree_to_list(root),
                                     f"Found target {node.val}"))
            return node
        left = lca(node.left, p, q)
        right = lca(node.right, p, q)
        if left and right:
            steps.append(_tree_step(StepType.HIGHLIGHT, [], node.val,
                                     _tree_to_list(root),
                                     f"LCA found! Node {node.val} — both {p} and {q} found in subtrees",
                                     lca=node.val))
            return node
        return left or right

    result_node = lca(root, p, q)
    lca_val = result_node.val if result_node else None
    steps.append(Step.complete(_tree_to_list(root),
                               f"LCA of {p} and {q} = {lca_val}", result=lca_val))
    return AlgorithmResult(
        algorithm="lowest_common_ancestor", steps=steps, total_steps=len(steps),
        input_data={"tree": values, "p": p, "q": q},
        complexity={"time": "O(n)", "space": "O(h)"}
    )


TREE_ALGORITHMS = {
    "inorder_traversal": inorder_traversal,
    "preorder_traversal": preorder_traversal,
    "postorder_traversal": postorder_traversal,
    "level_order_traversal": level_order_traversal,
    "bst_insert": bst_insert,
    "lowest_common_ancestor": lowest_common_ancestor,
}