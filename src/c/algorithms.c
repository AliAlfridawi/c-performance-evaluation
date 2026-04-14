#include "algorithms.h"

static uint64_t g_comparisons;

void algorithms_reset_comparison_count(void) { g_comparisons = 0; }

uint64_t algorithms_get_comparison_count(void) { return g_comparisons; }

static void inc(void) { g_comparisons++; }

static void quick_sort_range(int *arr, ptrdiff_t low, ptrdiff_t high);

void quick_sort(int *arr, size_t n) {
    if (n == 0) {
        return;
    }
    quick_sort_range(arr, 0, (ptrdiff_t)n - 1);
}

static ptrdiff_t partition(int *arr, ptrdiff_t low, ptrdiff_t high) {
    ptrdiff_t mid = low + (high - low) / 2;

    /* Median of Three (low, mid, high) */
    inc();
    if (arr[mid] < arr[low]) {
        int t = arr[mid];
        arr[mid] = arr[low];
        arr[low] = t;
    }
    inc();
    if (arr[high] < arr[low]) {
        int t = arr[high];
        arr[high] = arr[low];
        arr[low] = t;
    }
    inc();
    if (arr[high] < arr[mid]) {
        int t = arr[high];
        arr[high] = arr[mid];
        arr[mid] = t;
    }

    /* Move median (mid) to high as the Lomuto pivot */
    int t = arr[mid];
    arr[mid] = arr[high];
    arr[high] = t;

    int pivot = arr[high];
    ptrdiff_t i = low - 1;
    for (ptrdiff_t j = low; j < high; j++) {
        inc();
        if (arr[j] <= pivot) {
            i++;
            int temp = arr[i];
            arr[i] = arr[j];
            arr[j] = temp;
        }
    }
    int temp = arr[i + 1];
    arr[i + 1] = arr[high];
    arr[high] = temp;
    return i + 1;
}

static void quick_sort_range(int *arr, ptrdiff_t low, ptrdiff_t high) {
    if (low >= high) {
        return;
    }
    ptrdiff_t p = partition(arr, low, high);
    quick_sort_range(arr, low, p - 1);
    quick_sort_range(arr, p + 1, high);
}

int linear_search(const int *arr, size_t n, int target) {
    for (size_t i = 0; i < n; i++) {
        inc();
        if (arr[i] == target) {
            return (int)i;
        }
    }
    return -1;
}

int binary_search(const int *arr, size_t n, int target) {
    if (n == 0) {
        return -1;
    }
    ptrdiff_t lo = 0;
    ptrdiff_t hi = (ptrdiff_t)n - 1;
    while (lo <= hi) {
        ptrdiff_t mid = lo + (hi - lo) / 2;
        inc();
        if (arr[mid] == target) {
            return (int)mid;
        }
        inc();
        if (arr[mid] < target) {
            lo = mid + 1;
        } else {
            hi = mid - 1;
        }
    }
    return -1;
}
