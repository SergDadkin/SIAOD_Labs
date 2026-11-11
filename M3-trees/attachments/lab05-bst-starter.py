#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 5. Бинарное дерево поиска: обходы, вставка и удаление."""

from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback
from collections import deque

# ---------------------------------------------------------------------------
# 1. Бинарное дерево поиска (BST)
# ---------------------------------------------------------------------------
class Node:
    """Узел BST: ключ и ссылки на левое и правое поддеревья."""
    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


class BST:
    """Бинарное дерево поиска без дубликатов ключей.

    Инвариант: для каждого узла все ключи левого поддерева меньше key,
    все ключи правого — больше.
    """

    def __init__(self) -> None:
        self.root: Node | None = None

    def insert(self, key: int) -> None:
        """Вставка ключа; повторная вставка существующего ключа игнорируется."""
        if self.root is None:
            self.root = Node(key)
            return
        node = self.root
        while True:
            if key < node.key:
                if node.left is None:
                    node.left = Node(key)
                    return
                node = node.left
            elif key > node.key:
                if node.right is None:
                    node.right = Node(key)
                    return
                node = node.right
            else:
                return  # дубликат игнорируется

    def search(self, key: int) -> bool:
        """Возвращает True, если ключ есть в дереве."""
        node = self.root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def delete(self, key: int) -> None:
        """Удаление ключа. Обрабатывает три случая: лист, один ребёнок, два ребёнка."""
        self.root = self._delete_node(self.root, key)

    def _delete_node(self, node: Node | None, key: int) -> Node | None:
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete_node(node.left, key)
        elif key > node.key:
            node.right = self._delete_node(node.right, key)
        else:
            # Нашли узел для удаления
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # Два ребёнка: ищем преемника (минимум в правом поддереве)
            successor = self._min_node(node.right)
            node.key = successor.key
            node.right = self._delete_node(node.right, successor.key)
        return node

    @staticmethod
    def _min_node(node: Node) -> Node:
        while node.left is not None:
            node = node.left
        return node

    # -- Обходы --------------------------------------------------------------
    def in_order(self) -> list[int]:
        """Симметричный обход (лево — узел — право): рекурсивно."""
        result: list[int] = []
        self._in_order(self.root, result)
        return result

    def _in_order(self, node: Node | None, acc: list[int]) -> None:
        if node is None:
            return
        self._in_order(node.left, acc)
        acc.append(node.key)
        self._in_order(node.right, acc)

    def pre_order(self) -> list[int]:
        """Прямой обход (узел — лево — право): рекурсивно."""
        result: list[int] = []
        self._pre_order(self.root, result)
        return result

    def _pre_order(self, node: Node | None, acc: list[int]) -> None:
        if node is None:
            return
        acc.append(node.key)
        self._pre_order(node.left, acc)
        self._pre_order(node.right, acc)

    def post_order(self) -> list[int]:
        """Обратный обход (лево — право — узел): рекурсивно."""
        result: list[int] = []
        self._post_order(self.root, result)
        return result

    def _post_order(self, node: Node | None, acc: list[int]) -> None:
        if node is None:
            return
        self._post_order(node.left, acc)
        self._post_order(node.right, acc)
        acc.append(node.key)

    def level_order(self) -> list[int]:
        """Обход в ширину по уровням: итеративно через очередь (deque)."""
        if self.root is None:
            return []
        result: list[int] = []
        q = deque([self.root])
        while q:
            node = q.popleft()
            result.append(node.key)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        return result

    # -- Характеристики дерева -----------------------------------------------
    def height(self) -> int:
        """Высота дерева в рёбрах (пустое = -1, один узел = 0)."""
        return self._height(self.root)

    def _height(self, node: Node | None) -> int:
        if node is None:
            return -1
        return 1 + max(self._height(node.left), self._height(node.right))

    def size(self) -> int:
        """Число узлов в дереве."""
        return self._size(self.root)

    def _size(self, node: Node | None) -> int:
        if node is None:
            return 0
        return 1 + self._size(node.left) + self._size(node.right)


# ---------------------------------------------------------------------------
# 2. Верификация (из заготовки, оставлена без изменений)
# ---------------------------------------------------------------------------
class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SelfCheckError(message)


def build(keys) -> BST:
    tree = BST()
    for k in keys:
        tree.insert(k)
    return tree


def expect_search(tree: BST, key: int, present: bool, where: str) -> None:
    got = tree.search(key)
    expect(got is present, f"{where}: search({key}) вернул {got!r}, ожидалось {present}")


TRAVERSALS = ("in_order", "pre_order", "post_order", "level_order")

KNOWN_TREES = {
    (4, 2, 6, 1, 3, 5, 7): {
        "in_order": [1, 2, 3, 4, 5, 6, 7],
        "pre_order": [4, 2, 1, 3, 6, 5, 7],
        "post_order": [1, 3, 2, 5, 7, 6, 4],
        "level_order": [4, 2, 6, 1, 3, 5, 7],
        "height": 2,
        "size": 7,
    },
    (8, 3, 10, 1, 6, 14, 4, 7, 13): {
        "in_order": [1, 3, 4, 6, 7, 8, 10, 13, 14],
        "pre_order": [8, 3, 1, 6, 4, 7, 10, 14, 13],
        "post_order": [1, 4, 7, 6, 3, 13, 14, 10, 8],
        "level_order": [8, 3, 10, 1, 6, 14, 4, 7, 13],
        "height": 3,
        "size": 9,
    },
}

TWO_CHILDREN_CASES = [
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 3, [8, 4, 1, 6, 7, 10, 14, 13], [8, 1, 6, 4, 7, 10, 14, 13]),
    ((8, 3, 10, 1, 6, 14, 4, 7, 13), 6, [8, 3, 1, 7, 4, 10, 14, 13], [8, 3, 1, 4, 7, 10, 14, 13]),
]


def check_insert_search() -> None:
    for keys in ((), (5,), (2, 1, 3), (5, 3, 8, 1, 4, 7, 9)):
        tree = build(keys)
        for k in range(11):
            expect_search(tree, k, k in keys, f"дерево из вставок {keys}")
        got = tree.in_order()
        expect(got == sorted(keys), f"in_order() после вставок {keys}: {got}, ожидалось {sorted(keys)}")
        tree.insert(5)
        tree.insert(1)
        got = tree.in_order()
        expect(got == sorted(keys), f"повторная вставка 5 и 1 изменила дерево: in_order() = {got}")


def check_traversals() -> None:
    empty = BST()
    for name in TRAVERSALS:
        got = getattr(empty, name)()
        expect(got == [], f"{name}() пустого дерева: {got}, ожидалось []")
    for keys, answer in KNOWN_TREES.items():
        tree = build(keys)
        for name in TRAVERSALS:
            got = getattr(tree, name)()
            expect(got == answer[name], f"{name}() дерева из вставок {list(keys)}: {got}, ожидалось {answer[name]}")


def check_height_size() -> None:
    cases = [("пустое дерево", (), -1, 0), ("один узел 5", (5,), 0, 1)]
    cases += [(f"дерево из вставок {list(keys)}", keys, answer["height"], answer["size"])
              for keys, answer in KNOWN_TREES.items()]
    cases.append(("ключи 1, 2, …, 50 по возрастанию (цепочка)", tuple(range(1, 51)), 49, 50))
    for where, keys, height, size in cases:
        tree = build(keys)
        got_h, got_s = tree.height(), tree.size()
        expect(got_h == height, f"{where}: height() = {got_h}, ожидалось {height}")
        expect(got_s == size, f"{where}: size() = {got_s}, ожидалось {size}")


def check_delete() -> None:
    tree = BST()
    tree.delete(1)
    got = tree.in_order()
    expect(got == [], f"delete(1) из пустого дерева: in_order() = {got}")

    keys = [5, 2, 8, 1, 3]
    tree = build(keys)
    left = set(keys)
    steps = [(1, "лист 1"), (2, "узел 2 с одним ребёнком"), (5, "корень 5 с двумя детьми"),
             (4, "отсутствующий ключ 4"), (3, "ключ 3"), (8, "последний ключ 8")]
    for k, what in steps:
        tree.delete(k)
        left.discard(k)
        where = f"дерево из вставок {keys}, удаление: {what}"
        got = tree.in_order()
        expect(got == sorted(left), f"{where}: in_order() = {got}, ожидалось {sorted(left)}")
        expect_search(tree, k, False, where)
        for rest in left:
            expect_search(tree, rest, True, where)
    got_h, got_s = tree.height(), tree.size()
    expect(got_h == -1 and got_s == 0, f"после удаления всех ключей: height() = {got_h}, size() = {got_s}")


def check_delete_two_children() -> None:
    for keys, k, by_successor, by_predecessor in TWO_CHILDREN_CASES:
        tree = build(keys)
        tree.delete(k)
        got = tree.pre_order()
        expect(got in (by_successor, by_predecessor),
               f"удаление {k} из {keys}: pre_order() = {got}, ожидалось {by_successor} или {by_predecessor}")


def check_against_reference() -> None:
    rng = random.Random(0)
    for run in range(1, 101):
        tree = BST()
        etalon: set[int] = set()
        for step in range(1, rng.randint(1, 80) + 1):
            k = rng.randint(-30, 30)
            if rng.random() < 0.6:
                tree.insert(k)
                etalon.add(k)
                op = f"insert({k})"
            else:
                tree.delete(k)
                etalon.discard(k)
                op = f"delete({k})"
            got = tree.in_order()
            expect(got == sorted(etalon), f"прогон {run}, команда №{step} {op}: in_order() = {got}, эталон {sorted(etalon)}")
        where = f"прогон {run}, итоговое дерево"
        for k in range(-30, 31):
            expect_search(tree, k, k in etalon, where)
        n = len(etalon)
        got = tree.size()
        expect(got == n, f"{where}: size() = {got}, эталон {n}")
        for name in TRAVERSALS[1:]:
            got = getattr(tree, name)()
            expect(sorted(got) == sorted(etalon), f"{where}: {name}() содержит не те ключи: {got}")
        got = tree.height()
        low, high = (-1, -1) if n == 0 else (n.bit_length() - 1, n - 1)
        expect(low <= got <= high, f"{where}: height() = {got} при {n} узлах, возможно от {low} до {high}")


def self_check() -> None:
    checks = (
        ("вставка и поиск", check_insert_search),
        ("обходы", check_traversals),
        ("высота и размер", check_height_size),
        ("удаление", check_delete),
        ("удаление узла с двумя детьми", check_delete_two_children),
        ("сверка с эталоном set/sorted", check_against_reference),
    )
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк
# ---------------------------------------------------------------------------
SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
QUERIES = 1_000


def bench(fn) -> float:
    """Медиана времени выполнения fn() по REPEATS запускам, с прогревом."""
    fn()
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    print(f"{'n':>8} {'h(BST)':>7} {'t_bst, c':>10} {'t_list, c':>10}")
    for n in SIZES:
        keys = rng.sample(range(10 * n), n)
        queries = [rng.randint(0, 10 * n) for _ in range(QUERIES)]
        tree = BST()
        for k in keys:
            tree.insert(k)

        def search_bst() -> None:
            for q in queries:
                tree.search(q)

        def search_list() -> None:
            for q in queries:
                q in keys

        print(f"{n:>8} {tree.height():>7} {bench(search_bst):>10.6f} {bench(search_list):>10.6f}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed)


if __name__ == "__main__":
    main()