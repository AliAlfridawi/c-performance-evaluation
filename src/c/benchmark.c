/*
 * Wall time: clock() (CLOCKS_PER_SEC). Comparisons: algorithms_get_comparison_count().
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "algorithms.h"

static int int_cmp(const void *a, const void *b) {
    int x = *(const int *)a;
    int y = *(const int *)b;
    return (x > y) - (x < y);
}

static void build_array(int *a, size_t n, const char *dist, unsigned seed) {
    if (strcmp(dist, "ascending") == 0) {
        for (size_t i = 0; i < n; i++) {
            a[i] = (int)i;
        }
        return;
    }
    if (strcmp(dist, "descending") == 0) {
        for (size_t i = 0; i < n; i++) {
            a[i] = (int)(n - 1 - i);
        }
        return;
    }
    /* random */
    srand(seed);
    for (size_t i = 0; i < n; i++) {
        a[i] = 1 + (rand() % 1000);
    }
}

static int compare_str(const char *a, const char *b) { return strcmp(a, b) == 0; }

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr, "usage: %s <quicksort|linear_search|binary_search> "
                        "<random|ascending|descending> <N> [--seed N]\n",
                argv[0]);
        return 2;
    }
    const char *algo = argv[1];
    const char *dist = argv[2];
    size_t n = (size_t)strtoul(argv[3], NULL, 10);
    unsigned seed = 42;
    for (int i = 4; i + 1 < argc; i++) {
        if (strcmp(argv[i], "--seed") == 0) {
            seed = (unsigned)strtoul(argv[i + 1], NULL, 10);
            break;
        }
    }

    int *arr = NULL;
    if (n > 0) {
        arr = (int *)malloc(n * sizeof(int));
        if (!arr) {
            return 1;
        }
        build_array(arr, n, dist, seed);
    }

    if (compare_str(algo, "quicksort")) {
        algorithms_reset_comparison_count();
        clock_t t0 = clock();
        quick_sort(arr, n);
        clock_t t1 = clock();
        double sec = (double)(t1 - t0) / (double)CLOCKS_PER_SEC;
        uint64_t cmp = algorithms_get_comparison_count();
        printf("c,%s,%s,%zu,%llu,%.9f\n", algo, dist, n, (unsigned long long)cmp, sec);
        free(arr);
        return 0;
    }
    if (compare_str(algo, "linear_search")) {
        int target = (n > 0) ? arr[0] : 0;
        algorithms_reset_comparison_count();
        clock_t t0 = clock();
        linear_search(arr, n, target);
        clock_t t1 = clock();
        double sec = (double)(t1 - t0) / (double)CLOCKS_PER_SEC;
        uint64_t cmp = algorithms_get_comparison_count();
        printf("c,%s,%s,%zu,%llu,%.9f\n", algo, dist, n, (unsigned long long)cmp, sec);
        free(arr);
        return 0;
    }
    if (compare_str(algo, "binary_search")) {
        if (n > 0) {
            qsort(arr, n, sizeof(int), int_cmp);
        }
        int target = (n > 0) ? arr[n / 2] : 0;
        algorithms_reset_comparison_count();
        clock_t t0 = clock();
        binary_search(arr, n, target);
        clock_t t1 = clock();
        double sec = (double)(t1 - t0) / (double)CLOCKS_PER_SEC;
        uint64_t cmp = algorithms_get_comparison_count();
        printf("c,%s,%s,%zu,%llu,%.9f\n", algo, dist, n, (unsigned long long)cmp, sec);
        free(arr);
        return 0;
    }
    fprintf(stderr, "unknown algorithm\n");
    free(arr);
    return 2;
}
