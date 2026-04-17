"""
Dynamic Programming Algorithms
Returns step-by-step DP table updates so the frontend
can animate cell-by-cell fills.
"""

from utils.step_engine import Step, AlgorithmResult, StepType


def _dp_step(table, highlight_cells, desc, **extra):
    flat = [x for row in table for x in (row if isinstance(row, list) else [row])]
    shape = [len(table), len(table[0])] if table and isinstance(table[0], list) else [len(table)]
    return Step(
        type=StepType.UPDATE,
        indices=highlight_cells,
        array=flat,
        description=desc,
        extra={"table": [list(r) if isinstance(r, list) else r for r in table],
               "shape": shape, **extra}
    )


# ─────────────────────────── FIBONACCI ──────────────────────────────

def fibonacci(n: int) -> AlgorithmResult:
    steps: list[Step] = []
    dp = [0] * (n + 1)
    dp[0] = 0
    if n >= 1: dp[1] = 1

    steps.append(Step(type=StepType.UPDATE, indices=[0], array=list(dp),
                       description="Base case: F(0)=0", extra={"table": list(dp)}))
    if n >= 1:
        steps.append(Step(type=StepType.UPDATE, indices=[1], array=list(dp),
                           description="Base case: F(1)=1", extra={"table": list(dp)}))

    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
        steps.append(Step(
            type=StepType.UPDATE, indices=[i], array=list(dp),
            description=f"F({i}) = F({i-1}) + F({i-2}) = {dp[i-1]} + {dp[i-2]} = {dp[i]}",
            extra={"table": list(dp), "used": [i-1, i-2]}
        ))

    steps.append(Step.complete(dp, f"Fibonacci({n}) = {dp[n]}", result=dp[n]))
    return AlgorithmResult(
        algorithm="fibonacci", steps=steps, total_steps=len(steps),
        input_data={"n": n},
        complexity={"time": "O(n)", "space": "O(n)"}
    )


# ─────────────────────────── 0/1 KNAPSACK ───────────────────────────

def knapsack_01(weights: list[int], values: list[int], capacity: int) -> AlgorithmResult:
    steps: list[Step] = []
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    steps.append(_dp_step(dp, [], "Initialize DP table with zeros",
                           weights=weights, values=values, capacity=capacity))

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i - 1] <= w:
                include = values[i - 1] + dp[i - 1][w - weights[i - 1]]
                exclude = dp[i - 1][w]
                dp[i][w] = max(include, exclude)
                steps.append(_dp_step(dp, [i * (capacity + 1) + w],
                                       f"Item {i} (w={weights[i-1]}, v={values[i-1]}), cap={w}: "
                                       f"include={include} vs exclude={exclude} → {dp[i][w]}",
                                       item=i, cap=w, decision="include" if include >= exclude else "exclude"))
            else:
                dp[i][w] = dp[i - 1][w]
                steps.append(_dp_step(dp, [i * (capacity + 1) + w],
                                       f"Item {i} too heavy (w={weights[i-1]} > cap={w}), skip",
                                       item=i, cap=w, decision="skip"))

    steps.append(Step.complete([dp[n][capacity]],
                               f"Max value = {dp[n][capacity]}", result=dp[n][capacity]))
    return AlgorithmResult(
        algorithm="knapsack_01", steps=steps, total_steps=len(steps),
        input_data={"weights": weights, "values": values, "capacity": capacity},
        complexity={"time": "O(n × W)", "space": "O(n × W)"}
    )


# ─────────────────────────── LCS ────────────────────────────────────

def lcs(s1: str, s2: str) -> AlgorithmResult:
    steps: list[Step] = []
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    steps.append(_dp_step(dp, [], f"LCS of '{s1}' and '{s2}'. Init table.", s1=s1, s2=s2))

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                steps.append(_dp_step(dp, [i * (n + 1) + j],
                                       f"s1[{i-1}]='{s1[i-1]}' == s2[{j-1}]='{s2[j-1]}' → dp[{i}][{j}] = {dp[i][j]}",
                                       match=True, chars=(s1[i-1], s2[j-1])))
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
                steps.append(_dp_step(dp, [i * (n + 1) + j],
                                       f"s1[{i-1}]='{s1[i-1]}' ≠ s2[{j-1}]='{s2[j-1]}' → max({dp[i-1][j]},{dp[i][j-1]}) = {dp[i][j]}",
                                       match=False))

    # Backtrack to find actual LCS string
    lcs_str, i, j = [], m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            lcs_str.append(s1[i - 1]); i -= 1; j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    lcs_str = "".join(reversed(lcs_str))

    steps.append(Step.complete([dp[m][n]], f"LCS = '{lcs_str}', length = {dp[m][n]}",
                               result=lcs_str, length=dp[m][n]))
    return AlgorithmResult(
        algorithm="lcs", steps=steps, total_steps=len(steps),
        input_data={"s1": s1, "s2": s2},
        complexity={"time": "O(m × n)", "space": "O(m × n)"}
    )


# ─────────────────────────── LIS ────────────────────────────────────

def lis(arr: list[int]) -> AlgorithmResult:
    steps: list[Step] = []
    n = len(arr)
    dp = [1] * n

    steps.append(Step(type=StepType.UPDATE, indices=[], array=list(dp),
                       description="Init dp[i]=1 (each element is an LIS of length 1)",
                       extra={"table": list(dp), "input": arr}))

    for i in range(1, n):
        for j in range(i):
            steps.append(Step(type=StepType.COMPARE, indices=[j, i], array=list(dp),
                               description=f"arr[{j}]={arr[j]} < arr[{i}]={arr[i]}? dp[{i}]={dp[i]}, dp[{j}]+1={dp[j]+1}",
                               extra={"table": list(dp), "input": arr}))
            if arr[j] < arr[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
                steps.append(Step(type=StepType.UPDATE, indices=[i], array=list(dp),
                                   description=f"Updated dp[{i}] = {dp[i]}",
                                   extra={"table": list(dp), "input": arr}))

    result = max(dp)
    steps.append(Step.complete(dp, f"LIS length = {result}", result=result))
    return AlgorithmResult(
        algorithm="lis", steps=steps, total_steps=len(steps),
        input_data={"array": arr},
        complexity={"time": "O(n²)", "space": "O(n)"}
    )


DP_ALGORITHMS = {
    "fibonacci": fibonacci,
    "knapsack_01": knapsack_01,
    "lcs": lcs,
    "lis": lis,
}