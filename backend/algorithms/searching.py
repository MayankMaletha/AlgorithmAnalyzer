"""
Searching Algorithms - Linear Search, Binary Search
Each returns step-by-step execution states.
"""

from utils.step_engine import Step, AlgorithmResult, StepType


def linear_search(arr: list[int], target: int) -> AlgorithmResult:
    steps: list[Step] = []
    a = list(arr)

    for i in range(len(a)):
        steps.append(Step.visit(i, a,
            desc=f"Checking index {i}: a[{i}]={a[i]} == {target}?",
            target=target, current_index=i))

        if a[i] == target:
            steps.append(Step.found(i, a,
                desc=f"Found {target} at index {i}!",
                target=target))
            return AlgorithmResult(
                algorithm="linear_search", steps=steps,
                total_steps=len(steps), input_data={"array": arr, "target": target},
                complexity={"time": "O(n)", "space": "O(1)"}
            )

    steps.append(Step.not_found(a,
        desc=f"{target} not found in array",
        target=target))
    return AlgorithmResult(
        algorithm="linear_search", steps=steps,
        total_steps=len(steps), input_data={"array": arr, "target": target},
        complexity={"time": "O(n)", "space": "O(1)"}
    )


def binary_search(arr: list[int], target: int) -> AlgorithmResult:
    """Array must be sorted. Binary search with step-by-step states."""
    steps: list[Step] = []
    a = sorted(arr)   # ensure sorted; frontend can show the sorted array
    low, high = 0, len(a) - 1

    while low <= high:
        mid = (low + high) // 2

        steps.append(Step(
            type=StepType.COMPARE,
            indices=[low, mid, high],
            array=list(a),
            description=f"Range [{low}..{high}], mid={mid}, a[mid]={a[mid]} vs target={target}",
            extra={"low": low, "mid": mid, "high": high, "target": target}
        ))

        if a[mid] == target:
            steps.append(Step.found(mid, a,
                desc=f"Found {target} at index {mid}!",
                target=target, low=low, mid=mid, high=high))
            return AlgorithmResult(
                algorithm="binary_search", steps=steps,
                total_steps=len(steps), input_data={"array": arr, "target": target},
                complexity={"time": "O(log n)", "space": "O(1)"}
            )
        elif a[mid] < target:
            steps.append(Step(
                type=StepType.UPDATE, indices=[mid], array=list(a),
                description=f"a[{mid}]={a[mid]} < {target}, search right half",
                extra={"low": mid + 1, "high": high, "eliminated": "left"}
            ))
            low = mid + 1
        else:
            steps.append(Step(
                type=StepType.UPDATE, indices=[mid], array=list(a),
                description=f"a[{mid}]={a[mid]} > {target}, search left half",
                extra={"low": low, "high": mid - 1, "eliminated": "right"}
            ))
            high = mid - 1

    steps.append(Step.not_found(a,
        desc=f"{target} not found in array",
        target=target))
    return AlgorithmResult(
        algorithm="binary_search", steps=steps,
        total_steps=len(steps), input_data={"array": arr, "target": target},
        complexity={"time": "O(log n)", "space": "O(1)"}
    )


SEARCHING_ALGORITHMS = {
    "linear_search": linear_search,
    "binary_search": binary_search,
}