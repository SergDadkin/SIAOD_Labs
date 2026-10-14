import sys
import time
import collections

# Инициализируем matplotlib для построения графиков
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# =====================================================================
# ЗАДАНИЕ 2: РЕКУРСИВНЫЕ ФУНКЦИИ
# =====================================================================

class RecursionMetrics:
    """Класс для подсчета метрик рекурсивных вызовов."""
    def __init__(self):
        self.factorial_calls = 0
        self.fib_naive_calls = 0
        self.fib_memo_calls = 0
        self.hanoi_moves = []

metrics = RecursionMetrics()


def recursive_factorial(n: int) -> int:
    """Вычисление факториала с подсчетом вызовов."""
    metrics.factorial_calls += 1
    if n < 0:
        raise ValueError("Факториал определен только для неотрицательных чисел")
    if n == 0 or n == 1:
        return 1
    return n * recursive_factorial(n - 1)


def fibonacci_naive(n: int) -> int:
    """Наивное вычисление чисел Фибоначчи O(2^n)."""
    metrics.fib_naive_calls += 1
    if n < 0:
        raise ValueError("Индекс Фибоначчи должен быть >= 0")
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci_naive(n - 1) + fibonacci_naive(n - 2)


def fibonacci_memo(n: int, memo: dict = None) -> int:
    """Оптимизированное вычисление Фибоначчи с мемоизацией O(n)."""
    metrics.fib_memo_calls += 1
    if memo is None:
        memo = {}
    if n < 0:
        raise ValueError("Индекс Фибоначчи должен быть >= 0")
    if n == 0:
        return 0
    if n == 1:
        return 1
    if n in memo:
        return memo[n]
    
    memo[n] = fibonacci_memo(n - 1, memo) + fibonacci_memo(n - 2, memo)
    return memo[n]


def hanoi(n: int, from_peg: str, to_peg: str, aux_peg: str, pegs_state: dict):
    """
    Ханойские башни с записью ходов и валидацией правил игры.
    pegs_state: словарь вида {'A':, 'B': [], 'C': []} для верификации.
    """
    if n == 0:
        return
    
    # 1. Переместить n-1 диск на вспомогательный шпиль
    hanoi(n - 1, from_peg, aux_peg, to_peg, pegs_state)
    
    # 2. Переместить диск на целевой шпиль и проверить инвариант
    if not pegs_state[from_peg]:
        raise RuntimeError(f"Ошибка: Попытка взять диск с пустого шпиля {from_peg}")
    
    disk = pegs_state[from_peg].pop()
    
    # Нельзя класть больший диск на меньший
    if pegs_state[to_peg] and pegs_state[to_peg][-1] < disk:
        raise RuntimeError(f"Нарушение правил: Диск {disk} кладется поверх меньшего {pegs_state[to_peg][-1]}")
    
    pegs_state[to_peg].append(disk)
    metrics.hanoi_moves.append((disk, from_peg, to_peg))
    
    # 3. Переместить n-1 диск со вспомогательного на целевой шпиль
    hanoi(n - 1, aux_peg, to_peg, from_peg, pegs_state)


# =====================================================================
# ЗАДАНИЕ 3: ДИНАМИЧЕСКИЙ МАССИВ С УЧЕТОМ КОПИРОВАНИЙ
# =====================================================================

class DynamicArray:
    """
    Динамический массив с ручным управлением емкостью (рост *2, сжатие при 1/4).
    Инвариант: size <= capacity.
    """
    def __init__(self, initial_capacity: int = 1):
        self.capacity = initial_capacity
        self.size = 0
        self.buffer = [None] * self.capacity
        self.copies = 0  # Счётчик копирований элементов для отчёта

    def __len__(self) -> int:
        return self.size

    def _resize(self, new_capacity: int):
        """Изменение размера внутреннего буфера и копирование элементов."""
        new_buffer = [None] * new_capacity
        for i in range(self.size):
            new_buffer[i] = self.buffer[i]
            self.copies += 1  # Считаем каждое копирование
        self.buffer = new_buffer
        self.capacity = new_capacity

    def append(self, value) -> None:
        """Добавление элемента в конец массива."""
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        
        self.buffer[self.size] = value
        self.size += 1

    def pop(self):
        """Удаление последнего элемента с возможным сжатием буфера."""
        if self.size == 0:
            raise IndexError("pop от пустого массива")
        
        self.size -= 1
        value = self.buffer[self.size]
        self.buffer[self.size] = None  # Очищаем ячейку
        
        # Сжатие буфера вдвое, если заполнено менее 1/4 емкости
        if 0 < self.size <= self.capacity // 4 and self.capacity > 1:
            self._resize(self.capacity // 2)
            
        return value

    def __getitem__(self, index: int):
        if not (0 <= index < self.size):
            raise IndexError("Индекс вне диапазона массива")
        return self.buffer[index]

    def __setitem__(self, index: int, value):
        if not (0 <= index < self.size):
            raise IndexError("Индекс вне диапазона массива")
        self.buffer[index] = value


# =====================================================================
# ЗАДАНИЕ 4: СТЕК И ДЕК (СТРУКТУРЫ "С НУЛЯ")
# =====================================================================

class Stack:
    """Стек (LIFO) на базе DynamicArray через его публичный интерфейс."""
    def __init__(self):
        self._array = DynamicArray()

    def __len__(self) -> int:
        return len(self._array)

    def is_empty(self) -> bool:
        return len(self._array) == 0

    def push(self, value) -> None:
        self._array.append(value)

    def pop(self):
        if self.is_empty():
            raise IndexError("Попытка извлечь элемент из пустого стека")
        return self._array.pop()


class Node:
    """Узел двусвязного списка для Дека."""
    def __init__(self, value):
        self.value = value
        self.prev = None
        self.next = None


class Deque:
    """Дек (FIFO/LIFO) на базе двусвязного списка."""
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def __len__(self) -> int:
        return self.size

    def is_empty(self) -> bool:
        return self.size == 0

    def push_back(self, value) -> None:
        """Вставка в конец O(1)."""
        new_node = Node(value)
        if self.is_empty():
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def push_front(self, value) -> None:
        """Вставка в начало O(1)."""
        new_node = Node(value)
        if self.is_empty():
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.size += 1

    def pop_back(self):
        """Удаление с конца O(1)."""
        if self.is_empty():
            raise IndexError("Дек пуст")
        value = self.tail.value
        if self.size == 1:
            self.head = self.tail = None
        else:
            self.tail = self.tail.prev
            self.tail.next = None
        self.size -= 1
        return value

    def pop_front(self):
        """Удаление с начала O(1)."""
        if self.is_empty():
            raise IndexError("Дек пуст")
        value = self.head.value
        if self.size == 1:
            self.head = self.tail = None
        else:
            self.head = self.head.next
            self.head.prev = None
        self.size -= 1
        return value


# =====================================================================
# ЗАДАНИЕ 6: SELF_CHECK И ТЕСТЫ ВЕРИФИКАЦИИ
# =====================================================================

def run_self_checks():
    print("--- Запуск верификационных тестов (Self-Check) ---")
    
    # 1. Тестирование DynamicArray
    da = DynamicArray(initial_capacity=2)
    da.append(10)
    da.append(20)
    if da.capacity != 2: 
        raise ValueError("Неверная начальная емкость")
    da.append(30)  # Емкость растет до 4
    if da.capacity != 4: 
        raise ValueError("Емкость должна была удвоиться")
    if da.copies != 2: 
        raise ValueError("Неверное количество копирований")
    
    # Тест сжатия массива
    da.pop()
    da.pop()  # Остался 1 элемент при емкости 4 (заполнено на 1/4) -> сжатие до 2
    if da.capacity != 2: 
        raise ValueError("Массив не сжался при заполнении <= 1/4")
    print("[OK] DynamicArray успешно прошел тесты.")

    # 2. Тестирование Stack
    st = Stack()
    st.push(1)
    st.push(2)
    if st.pop() != 2 or st.pop() != 1: 
        raise ValueError("Нарушен принцип LIFO в Stack")
    print("[OK] Stack успешно прошел тесты.")

    # 3. Тестирование Deque
    dq = Deque()
    dq.push_back(10)
    dq.push_front(5)
    dq.push_back(15)
    if dq.pop_front() != 5 or dq.pop_back() != 15 or dq.pop_front() != 10: 
        raise ValueError("Ошибка в логике Deque")
    print("[OK] Deque успешно прошел тесты.")
    
    # 4. Тестирование Ханойских башен
    n_disks = 3
    initial_pegs = {'A': list(range(n_disks, 0, -1)), 'B': [], 'C': []}
    metrics.hanoi_moves.clear()
    hanoi(n_disks, 'A', 'C', 'B', initial_pegs)
    
    expected_moves = 2**n_disks - 1
    if len(metrics.hanoi_moves) != expected_moves:
        raise ValueError("Количество ходов не соответствует формуле 2^n - 1")
    if initial_pegs['C'] != [3, 2, 1] or initial_pegs['A'] or initial_pegs['B']:
        raise ValueError("Диски перенесены на целевой шпиль некорректно")
    print(f"[OK] Ханойские башни успешны. Шагов: {len(metrics.hanoi_moves)}.")



# =====================================================================
# ЗАДАНИЕ 5: ЭКСПЕРИМЕНТЫ И СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ
# =====================================================================

def run_benchmarks():
    print("\n--- Запуск бенчмарков производительности ---")
    sizes = [1000, 5000, 10000, 20000]
    
    list_times = []
    coll_deque_times = []
    my_deque_times = []
    
    print(f"{'Размер (N)':<12}{'list.insert(0)':<18}{'dq.appendleft':<18}{'MyDeque.front':<18}")
    
    for n in sizes:
        # 1. Встроенный список Python (O(N) на одну вставку, суммарно O(N^2))
        t0 = time.perf_counter()
        lst = []
        for i in range(n):
            lst.insert(0, i)
        t_list_ins = time.perf_counter() - t0
        list_times.append(t_list_ins)
        
        # 2. collections.deque (O(1) на одну вставку, суммарно O(N))
        t0 = time.perf_counter()
        coll_dq = collections.deque()
        for i in range(n):
            coll_dq.appendleft(i)
        t_coll_ins = time.perf_counter() - t0
        coll_deque_times.append(t_coll_ins)
        
        # 3. Наш Deque на двусвязном списке (O(1) на одну вставку, суммарно O(N))
        t0 = time.perf_counter()
        my_dq = Deque()
        for i in range(n):
            my_dq.push_front(i)
        t_my_ins = time.perf_counter() - t0
        my_deque_times.append(t_my_ins)
        
        print(f"{n:<12}{t_list_ins:.5f}s          {t_coll_ins:.5f}s          {t_my_ins:.5f}s")
        
    # Визуализация результатов для отчета
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 6))
        plt.plot(sizes, list_times, label='Встроенный list (insert в начало)', marker='o', color='red')
        plt.plot(sizes, coll_deque_times, label='collections.deque (appendleft)', marker='s', color='green')
        plt.plot(sizes, my_deque_times, label='Наш Deque (push_front)', marker='^', color='blue')
        plt.xlabel('Количество элементов (N)')
        plt.ylabel('Время выполнения (секунды)')
        plt.title('Сравнение времени вставки элементов в начало структуры')
        plt.legend()
        plt.grid(True)
        plt.savefig('deque_benchmark_results.png')
        print("\n[INFO] График бенчмарка сохранен в файл 'deque_benchmark_results.png'")
        plt.show()
    except ImportError:
        print("\n[INFO] Установите matplotlib (`pip install matplotlib`) для автоматического построения графиков.")

if __name__ == "__main__":
    run_self_checks()
    run_benchmarks()