#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 6. Поиск в линейных структурах: линейный, бинарный,
интерполяционный поиск и их экспериментальное сравнение.
"""

from __future__ import annotations

import bisect
import random
import statistics
import time
from typing import Callable

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Алгоритмы поиска
# ---------------------------------------------------------------------------

def linear_search(a: list[float], key: float) -> tuple[int, int]:
    """Линейный поиск. Возвращает (index, probes); index = -1, если не найден."""
    probes = 0
    for i in range(len(a)):
        probes += 1
        if a[i] == key:
            return i, probes
    return -1, probes

def binary_search(a: list[float], key: float) -> tuple[int, int]:
    """Бинарный поиск. Инвариант: элемент (если есть) всегда в [lo, hi]."""
    lo, hi = 0, len(a) - 1
    probes = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        probes += 1
        if a[mid] == key:
            return mid, probes
        elif a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, probes

def interpolation_search(a: list[float], key: float) -> tuple[int, int]:
    """Интерполяционный поиск. O(log log n) на равномерных данных."""
    lo, hi = 0, len(a) - 1
    probes = 0
    while lo <= hi and a[lo] <= key <= a[hi]:
        denom = a[hi] - a[lo]
        if denom == 0:
            probes += 1
            return (lo, probes) if a[lo] == key else (-1, probes)
        mid = lo + int((key - a[lo]) * (hi - lo) / denom)
        mid = max(lo, min(mid, hi))
        probes += 1
        if a[mid] == key:
            return mid, probes
        elif a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, probes

ALGS: list[tuple[str, Callable]] = [
    ("linear", linear_search),
    ("binary", binary_search),
    ("interpolation", interpolation_search),
]

# ---------------------------------------------------------------------------
# 2. Верификация (сверка с bisect)
# ---------------------------------------------------------------------------

def verify_searches() -> None:
    """Проверяет все три алгоритма на граничных и случайных данных."""
    rng = random.Random(123)
    test_arrays: list[list[float]] = [
        [], [5.0], [1.0, 2.0, 3.0, 4.0, 5.0],
        [1.0, 1.0, 1.0, 1.0],
        [0.0, 10.0, 20.0, 30.0, 40.0, 50.0],
        [-5.0, -5.0, 0.0, 0.0, 5.0, 5.0],
    ]
    for _ in range(40):
        n = rng.randint(0, 25)
        test_arrays.append(sorted(rng.uniform(-15.0, 15.0) for _ in range(n)))

    for a in test_arrays:
        n = len(a)
        if n == 0:
            keys = [0.0]
        else:
            keys = set(a)
            keys.add(a[0] - 1.0)
            keys.add(a[-1] + 1.0)
            for i in range(n - 1):
                if a[i] != a[i + 1]:
                    keys.add((a[i] + a[i + 1]) / 2.0)
            keys = list(keys)

        for key in keys:
            idx = bisect.bisect_left(a, key)
            present = idx < n and a[idx] == key
            for name, fn in ALGS:
                got, _ = fn(a, key)
                if present:
                    assert got != -1 and a[got] == key, \
                        f"{name}({a}, {key}) = {got}: ключ присутствует"
                else:
                    assert got == -1, \
                        f"{name}({a}, {key}) = {got}: ожидалось -1"
    print(f"[OK] Верификация пройдена: {len(test_arrays)} массивов, "
          f"все три алгоритма совпали с bisect.\n")

# ---------------------------------------------------------------------------
# 3. Генерация данных
# ---------------------------------------------------------------------------

def make_uniform(n: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    return sorted(rng.uniform(0.0, 1.0) for _ in range(n))

def make_exponential(n: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    return sorted(rng.expovariate(1.0) for _ in range(n))

def make_keys(a: list[float], dist: str, n_keys: int, seed: int
              ) -> tuple[list[float], list[float]]:
    """Возвращает (present, absent) — ключи, которые (не) есть в массиве."""
    if not a:
        return [], []
    rng = random.Random(seed + 7)
    n = len(a)
    present = [a[rng.randrange(n)] for _ in range(n_keys)]

    absent: list[float] = []
    attempts = 0
    while len(absent) < n_keys and attempts < n_keys * 50:
        attempts += 1
        if dist == "uniform":
            k = rng.uniform(a[0], a[-1])
        else:
            k = rng.expovariate(1.0)
        i = bisect.bisect_left(a, k)
        if i >= n or a[i] != k:
            absent.append(k)
    return present, absent

# ---------------------------------------------------------------------------
# 4. Замеры
# ---------------------------------------------------------------------------

def avg_probes(fn: Callable, a: list[float], keys: list[float]) -> float:
    if not keys:
        return 0.0
    return sum(fn(a, k)[1] for k in keys) / len(keys)

def measure_time(fn: Callable, a: list[float], keys: list[float],
                 repeats: int = 5) -> float:
    """Медиана времени по repeats повторам (с прогревом)."""
    if not keys:
        return 0.0
    for k in keys[:3]:
        fn(a, k)
    samples: list[float] = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        for k in keys:
            fn(a, k)
        samples.append(time.perf_counter() - t0)
    return statistics.median(samples)

def n_keys_probes(n: int) -> int:
    return 50 if n <= 100_000 else 15

def n_keys_time(n: int) -> int:
    if n <= 10_000:   return 100
    if n <= 100_000:  return 20
    return 5

# ---------------------------------------------------------------------------
# 5. Основной эксперимент
# ---------------------------------------------------------------------------

def run_experiment() -> dict[tuple[str, str, int], dict[str, float]]:
    sizes = [100, 1_000, 10_000, 100_000, 1_000_000]
    results: dict[tuple[str, str, int], dict[str, float]] = {}

    for dist in ("uniform", "exponential"):
        print(f"--- распределение: {dist} ---")
        for n in sizes:
            seed = 1_000 + n
            a = make_uniform(n, seed) if dist == "uniform" else make_exponential(n, seed)

            keys_present, keys_absent = make_keys(a, dist, n_keys_probes(n), seed)
            kt_present,  kt_absent   = make_keys(a, dist, n_keys_time(n),   seed + 1)

            for name, fn in ALGS:
                results[(dist, name, n)] = {
                    "probes_present": avg_probes(fn, a, keys_present),
                    "probes_absent":  avg_probes(fn, a, keys_absent),
                    "time_present":   measure_time(fn, a, kt_present),
                    "time_absent":    measure_time(fn, a, kt_absent),
                }
            print(f"  n = {n:>9}  ok")
        print()
    return results

# ---------------------------------------------------------------------------
# 6. Графики и сводка
# ---------------------------------------------------------------------------

def plot_results(results: dict[tuple[str, str, int], dict[str, float]]) -> None:
    sizes = [100, 1_000, 10_000, 100_000, 1_000_000]
    for dist in ("uniform", "exponential"):
        for metric, label in [
            ("probes_present", "Среднее число сравнений (присутствующие ключи)"),
            ("time_present",   "Время поиска, с (присутствующие ключи)"),
        ]:
            plt.figure(figsize=(8, 5))
            for name, _ in ALGS:
                ys = [results[(dist, name, n)][metric] for n in sizes]
                plt.plot(sizes, ys, marker="o", label=name)
            plt.xscale("log")
            plt.yscale("log")
            plt.xlabel("n (log)")
            plt.ylabel(label + " (log)")
            plt.title(f"{dist} — {metric}")
            plt.grid(True, which="both", alpha=0.3)
            plt.legend()
            fname = f"lab06_{dist}_{metric}.png"
            plt.savefig(fname, dpi=120, bbox_inches="tight")
            plt.close()
            print(f"Сохранён {fname}")

def print_summary(results: dict[tuple[str, str, int], dict[str, float]]) -> None:
    sizes = [100, 1_000, 10_000, 100_000, 1_000_000]
    for metric, title in [
        ("probes_present", "Среднее число сравнений (присутствующие)"),
        ("probes_absent",  "Среднее число сравнений (отсутствующие)"),
        ("time_present",   "Время, с (присутствующие)"),
        ("time_absent",    "Время, с (отсутствующие)"),
    ]:
        print(f"\n=== {title} ===")
        print(f"{'распред.':<12} {'n':>10} "
              f"{'linear':>12} {'binary':>12} {'interp':>12}")
        for dist in ("uniform", "exponential"):
            for n in sizes:
                row = [results[(dist, a, n)][metric] for a, _ in ALGS]
                print(f"{dist:<12} {n:>10} "
                      f"{row[0]:>12.4g} {row[1]:>12.4g} {row[2]:>12.4g}")

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    verify_searches()
    res = run_experiment()
    print_summary(res)
    plot_results(res)