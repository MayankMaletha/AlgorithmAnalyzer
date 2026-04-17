"""
Sorting Algorithms - Each returns a list of Steps (no in-place mutation visible to caller).
Algorithms: Bubble, Selection, Insertion, Merge, Quick, Heap
"""

from utils.step_engine import Step, AlgorithmResult, StepType


# ─────────────────────────── BUBBLE SORT ────────────────────────────

def bubble_sort(arr: list[int]) -> AlgorithmResult:
    steps: list[Step] = []
    a = list(arr)
    n = len(a)

    for i in range(n):
        for j in range(0, n - i - 1):
            steps.append(Step.compare(j, j + 1, a,
                desc=f"Comparing a[{j}]={a[j]} and a[{j+1}]={a[j+1]}"))
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                steps.append(Step.swap(j, j + 1, a,
                    desc=f"Swapped: a[{j}]={a[j]} and a[{j+1}]={a[j+1]}"))

    steps.append(Step.complete(a, "Array is fully sorted"))
    return AlgorithmResult(
        algorithm="bubble_sort", steps=steps,
        total_steps=len(steps), input_data={"array": arr},
        complexity={"time": "O(n²)", "space": "O(1)"}
    )


# ─────────────────────────── SELECTION SORT ─────────────────────────

def selection_sort(arr: list[int]) -> AlgorithmResult:
    steps: list[Step] = []
    a = list(arr)
    n = len(a)

    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            steps.append(Step.compare(min_idx, j, a,
                desc=f"Is a[{j}]={a[j]} < current min a[{min_idx}]={a[min_idx]}?",
                min_index=min_idx))
            if a[j] < a[min_idx]:
                min_idx = j

        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            steps.append(Step.swap(i, min_idx, a,
                desc=f"Placed minimum {a[i]} at position {i}"))

    steps.append(Step.complete(a, "Array is fully sorted"))
    return AlgorithmResult(
        algorithm="selection_sort", steps=steps,
        total_steps=len(steps), input_data={"array": arr},
        complexity={"time": "O(n²)", "space": "O(1)"}
    )


# ─────────────────────────── INSERTION SORT ─────────────────────────

def insertion_sort(arr: list[int]) -> AlgorithmResult:
    steps: list[Step] = []
    a = list(arr)
    n = len(a)

    for i in range(1, n):
        key = a[i]
        j = i - 1
        steps.append(Step.visit(i, a, desc=f"Inserting a[{i}]={key} into sorted portion"))
        while j >= 0 and a[j] > key:
            steps.append(Step.compare(j, j + 1, a,
                desc=f"a[{j}]={a[j]} > {key}, shifting right"))
            a[j + 1] = a[j]
            steps.append(Step.update([j + 1], a, desc=f"Shifted a[{j}] → a[{j+1}]"))
            j -= 1
        a[j + 1] = key
        steps.append(Step.update([j + 1], a, desc=f"Inserted {key} at position {j+1}"))

    steps.append(Step.complete(a, "Array is fully sorted"))
    return AlgorithmResult(
        algorithm="insertion_sort", steps=steps,
        total_steps=len(steps), input_data={"array": arr},
        complexity={"time": "O(n²)", "space": "O(1)"}
    )


# ─────────────────────────── MERGE SORT ─────────────────────────────

def merge_sort(arr: list[int]) -> AlgorithmResult:
    steps: list[Step] = []
    a = list(arr)

    def merge(a, left, mid, right):
        left_part = a[left:mid + 1]
        right_part = a[mid + 1:right + 1]
        i = j = 0
        k = left

        while i < len(left_part) and j < len(right_part):
            steps.append(Step.compare(left + i, mid + 1 + j, a,
                desc=f"Comparing {left_part[i]} and {right_part[j]}",
                left=left, mid=mid, right=right))
            if left_part[i] <= right_part[j]:
                a[k] = left_part[i]; i += 1
            else:
                a[k] = right_part[j]; j += 1
            steps.append(Step.update([k], a,
                desc=f"Placed {a[k]} at position {k}",
                left=left, mid=mid, right=right))
            k += 1

        while i < len(left_part):
            a[k] = left_part[i]
            steps.append(Step.update([k], a, desc=f"Copying remaining {a[k]}"))
            i += 1; k += 1

        while j < len(right_part):
            a[k] = right_part[j]
            steps.append(Step.update([k], a, desc=f"Copying remaining {a[k]}"))
            j += 1; k += 1

    def sort(a, left, right):
        if left < right:
            mid = (left + right) // 2
            steps.append(Step(type=StepType.HIGHLIGHT, indices=list(range(left, right + 1)),
                               array=list(a), description=f"Dividing [{left}..{right}] at mid={mid}",
                               extra={"left": left, "mid": mid, "right": right}))
            sort(a, left, mid)
            sort(a, mid + 1, right)
            merge(a, left, mid, right)

    sort(a, 0, len(a) - 1)
    steps.append(Step.complete(a, "Array is fully sorted"))
    return AlgorithmResult(
        algorithm="merge_sort", steps=steps,
        total_steps=len(steps), input_data={"array": arr},
        complexity={"time": "O(n log n)", "space": "O(n)"}
    )


# ─────────────────────────── QUICK SORT ─────────────────────────────

def quick_sort(arr: list[int]) -> AlgorithmResult:
    steps: list[Step] = []
    a = list(arr)

    def partition(a, low, high):
        pivot = a[high]
        steps.append(Step(type=StepType.SELECT, indices=[high], array=list(a),
                           description=f"Pivot selected: {pivot} at index {high}",
                           extra={"pivot": pivot, "low": low, "high": high}))
        i = low - 1
        for j in range(low, high):
            steps.append(Step.compare(j, high, a,
                desc=f"Comparing a[{j}]={a[j]} with pivot={pivot}",
                pivot_index=high, pivot=pivot))
            if a[j] <= pivot:
                i += 1
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    steps.append(Step.swap(i, j, a,
                        desc=f"Swapped a[{i}]={a[i]} and a[{j}]={a[j]}"))
        a[i + 1], a[high] = a[high], a[i + 1]
        steps.append(Step.swap(i + 1, high, a,
            desc=f"Placed pivot {pivot} at final position {i+1}"))
        return i + 1

    def sort(a, low, high):
        if low < high:
            pi = partition(a, low, high)
            sort(a, low, pi - 1)
            sort(a, pi + 1, high)

    sort(a, 0, len(a) - 1)
    steps.append(Step.complete(a, "Array is fully sorted"))
    return AlgorithmResult(
        algorithm="quick_sort", steps=steps,
        total_steps=len(steps), input_data={"array": arr},
        complexity={"time": "O(n log n) avg / O(n²) worst", "space": "O(log n)"}
    )


# ─────────────────────────── HEAP SORT ──────────────────────────────

def heap_sort(arr: list[int]) -> AlgorithmResult:
    steps: list[Step] = []
    a = list(arr)
    n = len(a)

    def heapify(a, n, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        if left < n:
            steps.append(Step.compare(left, largest, a,
                desc=f"Comparing left child a[{left}]={a[left]} with root a[{largest}]={a[largest]}"))
            if a[left] > a[largest]:
                largest = left

        if right < n:
            steps.append(Step.compare(right, largest, a,
                desc=f"Comparing right child a[{right}]={a[right]} with largest a[{largest}]={a[largest]}"))
            if a[right] > a[largest]:
                largest = right

        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            steps.append(Step.swap(i, largest, a,
                desc=f"Swapped a[{i}]={a[i]} and a[{largest}]={a[largest]} to maintain heap"))
            heapify(a, n, largest)

    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        steps.append(Step(type=StepType.HIGHLIGHT, indices=[i], array=list(a),
                           description=f"Building max heap: heapifying at index {i}",
                           extra={"phase": "build_heap"}))
        heapify(a, n, i)

    # Extract elements
    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        steps.append(Step.swap(0, i, a,
            desc=f"Moved max {a[i]} to position {i}",
            sorted_boundary=i))
        heapify(a, i, 0)

    steps.append(Step.complete(a, "Array is fully sorted"))
    return AlgorithmResult(
        algorithm="heap_sort", steps=steps,
        total_steps=len(steps), input_data={"array": arr},
        complexity={"time": "O(n log n)", "space": "O(1)"}
    )


# ─────────────────────────── REGISTRY ───────────────────────────────

SORTING_ALGORITHMS = {
    "bubble_sort": bubble_sort,
    "selection_sort": selection_sort,
    "insertion_sort": insertion_sort,
    "merge_sort": merge_sort,
    "quick_sort": quick_sort,
    "heap_sort": heap_sort,
}