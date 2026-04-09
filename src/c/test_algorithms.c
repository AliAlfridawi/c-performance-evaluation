#include <assert.h>
#include <stdint.h>
#include <string.h>

#include "algorithms.h"

static void test_quicksort_empty(void) {
    algorithms_reset_comparison_count();
    quick_sort(NULL, 0);
    assert(algorithms_get_comparison_count() == 0);
}

static void test_quicksort_single(void) {
    int a[] = {42};
    quick_sort(a, 1);
    assert(a[0] == 42);
}

static void test_quicksort_reverse(void) {
    int a[] = {4, 3, 2, 1};
    quick_sort(a, 4);
    assert(a[0] == 1 && a[1] == 2 && a[2] == 3 && a[3] == 4);
}

static void test_quicksort_n10(void) {
    int a[] = {73, 21, 56, 89, 12, 45, 98, 34, 67, 4};
    int expect[] = {4, 12, 21, 34, 45, 56, 67, 73, 89, 98};
    quick_sort(a, 10);
    assert(memcmp(a, expect, sizeof(expect)) == 0);
}

static void test_linear(void) {
    int a[] = {1, 2, 3};
    assert(linear_search(a, 3, 1) == 0);
    assert(linear_search(a, 3, 3) == 2);
    assert(linear_search(a, 3, 99) == -1);
    assert(linear_search(NULL, 0, 1) == -1);
}

static void test_binary(void) {
    int a[] = {1, 3, 5, 7, 9};
    assert(binary_search(a, 5, 5) == 2);
    assert(binary_search(a, 5, 4) == -1);
    assert(binary_search(NULL, 0, 1) == -1);
    int one[] = {42};
    assert(binary_search(one, 1, 42) == 0);
    assert(binary_search(one, 1, 1) == -1);
}

int main(void) {
    test_quicksort_empty();
    test_quicksort_single();
    test_quicksort_reverse();
    test_quicksort_n10();
    test_linear();
    test_binary();
    return 0;
}
