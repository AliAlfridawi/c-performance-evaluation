"""
Benchmark algorithms with a hardware-independent comparison counter.

Contract (match C/Java): increment once per scalar comparison between two values
(array elements or search target) used to drive the algorithm (partition, search).
"""

from __future__ import annotations

from typing import MutableSequence, Sequence

_comparison_count: int = 0


def reset_comparison_count() -> None:
    global _comparison_count
    _comparison_count = 0


def get_comparison_count() -> int:
    return _comparison_count


def _inc() -> None:
    global _comparison_count
    _comparison_count += 1


def quick_sort(arr: MutableSequence[int]) -> None:
    """In-place ascending quicksort (Lomuto partition, pivot = last element)."""
    _quick_sort_range(arr, 0, len(arr) - 1)


def _quick_sort_range(arr: MutableSequence[int], low: int, high: int) -> None:
    if low >= high:
        return
    pivot_idx = _partition(arr, low, high)
    _quick_sort_range(arr, low, pivot_idx - 1)
    _quick_sort_range(arr, pivot_idx + 1, high)


def _partition(arr: MutableSequence[int], low: int, high: int) -> int:
    mid = low + (high - low) // 2

    # Median of Three (low, mid, high)
    _inc()
    if arr[mid] < arr[low]:
        arr[mid], arr[low] = arr[low], arr[mid]
    _inc()
    if arr[high] < arr[low]:
        arr[high], arr[low] = arr[low], arr[high]
    _inc()
    if arr[high] < arr[mid]:
        arr[high], arr[mid] = arr[mid], arr[high]

    # Move median (mid) to high as the Lomuto pivot
    arr[mid], arr[high] = arr[high], arr[mid]

    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        _inc()
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def linear_search(arr: Sequence[int], target: int) -> int:
    """Return first index with value target, or -1."""
    for i in range(len(arr)):
        _inc()
        if arr[i] == target:
            return i
    return -1


def binary_search(arr: Sequence[int], target: int) -> int:
    """Binary search on ascending-sorted arr. Returns index or -1. Empty arr -> -1."""
    lo = 0
    hi = len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        _inc()
        if arr[mid] == target:
            return mid
        _inc()
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
