"""Correctness tests for algorithms (small N, deterministic)."""

import copy
import unittest

from algorithms import (
    binary_search,
    get_comparison_count,
    linear_search,
    quick_sort,
    reset_comparison_count,
)


# Standalone regression cases (N=10)
REGRESSION_N10_RANDOM = [73, 21, 56, 89, 12, 45, 98, 34, 67, 4]
REGRESSION_N10_SORTED = [4, 12, 21, 34, 45, 56, 67, 73, 89, 98]


class TestQuickSort(unittest.TestCase):
    def test_empty(self) -> None:
        a: list[int] = []
        reset_comparison_count()
        quick_sort(a)
        self.assertEqual(a, [])
        self.assertEqual(get_comparison_count(), 0)

    def test_single(self) -> None:
        a = [42]
        quick_sort(a)
        self.assertEqual(a, [42])

    def test_sorted(self) -> None:
        a = [1, 2, 3, 4]
        quick_sort(a)
        self.assertEqual(a, [1, 2, 3, 4])

    def test_reverse(self) -> None:
        a = [4, 3, 2, 1]
        quick_sort(a)
        self.assertEqual(a, [1, 2, 3, 4])

    def test_regression_n10_random(self) -> None:
        a = copy.copy(REGRESSION_N10_RANDOM)
        quick_sort(a)
        self.assertEqual(a, REGRESSION_N10_SORTED)


class TestLinearSearch(unittest.TestCase):
    def test_present_first(self) -> None:
        self.assertEqual(linear_search([1, 2, 3], 1), 0)

    def test_present_last(self) -> None:
        self.assertEqual(linear_search([1, 2, 3], 3), 2)

    def test_absent(self) -> None:
        self.assertEqual(linear_search([1, 2, 3], 99), -1)

    def test_empty(self) -> None:
        self.assertEqual(linear_search([], 1), -1)


class TestBinarySearch(unittest.TestCase):
    def test_present(self) -> None:
        a = [1, 3, 5, 7, 9]
        self.assertEqual(binary_search(a, 5), 2)

    def test_absent(self) -> None:
        a = [1, 3, 5, 7, 9]
        self.assertEqual(binary_search(a, 4), -1)

    def test_empty(self) -> None:
        self.assertEqual(binary_search([], 1), -1)

    def test_single_hit(self) -> None:
        self.assertEqual(binary_search([42], 42), 0)

    def test_single_miss(self) -> None:
        self.assertEqual(binary_search([42], 1), -1)


if __name__ == "__main__":
    unittest.main()
