#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fast sorting utilities (fixed version).

Исправления относительно исходного ИИ-кода:
  * потеря элементов, равных опорному → трёхпутевое разбиение (<, ==, >);
  * деградация до Θ(n²) и RecursionError на упорядоченном входе
    → случайный выбор опорного элемента.

Time complexity: O(n log n) expected, O(n²) worst-case (very unlikely).
Space complexity: O(log n) expected recursion stack, O(n) worst-case.
The input list is not modified; a new sorted list is returned.

>>> quicksort([3, 1, 2])
[1, 2, 3]
>>> quicksort([])
[]
>>> quicksort([1, 1, 1])
[1, 1, 1]
"""

from __future__ import annotations

import random


def quicksort(data: list[int]) -> list[int]:
    """Sort a list of integers using 3-way quicksort with random pivot.

    Time complexity: O(n log n) expected, O(n²) worst-case (rare).
    Space complexity: O(log n) expected recursion stack, O(n) worst-case.
    The input list is not modified; a new sorted list is returned.
    """
    if len(data) <= 1:
        return list(data)

    pivot = random.choice(data)
    smaller = [x for x in data if x < pivot]
    equal = [x for x in data if x == pivot]
    larger = [x for x in data if x > pivot]

    return quicksort(smaller) + equal + quicksort(larger)


if __name__ == "__main__":
    example = [5, 2, 9, 1, 7]
    print("Input :", example)
    print("Sorted:", quicksort(example))
    print("Dupes :", quicksort([7, 7]))
    print("All eq:", quicksort([5] * 10))