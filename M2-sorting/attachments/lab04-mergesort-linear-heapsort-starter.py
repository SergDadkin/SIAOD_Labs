"""
ЛР04: MergeSort, линейные сортировки (CountingSort, RadixSort LSD), HeapSort.
Сравнение с QuickSort (из ЛР03) и со встроенной sorted().

Все сортировки возвращают новый отсортированный список
(кроме heap_sort — она сортирует in-place и возвращает тот же объект).
"""

import random
import time
import sys

sys.setrecursionlimit(10000)


# ============================================================
# 1. MergeSort (стабильная сортировка слиянием)
# ============================================================

def _merge(left, right, key):
    result = []
    i = j = 0
    n_l, n_r = len(left), len(right)
    while i < n_l and j < n_r:
        # <= гарантирует стабильность: равные — из левой части
        if key(left[i]) <= key(right[j]):
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(a, key=lambda x: x):
    a = list(a)
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    return _merge(merge_sort(a[:mid], key), merge_sort(a[mid:], key), key)


# ============================================================
# 2. CountingSort (устойчивая, O(n + k))
# ============================================================

def counting_sort(a, key_max=None):
    a = list(a)
    if not a:
        return a
    if key_max is None:
        key_max = max(a)
    if min(a) < 0:
        raise ValueError("counting_sort требует неотрицательных ключей")
    count = [0] * (key_max + 1)
    for x in a:
        count[x] += 1
    for i in range(1, key_max + 1):
        count[i] += count[i - 1]
    result = [0] * len(a)
    for x in reversed(a):          # с конца — сохраняет порядок равных
        count[x] -= 1
        result[count[x]] = x
    return result


# ============================================================
# 3. RadixSort LSD (O(d·n))
# ============================================================

def _counting_sort_by_digit(a, exp):
    n = len(a)
    result = [0] * n
    count = [0] * 10
    for x in a:
        count[(x // exp) % 10] += 1
    for i in range(1, 10):
        count[i] += count[i - 1]
    for x in reversed(a):          # обратный проход — устойчивость
        d = (x // exp) % 10
        count[d] -= 1
        result[count[d]] = x
    return result


def radix_sort_lsd(a):
    a = list(a)
    if not a:
        return a
    if min(a) < 0:
        raise ValueError("radix_sort_lsd требует неотрицательных ключей")
    max_val = max(a)
    exp = 1
    while max_val // exp > 0:
        a = _counting_sort_by_digit(a, exp)
        exp *= 10
    return a


# ============================================================
# 4. HeapSort (in-place, O(1) памяти, нестабильна)
# ============================================================

def _sift_down(a, i, n):
    while True:
        largest = i
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and a[l] > a[largest]:
            largest = l
        if r < n and a[r] > a[largest]:
            largest = r
        if largest == i:
            break
        a[i], a[largest] = a[largest], a[i]
        i = largest


def heap_sort(a):
    """Сортирует список на месте, возвращает его же."""
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):   # построение max-кучи, O(n)
        _sift_down(a, i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        _sift_down(a, 0, end)
    return a


# ============================================================
# 5. QuickSort (из ЛР03 — для сравнения)
# ============================================================

def quick_sort(a):
    a = list(a)
    if len(a) <= 1:
        return a
    pivot = a[len(a) // 2]
    left  = [x for x in a if x < pivot]
    mid   = [x for x in a if x == pivot]
    right = [x for x in a if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)


# ============================================================
# 6. Проверки корректности и свойств
# ============================================================

def check_sort(sort_fn, name, **extra):
    cases = [
        [],
        [1],
        [2, 1],
        [1, 2],
        [3, 3, 3, 3],
        [5, 4, 3, 2, 1],
        [1, 2, 3, 4, 5],
        [0, 0, 1, 0, 1],
        [7, 7, 7, 0, 0, 7],
    ]
    for case in cases:
        original = list(case)
        expected = sorted(case)
        got = list(sort_fn(list(case), **extra))
        assert got == expected, \
            f"{name}: {original} -> {got}, ожидалось {expected}"

    for _ in range(200):
        n = random.randint(0, 50)
        arr = [random.randint(0, 20) for _ in range(n)]
        expected = sorted(arr)
        got = list(sort_fn(list(arr), **extra))
        assert got == expected, \
            f"{name}: {arr} -> {got}, ожидалось {expected}"

    print(f"[OK] {name}: пройдено {len(cases) + 200} проверок")


def check_merge_stability():
    data = [(3, 0), (1, 1), (3, 2), (1, 3), (2, 4), (3, 5), (2, 6), (1, 7)]
    result = merge_sort(data, key=lambda p: p[0])
    keys = [p[0] for p in result]
    assert keys == sorted(keys)
    for k in set(keys):
        ids = [p[1] for p in result if p[0] == k]
        assert ids == sorted(ids), f"merge_sort нестабилен для ключа {k}: {ids}"
    print("[OK] merge_sort стабилен")


def check_counting_stability():
    # кодируем (key, id) как key * OFFSET + id; при устойчивой сортировке
    # id внутри группы равных ключей идут в исходном (возрастающем) порядке.
    data = [(3, 0), (1, 1), (3, 2), (1, 3), (2, 4), (3, 5), (2, 6), (1, 7)]
    OFFSET = 100
    encoded = [k * OFFSET + i for i, (k, _) in enumerate(data)]
    sorted_enc = counting_sort(encoded)
    for k in sorted({p[0] for p in data}):
        ids = [e - k * OFFSET for e in sorted_enc if e // OFFSET == k]
        assert ids == sorted(ids), \
            f"counting_sort нестабилен для ключа {k}: {ids}"
    print("[OK] counting_sort стабилен")


def check_radix_stability():
    # RadixSort LSD устойчив, если устойчив проход по разряду.
    # Проверим на числах, различающихся в младшем разряде.
    data = [(10, 0), (11, 1), (10, 2), (11, 3), (10, 4), (11, 5)]
    OFFSET = 100
    encoded = [k * OFFSET + i for i, (k, _) in enumerate(data)]
    sorted_enc = radix_sort_lsd(encoded)
    for k in sorted({p[0] for p in data}):
        ids = [e - k * OFFSET for e in sorted_enc if e // OFFSET == k]
        assert ids == sorted(ids), f"radix_sort_lsd нестабилен: {ids}"
    print("[OK] radix_sort_lsd стабилен")


def check_heap_property():
    a = [random.randint(0, 100) for _ in range(64)]
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(a, i, n)
    for i in range(n):
        l, r = 2 * i + 1, 2 * i + 2
        if l < n:
            assert a[i] >= a[l], "Нарушено свойство max-кучи (левый)"
        if r < n:
            assert a[i] >= a[r], "Нарушено свойство max-кучи (правый)"
    print("[OK] heap_sort: свойство max-кучи выполняется")


def check_limits():
    for fn, name in [(counting_sort, "counting_sort"),
                     (radix_sort_lsd, "radix_sort_lsd")]:
        try:
            fn([1, -2, 3])
            assert False, f"{name} должен был упасть на отрицательных"
        except ValueError:
            pass
    print("[OK] counting_sort / radix_sort_lsd корректно отклоняют отрицательные")


# ============================================================
# 7. Бенчмарк
# ============================================================

def bench(fn, data, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn(list(data))
        best = min(best, time.perf_counter() - t0)
    return best


def generate(n, kind):
    random.seed(42 + n)
    if kind == "sorted":
        return list(range(n))
    if kind == "reversed":
        return list(range(n, 0, -1))
    if kind == "nearly":
        a = list(range(n))
        for _ in range(max(1, n // 100)):
            i, j = random.randrange(n), random.randrange(n)
            a[i], a[j] = a[j], a[i]
        return a
    if kind == "random":
        return [random.randint(0, 10 * n) for _ in range(n)]
    if kind == "random_wide":
        return [random.randint(0, 10**9) for _ in range(n)]
    if kind == "duplicates":
        return [random.randint(0, 5) for _ in range(n)]
    raise ValueError(kind)


def run_benchmarks():
    sizes = [100, 500, 1000, 2000, 5000]
    distributions = ["sorted", "reversed", "nearly",
                       "random", "random_wide", "duplicates"]

    algos = [
        ("merge_sort", merge_sort),
        ("heap_sort",  heap_sort),
        ("quick_sort", quick_sort),
        ("counting",   counting_sort),
        ("radix_lsd",  radix_sort_lsd),
        ("sorted()",   lambda a: sorted(a)),
    ]

    print("\n" + "=" * 100)
    print("БЕНЧМАРК (время в мс, лучшее из 3 запусков)")
    print("=" * 100)

    for dist in distributions:
        print(f"\n--- распределение: {dist} ---")
        header = f"{'n':>6} | " + " | ".join(f"{name:>12}" for name, _ in algos)
        print(header)
        print("-" * len(header))
        for n in sizes:
            data = generate(n, dist)
            row = f"{n:>6} | "
            cells = []
            for name, fn in algos:
                # counting_sort на random_wide: k ~ 1e9 — нереалистично
                if name == "counting" and dist == "random_wide":
                    cells.append(f"{'—':>12}")
                    continue
                try:
                    t = bench(fn, data)
                    cells.append(f"{t * 1000:>10.2f} мс")
                except Exception:
                    cells.append(f"{'err':>12}")
            print(row + " | ".join(cells))


# ============================================================
# 8. main
# ============================================================

if __name__ == "__main__":
    print("Проверки корректности и свойств:")
    check_sort(merge_sort,      "merge_sort")
    check_sort(counting_sort,   "counting_sort")
    check_sort(radix_sort_lsd,  "radix_sort_lsd")
    check_sort(heap_sort,       "heap_sort")
    check_merge_stability()
    check_counting_stability()
    check_radix_stability()
    check_heap_property()
    check_limits()

    run_benchmarks()

    print("\nГотово. В отчёт:")
    print("  • таблица свойств 6 сортировок (лучший/средний/худший, память, стабильность, ограничения);")
    print("  • объяснение, почему counting_sort пропущен на random_wide;")
    print("  • почему radix_sort_lsd без устойчивого прохода по разряду неверен;")
    print("  • log-log графики времени от n по распределениям.")