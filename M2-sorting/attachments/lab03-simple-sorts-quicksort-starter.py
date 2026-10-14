#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Алгоритмы сортировки"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
import time
from pathlib import Path

# Увеличиваем лимит рекурсии, так как быстрая сортировка на плохих входах может уйти глубоко
sys.setrecursionlimit(50000)

# Параметры эксперимента
SIZES = (1_000, 3_000, 10_000, 30_000)  # Ограничим квадратичные тесты 30k для экономии времени
REPEATS = 5

# ---------------------------------------------------------------------------
# Алгоритмы сортировки
# ---------------------------------------------------------------------------

def insertion_sort(arr: list[int]) -> list[int]:
    """Сортировка вставками. Временная сложность: O(n²)."""
    a = arr.copy()  # Работаем с копией, чтобы не портить исходные данные
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def quick_sort(arr: list[int]) -> list[int]:
    """Быстрая сортировка (Разделяй и властвуй). Временная сложность: O(n log n)."""
    a = arr.copy()
    
    def _quicksort(left: int, right: int):
        if left >= right:
            return
        
        # Выбираем случайный опорный элемент для защиты от худшего случая O(n²)
        pivot_idx = random.randint(left, right)
        pivot = a[pivot_idx]
        
        i, j = left, right
        while i <= j:
            while a[i] < pivot:
                i += 1
            while a[j] > pivot:
                j -= 1
            if i <= j:
                a[i], a[j] = a[j], a[i]
                i += 1
                j -= 1
                
        _quicksort(left, j)
        _quicksort(i, right)

    _quicksort(0, len(a) - 1)
    return a

# ---------------------------------------------------------------------------
# Сервисные функции и замеры
# ---------------------------------------------------------------------------

def find_data_dir(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    for base in (Path.cwd(), Path(__file__).resolve().parent):
        for parent in (base, *base.parents):
            path = parent / "data" / "generated"
            if path.is_dir():
                return path
    raise SystemExit("Не найден каталог data/generated. Сгенерируйте данные.")


def load_array(data_dir: Path, kind: str, n: int) -> list[int]:
    path = data_dir / f"arrays_{kind}_{n}.txt"
    if not path.is_file():
        # Если файла нет, попробуем взять случайный префикс из доступных
        path = data_dir / f"arrays_random_{n}.txt"
    if not path.is_file():
        raise SystemExit(f"Не найден файл данных: {path}")
    return [int(line) for line in path.read_text(encoding="utf-8").split()]


def bench(call) -> float:
    call()  # Прогрев
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        call()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)

# ---------------------------------------------------------------------------
# Основной запуск и графики
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", type=int, required=True)
    ap.add_argument("--data", type=Path, default=None)
    args = ap.parse_args()

    data_dir = find_data_dir(args.data)
    print(f"--- Тестирование алгоритмов (Вариант {args.variant}) ---")
    
    # Smoke-тест на корректность
    test_arr = [5, 2, 9, 1, 5, 6]
    assert sorted(test_arr) == insertion_sort(test_arr)
    assert sorted(test_arr) == quick_sort(test_arr)
    print("[OK] Тесты на корректность успешно пройдены.\n")

    results = {"insertion": [], "quicksort": []}

    print("Замеры производительности:")
    print(f"{'N':>7} | {'Insertion (O(n²))':>18} | {'QuickSort (O(n log n))':>22}")
    print("-" * 55)

    for n in SIZES:
        arr = load_array(data_dir, "random", n)
        
        t_insert = bench(lambda: insertion_sort(arr))
        results["insertion"].append((n, t_insert))
        
        t_quick = bench(lambda: quick_sort(arr))
        results["quicksort"].append((n, t_quick))
        
        print(f"{n:>7} | {t_insert:>16.5f} c | {t_quick:>20.5f} c")

    # Построение графиков
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots(figsize=(7, 5))
        
        ns_i, ts_i = zip(*results["insertion"])
        ns_q, ts_q = zip(*results["quicksort"])
        
        ax.plot(ns_i, ts_i, marker="o", color="red", label="Insertion Sort O(n²)")
        ax.plot(ns_q, ts_q, marker="s", color="blue", label="Quick Sort O(n log n)")
        
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Размер массива N")
        ax.set_ylabel("Время работы, с")
        ax.set_title("Сравнение алгоритмов сортировки (Log-Log оси)")
        ax.grid(True, which="both", linewidth=0.3)
        ax.legend()
        
        fig.tight_layout()
        out_path = Path.cwd() / "lab03_sorting_results.png"
        fig.savefig(out_path, dpi=150)
        print(f"\n[INFO] График успешно сохранен в файл: {out_path}")
    except ImportError:
        print("\n[WARN] matplotlib не установлен, построение графика пропущено.")


if __name__ == "__main__":
    main()
