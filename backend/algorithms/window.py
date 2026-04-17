"""
Sliding Window + Prefix Sum Algorithms
"""

from utils.step_engine import Step, AlgorithmResult, StepType


def _window_step(step_type, arr, left, right, value, desc, **extra):
    return Step(
        type=step_type, indices=[left, right], array=list(arr),
        description=desc,
        extra={"left": left, "right": right, "current_value": value, **extra}
    )


# ──────────────── MAX SUBARRAY SUM (Sliding Window) ──────────────────

def max_subarray_sum(arr: list[int], k: int) -> AlgorithmResult:
    steps: list[Step] = []
    n = len(arr)
    if k > n:
        return AlgorithmResult(algorithm="max_subarray_sum", steps=[],
                               total_steps=0, input_data={"array": arr, "k": k},
                               complexity={"time": "O(n)", "space": "O(1)"})

    window_sum = sum(arr[:k])
    max_sum = window_sum
    max_start = 0

    steps.append(_window_step(StepType.UPDATE, arr, 0, k - 1, window_sum,
                               f"Initial window [0..{k-1}] sum={window_sum}",
                               max_sum=max_sum, max_window=[0, k-1]))

    for i in range(1, n - k + 1):
        removed, added = arr[i - 1], arr[i + k - 1]
        window_sum = window_sum - removed + added
        steps.append(_window_step(StepType.UPDATE, arr, i, i + k - 1, window_sum,
                                   f"Slide: remove arr[{i-1}]={removed}, add arr[{i+k-1}]={added} → sum={window_sum}",
                                   max_sum=max_sum, removed=removed, added=added))
        if window_sum > max_sum:
            max_sum = window_sum
            max_start = i
            steps.append(_window_step(StepType.HIGHLIGHT, arr, i, i + k - 1, window_sum,
                                       f"New maximum! sum={window_sum} at window [{i}..{i+k-1}]",
                                       max_sum=max_sum, max_window=[i, i+k-1]))

    steps.append(Step.complete(arr,
                               f"Max subarray sum of size {k} = {max_sum} at [{max_start}..{max_start+k-1}]",
                               result=max_sum, window=[max_start, max_start + k - 1]))
    return AlgorithmResult(
        algorithm="max_subarray_sum", steps=steps, total_steps=len(steps),
        input_data={"array": arr, "k": k},
        complexity={"time": "O(n)", "space": "O(1)"}
    )


# ──────────────── LONGEST SUBSTRING WITHOUT REPEATING ─────────────────

def longest_unique_substring(s: str) -> AlgorithmResult:
    steps: list[Step] = []
    char_map = {}
    left = max_len = 0
    max_window = (0, 0)
    arr = list(s)

    for right in range(len(s)):
        char = s[right]
        steps.append(_window_step(StepType.COMPARE, arr, left, right, right - left + 1,
                                   f"Checking '{char}' at right={right}. In window? {char in char_map and char_map[char] >= left}",
                                   window_str=s[left:right+1]))

        if char in char_map and char_map[char] >= left:
            old_left = left
            left = char_map[char] + 1
            steps.append(_window_step(StepType.UPDATE, arr, left, right, right - left + 1,
                                       f"Duplicate '{char}'! Move left from {old_left} to {left}",
                                       window_str=s[left:right+1]))

        char_map[char] = right
        curr_len = right - left + 1

        if curr_len > max_len:
            max_len = curr_len
            max_window = (left, right)
            steps.append(_window_step(StepType.HIGHLIGHT, arr, left, right, curr_len,
                                       f"New longest! '{s[left:right+1]}' length={curr_len}",
                                       max_len=max_len, window_str=s[left:right+1]))

    steps.append(Step.complete(arr,
                               f"Longest unique substring: '{s[max_window[0]:max_window[1]+1]}' length={max_len}",
                               result=max_len, window=list(max_window),
                               substring=s[max_window[0]:max_window[1]+1]))
    return AlgorithmResult(
        algorithm="longest_unique_substring", steps=steps, total_steps=len(steps),
        input_data={"string": s},
        complexity={"time": "O(n)", "space": "O(k)"}
    )


# ──────────────── PREFIX SUM - RANGE QUERIES ──────────────────────────

def prefix_sum_range(arr: list[int], queries: list[list[int]]) -> AlgorithmResult:
    steps: list[Step] = []
    n = len(arr)
    prefix = [0] * (n + 1)

    steps.append(Step(type=StepType.UPDATE, indices=[], array=list(arr),
                       description="Building prefix sum array",
                       extra={"prefix": list(prefix), "phase": "build"}))

    for i in range(n):
        prefix[i + 1] = prefix[i] + arr[i]
        steps.append(Step(type=StepType.UPDATE, indices=[i], array=list(arr),
                           description=f"prefix[{i+1}] = prefix[{i}] + arr[{i}] = {prefix[i]} + {arr[i]} = {prefix[i+1]}",
                           extra={"prefix": list(prefix), "i": i}))

    results = []
    for l, r in queries:
        result = prefix[r + 1] - prefix[l]
        results.append(result)
        steps.append(Step(type=StepType.HIGHLIGHT, indices=[l, r], array=list(arr),
                           description=f"Range [{l},{r}] sum = prefix[{r+1}] - prefix[{l}] = {prefix[r+1]} - {prefix[l]} = {result}",
                           extra={"prefix": list(prefix), "l": l, "r": r, "result": result}))

    steps.append(Step.complete(arr, f"All queries answered: {results}",
                               results=results, prefix=prefix))
    return AlgorithmResult(
        algorithm="prefix_sum_range", steps=steps, total_steps=len(steps),
        input_data={"array": arr, "queries": queries},
        complexity={"time": "O(n + q)", "space": "O(n)"}
    )


# ──────────────── SUBARRAY SUM EQUALS K ──────────────────────────────

def subarray_sum_k(arr: list[int], k: int) -> AlgorithmResult:
    steps: list[Step] = []
    prefix_count = {0: 1}
    curr_sum = count = 0
    subarrays = []

    steps.append(Step(type=StepType.UPDATE, indices=[], array=list(arr),
                       description=f"Find subarrays with sum = {k}. Init prefix_count={{0:1}}",
                       extra={"k": k, "prefix_count": dict(prefix_count)}))

    for i, num in enumerate(arr):
        curr_sum += num
        need = curr_sum - k
        steps.append(Step(type=StepType.COMPARE, indices=[i], array=list(arr),
                           description=f"arr[{i}]={num}, curr_sum={curr_sum}. Need prefix sum {need} to get sum={k}. Found? {need in prefix_count}",
                           extra={"curr_sum": curr_sum, "need": need, "prefix_count": dict(prefix_count)}))

        if need in prefix_count:
            count += prefix_count[need]
            subarrays.append({"end": i, "count": prefix_count[need]})
            steps.append(Step(type=StepType.FOUND, indices=[i], array=list(arr),
                               description=f"Found {prefix_count[need]} subarray(s) ending at index {i} with sum={k}!",
                               extra={"count": count, "end_index": i}))

        prefix_count[curr_sum] = prefix_count.get(curr_sum, 0) + 1

    steps.append(Step.complete(arr, f"Total subarrays with sum={k}: {count}",
                               result=count, subarrays=subarrays))
    return AlgorithmResult(
        algorithm="subarray_sum_k", steps=steps, total_steps=len(steps),
        input_data={"array": arr, "k": k},
        complexity={"time": "O(n)", "space": "O(n)"}
    )


WINDOW_ALGORITHMS = {
    "max_subarray_sum": max_subarray_sum,
    "longest_unique_substring": longest_unique_substring,
    "prefix_sum_range": prefix_sum_range,
    "subarray_sum_k": subarray_sum_k,
}