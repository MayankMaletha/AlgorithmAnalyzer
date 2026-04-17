"""
String Matching Algorithms
- KMP (LPS table + pattern matching)
- Rabin-Karp (rolling hash)
- Z Algorithm
"""

from utils.step_engine import Step, AlgorithmResult, StepType


def _str_step(step_type, text, pattern, text_idx, pat_idx, matches, desc, **extra):
    return Step(
        type=step_type,
        indices=[text_idx, pat_idx],
        array=list(text),
        description=desc,
        extra={"text": text, "pattern": pattern, "text_idx": text_idx,
               "pat_idx": pat_idx, "matches": matches, **extra}
    )


# ──────────────────── KMP ─────────────────────────────────────────────

def kmp_search(text: str, pattern: str) -> AlgorithmResult:
    steps: list[Step] = []
    matches = []
    n, m = len(text), len(pattern)

    # Build LPS (Longest Proper Prefix which is also Suffix)
    lps = [0] * m
    length, i = 0, 1
    steps.append(Step(type=StepType.UPDATE, indices=[], array=list(pattern),
                       description=f"Building LPS table for pattern '{pattern}'",
                       extra={"lps": list(lps), "phase": "lps_build"}))

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            steps.append(Step(type=StepType.UPDATE, indices=[i], array=list(pattern),
                               description=f"LPS[{i}]={length}: pattern[{i}]='{pattern[i]}' matches pattern[{length-1}]",
                               extra={"lps": list(lps), "i": i, "length": length, "phase": "lps_build"}))
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
                steps.append(Step(type=StepType.COMPARE, indices=[i], array=list(pattern),
                                   description=f"Mismatch: fallback length to {length}",
                                   extra={"lps": list(lps), "phase": "lps_build"}))
            else:
                lps[i] = 0
                i += 1

    steps.append(Step(type=StepType.COMPLETE, indices=[], array=list(pattern),
                       description=f"LPS table complete: {lps}",
                       extra={"lps": lps, "phase": "lps_done"}))

    # Search
    i = j = 0
    while i < n:
        steps.append(_str_step(StepType.COMPARE, text, pattern, i, j, list(matches),
                                f"Comparing text[{i}]='{text[i]}' with pattern[{j}]='{pattern[j]}'",
                                lps=lps, phase="search"))
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == m:
            match_start = i - j
            matches.append(match_start)
            steps.append(_str_step(StepType.FOUND, text, pattern, match_start, j - 1, list(matches),
                                    f"Pattern found at index {match_start}!",
                                    lps=lps, match_start=match_start, phase="search"))
            j = lps[j - 1]
        elif i < n and text[i] != pattern[j]:
            if j != 0:
                steps.append(_str_step(StepType.UPDATE, text, pattern, i, j, list(matches),
                                        f"Mismatch: jump pattern to lps[{j-1}]={lps[j-1]}",
                                        lps=lps, phase="search"))
                j = lps[j - 1]
            else:
                i += 1

    steps.append(Step.complete(list(text),
                               f"KMP done. Matches at: {matches}" if matches else "No matches found",
                               matches=matches, total_matches=len(matches)))
    return AlgorithmResult(
        algorithm="kmp_search", steps=steps, total_steps=len(steps),
        input_data={"text": text, "pattern": pattern},
        complexity={"time": "O(n + m)", "space": "O(m)"}
    )


# ──────────────────── RABIN-KARP ─────────────────────────────────────

def rabin_karp(text: str, pattern: str) -> AlgorithmResult:
    steps: list[Step] = []
    matches = []
    n, m = len(text), len(pattern)
    BASE, MOD = 31, 10**9 + 7

    def char_val(c):
        return ord(c) - ord('a') + 1

    # Compute pattern hash and first window hash
    pat_hash = 0
    window_hash = 0
    power = 1

    for i in range(m):
        pat_hash = (pat_hash + char_val(pattern[i]) * power) % MOD
        window_hash = (window_hash + char_val(text[i]) * power) % MOD
        if i < m - 1:
            power = (power * BASE) % MOD

    steps.append(Step(type=StepType.UPDATE, indices=[], array=list(text),
                       description=f"Pattern hash = {pat_hash}. First window hash = {window_hash}",
                       extra={"pat_hash": pat_hash, "window_hash": window_hash, "base": BASE}))

    for i in range(n - m + 1):
        steps.append(_str_step(StepType.COMPARE, text, pattern, i, 0, list(matches),
                                f"Window [{i}..{i+m-1}] hash={window_hash} vs pattern hash={pat_hash}. Match? {window_hash == pat_hash}",
                                window_hash=window_hash, pat_hash=pat_hash))

        if window_hash == pat_hash:
            # Verify character by character
            if text[i:i+m] == pattern:
                matches.append(i)
                steps.append(_str_step(StepType.FOUND, text, pattern, i, m - 1, list(matches),
                                        f"Verified match at index {i}!",
                                        match_start=i))
            else:
                steps.append(_str_step(StepType.UPDATE, text, pattern, i, 0, list(matches),
                                        f"Hash collision at {i} — no real match"))

        if i < n - m:
            window_hash = (window_hash - char_val(text[i]) + MOD) % MOD
            window_hash = (window_hash * pow(BASE, MOD - 2, MOD)) % MOD
            window_hash = (window_hash + char_val(text[i + m]) * power) % MOD

    steps.append(Step.complete(list(text),
                               f"Rabin-Karp done. Matches at: {matches}" if matches else "No matches found",
                               matches=matches))
    return AlgorithmResult(
        algorithm="rabin_karp", steps=steps, total_steps=len(steps),
        input_data={"text": text, "pattern": pattern},
        complexity={"time": "O(n + m) average", "space": "O(1)"}
    )


# ──────────────────── Z ALGORITHM ────────────────────────────────────

def z_algorithm(text: str, pattern: str) -> AlgorithmResult:
    steps: list[Step] = []
    matches = []
    combined = pattern + "$" + text
    n = len(combined)
    z = [0] * n
    z[0] = n
    l, r = 0, 0

    steps.append(Step(type=StepType.UPDATE, indices=[], array=list(combined),
                       description=f"Combined string: '{combined}' (pattern + '$' + text)",
                       extra={"combined": combined, "pattern_len": len(pattern)}))

    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and combined[z[i]] == combined[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
        steps.append(Step(type=StepType.UPDATE, indices=[i], array=list(combined),
                           description=f"Z[{i}]={z[i]}: longest prefix match at pos {i}",
                           extra={"z": list(z), "l": l, "r": r, "i": i}))
        if z[i] == len(pattern):
            match_start = i - len(pattern) - 1
            matches.append(match_start)
            steps.append(_str_step(StepType.FOUND, text, pattern, match_start, 0, list(matches),
                                    f"Pattern found at text index {match_start} (Z[{i}]={len(pattern)})",
                                    z_index=i, z_value=z[i]))

    steps.append(Step.complete(list(text),
                               f"Z Algorithm done. Matches at: {matches}" if matches else "No matches found",
                               matches=matches, z_array=z))
    return AlgorithmResult(
        algorithm="z_algorithm", steps=steps, total_steps=len(steps),
        input_data={"text": text, "pattern": pattern},
        complexity={"time": "O(n + m)", "space": "O(n + m)"}
    )


STRING_ALGORITHMS = {
    "kmp_search": kmp_search,
    "rabin_karp": rabin_karp,
    "z_algorithm": z_algorithm,
}