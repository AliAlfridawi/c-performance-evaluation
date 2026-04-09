#ifndef ALGORITHMS_H
#define ALGORITHMS_H

#include <stddef.h>
#include <stdint.h>

/*
 * Comparison metric (match Python/Java): one increment per scalar comparison
 * between two values that drives the algorithm (partition loop, search).
 */

void algorithms_reset_comparison_count(void);
uint64_t algorithms_get_comparison_count(void);

void quick_sort(int *arr, size_t n);

/* Returns index or (size_t)-1 cast to int as -1; use return value < 0 for miss. */
int linear_search(const int *arr, size_t n, int target);

/* Precondition: arr sorted ascending. Returns index or -1. */
int binary_search(const int *arr, size_t n, int target);

#endif
