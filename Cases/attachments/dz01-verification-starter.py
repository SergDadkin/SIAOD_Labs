#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 1. Верификация ИИ-сгенерированной сортировки — стартовая заготовка.



Запуск: python dz01-verification-starter.py --variant N
"""

from __future__ import annotations

import argparse
import importlib.util
import random
import statistics
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable

SortFn = Callable[[list], list]

DEFAULT_BENCH_SIZES = [500, 1000, 2000, 4000, 8000]
RECURSION_LIMIT_HINT = (
    "RecursionError — превышена глубина рекурсии Python "
    "(sys.getrecursionlimit() по умолчанию ≈ 1000)"
)


# --------------------------------------------------------------------------- #
# Загрузка проверяемого модуля
# --------------------------------------------------------------------------- #
def load_sort_function(path: Path) -> SortFn:
    if not path.exists():
        raise SystemExit(f"[!] Файл не найден: {path}")
    spec = importlib.util.spec_from_file_location("candidate_sort", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"[!] Не удалось загрузить модуль из {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["candidate_sort"] = module
    spec.loader.exec_module(module)

    for name in ("quicksort", "sort", "sort_list", "merge_sort"):
        fn = getattr(module, name, None)
        if callable(fn):
            print(f"    найдена функция: {name}()")
            return fn
    raise SystemExit(
        f"[!] В {path} не найдена функция сортировки "
        "(ожидались quicksort / sort / sort_list / merge_sort)"
    )


# --------------------------------------------------------------------------- #
# Шаг 1. Инварианты
# --------------------------------------------------------------------------- #
def check_invariants(original: Iterable, result) -> list[str]:
    """Проверяет обязательные инварианты сортировки.

    Возвращает список нарушений (пустой список = инварианты выполнены):
      * упорядоченность по неубыванию;
      * перестановка (мультимножество элементов сохраняется);
      * тип результата — list.
    """
    violations: list[str] = []
    try:
        res = list(result)
    except TypeError:
        return [f"результат не итерируем: {type(result).__name__}"]

    if not isinstance(result, list):
        violations.append(f"результат не list, а {type(result).__name__}")

    for i in range(len(res) - 1):
        if res[i] > res[i + 1]:
            violations.append(
                f"нарушена упорядоченность: a[{i}]={res[i]!r} > a[{i + 1}]={res[i + 1]!r}"
            )
            break

    src = Counter(original)
    dst = Counter(res)
    if src != dst:
        lost = src - dst
        extra = dst - src
        parts = []
        if lost:
            parts.append(
                "потеряны " + ", ".join(
                    f"{k!r}×{v}" for k, v in sorted(lost.items(), key=lambda kv: repr(kv[0]))
                )
            )
        if extra:
            parts.append(
                "лишние " + ", ".join(
                    f"{k!r}×{v}" for k, v in sorted(extra.items(), key=lambda kv: repr(kv[0]))
                )
            )
        violations.append("нарушен инвариант перестановки: " + "; ".join(parts))

    return violations


# --------------------------------------------------------------------------- #
# Шаг 2. Репрезентативные тесты
# --------------------------------------------------------------------------- #
def build_representative_cases(rng: random.Random) -> list[tuple[str, list]]:
    return [
        ("граничный: пустой список", []),
        ("граничный: один элемент", [42]),
        ("граничный: два равных", [7, 7]),
        ("граничный: два по возрастанию", [1, 2]),
        ("граничный: два по убыванию", [2, 1]),
        ("вырожденный: все равны (10)", [5] * 10),
        ("вырожденный: уже отсортирован (малый)", list(range(10))),
        ("вырожденный: обратно отсортирован (малый)", list(range(10, 0, -1))),
        ("типовой: дубликаты", [3, 1, 2, 3, 1, 2, 3]),
        ("типовой: отрицательные + дубликаты", [-5, 3, -1, 0, -5, 2]),
        ("типовой: все отрицательные", [-1, -2, -3, -4, -5]),
        ("типовой: случайный малый", [rng.randint(-20, 20) for _ in range(15)]),
        ("типовой: случайный средний", [rng.randint(-1000, 1000) for _ in range(300)]),
        ("вырожденный: отсортирован большой (1200)", list(range(1200))),
        ("вырожденный: обратно отсортирован большой (1200)", list(range(1200, 0, -1))),
    ]


def run_representative_tests(sort_fn: SortFn, rng: random.Random) -> dict:
    results = []
    for name, data in build_representative_cases(rng):
        status, detail = "ok", ""
        try:
            got = sort_fn(list(data))
        except RecursionError:
            status, detail = "error", "RecursionError"
        except Exception as exc:  # noqa: BLE001 — фиксируем любое падение
            status, detail = "error", f"{type(exc).__name__}: {exc}"
        else:
            violations = check_invariants(data, got)
            if violations:
                status, detail = "fail", "; ".join(violations)
        results.append({"name": name, "size": len(data), "status": status, "detail": detail})

    summary = {
        "ok": sum(r["status"] == "ok" for r in results),
        "fail": sum(r["status"] == "fail" for r in results),
        "error": sum(r["status"] == "error" for r in results),
        "cases": results,
    }
    return summary


# --------------------------------------------------------------------------- #
# Шаг 3. Сравнение с эталоном sorted()
# --------------------------------------------------------------------------- #
def run_reference_comparison(sort_fn: SortFn, rng: random.Random, runs: int) -> dict:
    mismatches: list[tuple[list, list, list]] = []
    errors: list[tuple[list, str]] = []

    for _ in range(runs):
        n = rng.randint(0, 200)
        lo, hi = rng.choice([(-5, 5), (-100, 100), (0, 1000), (-1000, 0)])
        data = [rng.randint(lo, hi) for _ in range(n)]

        expected = sorted(data)
        try:
            got = sort_fn(list(data))
        except RecursionError:
            errors.append((data, "RecursionError"))
            continue
        except Exception as exc:  # noqa: BLE001
            errors.append((data, f"{type(exc).__name__}: {exc}"))
            continue

        got_list = list(got)
        if got_list != expected:
            mismatches.append((data, expected, got_list))

    minimal = None
    if mismatches:
        minimal = min(mismatches, key=lambda m: (len(m[0]), repr(m[0])))

    return {
        "runs": runs,
        "mismatches": len(mismatches),
        "errors": len(errors),
        "minimal": minimal,
        "first_errors": errors[:3],
    }


# --------------------------------------------------------------------------- #
# Шаг 4. Бенчмарк
# --------------------------------------------------------------------------- #
def time_call(sort_fn: SortFn, data: list, repeats: int = 5) -> tuple[float | None, str | None]:
    """Медиана времени по repeats прогонам; (None, причина) при ошибке."""
    try:
        sort_fn(list(data))  # прогрев
    except RecursionError:
        return None, "RecursionError"
    except Exception as exc:  # noqa: BLE001
        return None, type(exc).__name__

    times = []
    for _ in range(repeats):
        payload = list(data)
        t0 = time.perf_counter()
        try:
            sort_fn(payload)
        except RecursionError:
            return None, "RecursionError"
        except Exception as exc:  # noqa: BLE001
            return None, type(exc).__name__
        times.append(time.perf_counter() - t0)

    return statistics.median(times), None


def run_benchmark(sort_fn: SortFn, sizes: list[int], rng: random.Random) -> list[dict]:
    rows = []
    for n in sizes:
        row = {"n": n}
        datasets = {
            "random": [rng.randint(-n, n) for _ in range(n)],
            "sorted": list(range(n)),
            "reversed": list(range(n, 0, -1)),
        }
        for kind, data in datasets.items():
            median, error = time_call(sort_fn, data)
            row[kind] = {"median": median, "error": error}
        rows.append(row)
    return rows


# --------------------------------------------------------------------------- #
# Отчёт
# --------------------------------------------------------------------------- #
def _fmt_time(cell: dict) -> str:
    if cell["error"]:
        return cell["error"]
    return f"{cell['median'] * 1000:.2f} ms"


def print_report(variant: int, seed: int, code_path: Path, rep: dict, ref: dict, bench: list[dict]) -> bool:
    line = "=" * 72
    print(line)
    print("  ДЗ-01. Верификация ИИ-кода сортировки")
    print(line)
    print(f"  Вариант:      {variant}")
    print(f"  Seed:         {seed}")
    print(f"  Проверяемый:  {code_path}")

    print("\n--- Шаг 1. Инварианты сортировки ---")
    print("  ✓ упорядоченность по неубыванию")
    print("  ✓ перестановка (мультимножество элементов сохраняется)")
    print("  ✓ тип результата — list")
    print("  Реализация: check_invariants()")

    print("\n--- Шаг 2. Репрезентативные тесты ---")
    for case in rep["cases"]:
        if case["status"] == "ok":
            mark, tail = "OK  ", ""
        elif case["status"] == "fail":
            mark, tail = "FAIL", f"  → {case['detail']}"
        else:
            mark, tail = "ERR ", f"  → {case['detail']}"
        print(f"  [{mark}] {case['name']}{tail}")
    print(
        f"  Итого: ok={rep['ok']}, fail={rep['fail']}, error={rep['error']} "
        f"(всего {len(rep['cases'])})"
    )
    if rep["error"]:
        print(f"  {RECURSION_LIMIT_HINT}")

    print("\n--- Шаг 3. Сравнение с эталоном sorted() ---")
    print(f"  Прогонов:        {ref['runs']}")
    print(f"  Расхождений:     {ref['mismatches']}")
    print(f"  Ошибок:          {ref['errors']}")
    if ref["minimal"]:
        data, expected, got = ref["minimal"]
        print(f"  Минимальный контрпример (длина {len(data)}):")
        print(f"    вход:     {data}")
        print(f"    ожидалось: {expected}")
        print(f"    получено:  {got}")
    if ref["first_errors"]:
        print("  Первые ошибки:")
        for data, err in ref["first_errors"]:
            snippet = data[:12]
            print(f"    {err}: вход длины {len(data)} {snippet}{'...' if len(data) > 12 else ''}")

    print("\n--- Шаг 4. Сложность и производительность ---")
    print("  Аналитика (худший случай): на упорядоченном/обратно упорядоченном")
    print("  входе опорный элемент — минимум/максимум, разбиение 0 : n-1,")
    print("  T(n) = T(n-1) + Θ(n) = Θ(n²), глубина рекурсии — n, а не log n.")
    print()
    header = f"  {'n':>6} | {'random':>14} | {'sorted':>14} | {'reversed':>14}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for row in bench:
        print(
            f"  {row['n']:>6} | {_fmt_time(row['random']):>14} | "
            f"{_fmt_time(row['sorted']):>14} | {_fmt_time(row['reversed']):>14}"
        )
    print("  (прогрев + медиана из 5 прогонов, time.perf_counter)")

    correct = rep["fail"] == 0 and rep["error"] == 0 and ref["mismatches"] == 0 and ref["errors"] == 0
    bench_ok = all(
        cell["error"] is None for row in bench for cell in (row["random"], row["sorted"], row["reversed"])
    )
    verdict = "ACCEPT" if correct and bench_ok else "REJECT"

    print("\n--- Вердикт ---")
    if verdict == "ACCEPT":
        print("  ACCEPT: инварианты выполняются, расхождений с эталоном нет,")
        print("  аварийных завершений и квадратичного роста на бенчмарке нет.")
    else:
        print("  REJECT:")
        if rep["fail"] or ref["mismatches"]:
            print("   • нарушен инвариант перестановки — теряются элементы,")
            print("     равные опорному (строгие < и > в разбиении).")
        if rep["error"] or any(
            cell["error"] == "RecursionError"
            for row in bench
            for cell in (row["random"], row["sorted"], row["reversed"])
        ):
            print("   • деградация до Θ(n²) и RecursionError на упорядоченном входе")
            print("     (pivot = data[0]).")
        if not bench_ok:
            print("   • бенчмарк не пройден полностью: см. таблицу выше.")
    print(line)
    return verdict == "ACCEPT"


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ДЗ-01. Верификация ИИ-кода сортировки")
    parser.add_argument("--variant", type=int, default=1, help="номер варианта (seed = 30 + variant)")
    parser.add_argument(
        "--code",
        type=Path,
        default=Path(__file__).with_name("dz01-ai-code.py"),
        help="путь к проверяемому файлу (по умолчанию dz01-ai-code.py рядом со скриптом)",
    )
    parser.add_argument("--runs", type=int, default=300, help="число случайных прогонов на шаге 3")
    parser.add_argument(
        "--bench-sizes",
        type=int,
        nargs="*",
        default=DEFAULT_BENCH_SIZES,
        help="размеры входов для бенчмарка",
    )
    args = parser.parse_args(argv)

    seed = 30 + args.variant
    rng = random.Random(seed)

    print(f"[*] Загружаю проверяемый модуль: {args.code}")
    sort_fn = load_sort_function(args.code)
    print(f"[*] Seed = {seed}\n")

    rep = run_representative_tests(sort_fn, rng)
    ref = run_reference_comparison(sort_fn, random.Random(seed + 1), args.runs)
    bench = run_benchmark(sort_fn, args.bench_sizes, random.Random(seed + 2))

    accepted = print_report(args.variant, seed, args.code, rep, ref, bench)
    return 0 if accepted else 1


if __name__ == "__main__":
    sys.exit(main())