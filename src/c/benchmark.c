/*
 * Emit raw benchmark trial rows as CSV.
 */

#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#else
#include <time.h>
#endif

#include "algorithms.h"

#define MIN_BATCH_TIME_NS 50000000ULL

typedef struct {
    const char *algorithm;
    const char *distribution;
    size_t n;
    unsigned seed;
    const char *input_file;
    int trials;
    int warmup;
    const char *search_case;
    const char *input_id;
    int *base_arr;
} BenchConfig;

static uint64_t get_time_ns(void) {
#ifdef _WIN32
    static LARGE_INTEGER freq = {0};
    LARGE_INTEGER counter;
    if (freq.QuadPart == 0 && !QueryPerformanceFrequency(&freq)) {
        return 0;
    }
    if (!QueryPerformanceCounter(&counter)) {
        return 0;
    }
    return (uint64_t)((counter.QuadPart * 1000000000LL) / freq.QuadPart);
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
#endif
}

static int compare_str(const char *a, const char *b) {
    return strcmp(a, b) == 0;
}

static int int_cmp(const void *a, const void *b) {
    int x = *(const int *)a;
    int y = *(const int *)b;
    return (x > y) - (x < y);
}

static void build_array(int *a, size_t n, const char *dist, unsigned seed) {
    if (compare_str(dist, "ascending")) {
        for (size_t i = 0; i < n; i++) {
            a[i] = (int)i;
        }
        return;
    }
    if (compare_str(dist, "descending")) {
        for (size_t i = 0; i < n; i++) {
            a[i] = (int)(n - 1 - i);
        }
        return;
    }

    for (size_t i = 0; i < n; i++) {
        a[i] = (int)i;
    }
    srand(seed);
    for (size_t i = n; i > 1; i--) {
        size_t j = (size_t)(rand() % (int)i);
        int temp = a[i - 1];
        a[i - 1] = a[j];
        a[j] = temp;
    }
}

static int *load_array_from_file(const char *path, size_t *out_n) {
    FILE *fp = fopen(path, "r");
    int *arr = NULL;
    size_t n = 0;
    size_t cap = 0;
    int value;
    int rc;

    if (!fp) {
        *out_n = (size_t)-1;
        fprintf(stderr, "error: could not open input file: %s\n", path);
        return NULL;
    }

    while ((rc = fscanf(fp, "%d", &value)) == 1) {
        if (n == cap) {
            size_t next_cap = cap == 0 ? 64 : cap * 2;
            int *next = (int *)realloc(arr, next_cap * sizeof(int));
            if (!next) {
                fclose(fp);
                free(arr);
                *out_n = (size_t)-1;
                fprintf(stderr, "error: memory allocation failed\n");
                return NULL;
            }
            arr = next;
            cap = next_cap;
        }
        arr[n++] = value;
    }

    if (rc != EOF) {
        fclose(fp);
        free(arr);
        *out_n = (size_t)-1;
        fprintf(stderr, "error: invalid token in input file: %s\n", path);
        return NULL;
    }

    fclose(fp);
    *out_n = n;
    return arr;
}

static void derive_input_id(const char *input_file, const char *distribution, size_t n, char *buf, size_t buf_size) {
    if (!input_file || input_file[0] == '\0') {
        snprintf(buf, buf_size, "%s_n%zu", distribution, n);
        return;
    }

    const char *name = input_file;
    const char *slash = strrchr(input_file, '/');
    const char *backslash = strrchr(input_file, '\\');
    const char *cut = slash;
    if (!cut || (backslash && backslash > cut)) {
        cut = backslash;
    }
    if (cut) {
        name = cut + 1;
    }

    strncpy(buf, name, buf_size - 1);
    buf[buf_size - 1] = '\0';
    char *dot = strrchr(buf, '.');
    if (dot) {
        *dot = '\0';
    }
}

static int parse_non_negative_int(const char *value, const char *label, int *out) {
    char *end = NULL;
    long parsed = strtol(value, &end, 10);
    if (!end || *end != '\0' || parsed < 0 || parsed > INT_MAX) {
        fprintf(stderr, "error: invalid %s: %s\n", label, value);
        return 0;
    }
    *out = (int)parsed;
    return 1;
}

static int parse_config(int argc, char **argv, BenchConfig *cfg) {
    if (argc < 4) {
        fprintf(stderr, "usage: %s <quicksort|linear_search|binary_search> "
                        "<random|ascending|descending> <N> [--seed N] [--input-file PATH] "
                        "[--trials N] [--warmup N] [--search-case CASE]\n",
                argv[0]);
        return 0;
    }

    memset(cfg, 0, sizeof(*cfg));
    cfg->algorithm = argv[1];
    cfg->distribution = argv[2];
    int temp_n = 0;
    if (!parse_non_negative_int(argv[3], "N", &temp_n)) {
        return 0;
    }
    cfg->n = (size_t)temp_n;
    cfg->seed = 42U;
    cfg->trials = 1;
    cfg->warmup = 0;
    cfg->search_case = NULL;

    if (!compare_str(cfg->algorithm, "quicksort")
            && !compare_str(cfg->algorithm, "linear_search")
            && !compare_str(cfg->algorithm, "binary_search")) {
        fprintf(stderr, "error: unknown algorithm\n");
        return 0;
    }
    if (!compare_str(cfg->distribution, "random")
            && !compare_str(cfg->distribution, "ascending")
            && !compare_str(cfg->distribution, "descending")) {
        fprintf(stderr, "error: unknown distribution\n");
        return 0;
    }

    for (int i = 4; i < argc; i++) {
        if (compare_str(argv[i], "--seed") && i + 1 < argc) {
            cfg->seed = (unsigned)strtoul(argv[++i], NULL, 10);
        } else if (compare_str(argv[i], "--input-file") && i + 1 < argc) {
            cfg->input_file = argv[++i];
        } else if (compare_str(argv[i], "--trials") && i + 1 < argc) {
            if (!parse_non_negative_int(argv[++i], "trials", &cfg->trials) || cfg->trials <= 0) {
                fprintf(stderr, "error: trials must be positive\n");
                return 0;
            }
        } else if (compare_str(argv[i], "--warmup") && i + 1 < argc) {
            if (!parse_non_negative_int(argv[++i], "warmup", &cfg->warmup)) {
                return 0;
            }
        } else if (compare_str(argv[i], "--search-case") && i + 1 < argc) {
            cfg->search_case = argv[++i];
        } else {
            fprintf(stderr, "error: unknown option: %s\n", argv[i]);
            return 0;
        }
    }

    if (!cfg->search_case) {
        if (compare_str(cfg->algorithm, "quicksort")) {
            cfg->search_case = "sort";
        } else if (compare_str(cfg->algorithm, "linear_search")) {
            cfg->search_case = "first_hit";
        } else {
            cfg->search_case = "middle_hit";
        }
    }

    if (compare_str(cfg->algorithm, "quicksort") && !compare_str(cfg->search_case, "sort")) {
        fprintf(stderr, "error: quicksort only supports --search-case sort\n");
        return 0;
    }
    if (!compare_str(cfg->algorithm, "quicksort")) {
        if (compare_str(cfg->search_case, "sort")) {
            fprintf(stderr, "error: search algorithms require a hit/miss search case\n");
            return 0;
        }
        if (!compare_str(cfg->search_case, "first_hit") &&
            !compare_str(cfg->search_case, "middle_hit") &&
            !compare_str(cfg->search_case, "last_hit") &&
            !compare_str(cfg->search_case, "miss")) {
            fprintf(stderr, "error: unsupported search case: %s\n", cfg->search_case);
            return 0;
        }
    }

    return 1;
}

static int max_value(const int *arr, size_t n) {
    int max_v = 0;
    for (size_t i = 0; i < n; i++) {
        if (i == 0 || arr[i] > max_v) {
            max_v = arr[i];
        }
    }
    return max_v;
}

static int select_target(const int *arr, size_t n, const char *search_case) {
    if (n == 0) {
        return 0;
    }
    if (compare_str(search_case, "first_hit")) {
        return arr[0];
    }
    if (compare_str(search_case, "middle_hit")) {
        return arr[n / 2];
    }
    if (compare_str(search_case, "last_hit")) {
        return arr[n - 1];
    }
    if (compare_str(search_case, "miss")) {
        return max_value(arr, n) + 1;
    }
    fprintf(stderr, "error: unsupported search case: %s\n", search_case);
    return 0;
}

static void run_quicksort_trial(const int *base_arr, size_t n, uint64_t *comparisons, uint64_t *elapsed_ns, int *batch_loops) {
    int *work = NULL;
    if (n > 0) {
        work = (int *)malloc(n * sizeof(int));
        if (!work) {
            fprintf(stderr, "error: memory allocation failed\n");
            exit(1);
        }
    }

    *comparisons = 0;
    *elapsed_ns = 0;
    *batch_loops = 0;
    while (*batch_loops == 0 || *elapsed_ns < MIN_BATCH_TIME_NS) {
        if (n > 0) {
            memcpy(work, base_arr, n * sizeof(int));
        }
        algorithms_reset_comparison_count();
        uint64_t t0 = get_time_ns();
        quick_sort(work, n);
        uint64_t t1 = get_time_ns();
        *comparisons = algorithms_get_comparison_count();
        *elapsed_ns += (t1 - t0);
        (*batch_loops)++;
    }

    free(work);
}

static void run_linear_search_trial(const int *base_arr, size_t n, int target, uint64_t *comparisons, uint64_t *elapsed_ns, int *batch_loops) {
    *comparisons = 0;
    *elapsed_ns = 0;
    *batch_loops = 0;
    while (*batch_loops == 0 || *elapsed_ns < MIN_BATCH_TIME_NS) {
        algorithms_reset_comparison_count();
        uint64_t t0 = get_time_ns();
        linear_search(base_arr, n, target);
        uint64_t t1 = get_time_ns();
        *comparisons = algorithms_get_comparison_count();
        *elapsed_ns += (t1 - t0);
        (*batch_loops)++;
    }
}

static void run_binary_search_trial(const int *sorted_arr, size_t n, int target, uint64_t *comparisons, uint64_t *elapsed_ns, int *batch_loops) {
    *comparisons = 0;
    *elapsed_ns = 0;
    *batch_loops = 0;
    while (*batch_loops == 0 || *elapsed_ns < MIN_BATCH_TIME_NS) {
        algorithms_reset_comparison_count();
        uint64_t t0 = get_time_ns();
        binary_search(sorted_arr, n, target);
        uint64_t t1 = get_time_ns();
        *comparisons = algorithms_get_comparison_count();
        *elapsed_ns += (t1 - t0);
        (*batch_loops)++;
    }
}

int main(int argc, char **argv) {
    BenchConfig cfg;
    char input_id_buf[128];
    size_t loaded_n = 0;

    if (!parse_config(argc, argv, &cfg)) {
        return 2;
    }

    if (cfg.input_file) {
        cfg.base_arr = load_array_from_file(cfg.input_file, &loaded_n);
        if (!cfg.base_arr && loaded_n == (size_t)-1) {
            return 1;
        }
        if (loaded_n != cfg.n) {
            fprintf(stderr, "error: N mismatch: expected %zu, input file contains %zu values\n", cfg.n, loaded_n);
            free(cfg.base_arr);
            return 2;
        }
    } else if (cfg.n > 0) {
        cfg.base_arr = (int *)malloc(cfg.n * sizeof(int));
        if (!cfg.base_arr) {
            fprintf(stderr, "error: memory allocation failed\n");
            return 1;
        }
        build_array(cfg.base_arr, cfg.n, cfg.distribution, cfg.seed);
    }

    derive_input_id(cfg.input_file, cfg.distribution, cfg.n, input_id_buf, sizeof(input_id_buf));
    cfg.input_id = input_id_buf;

    int *sorted_arr = NULL;
    int target = 0;
    if (compare_str(cfg.algorithm, "binary_search") && cfg.n > 0) {
        sorted_arr = (int *)malloc(cfg.n * sizeof(int));
        if (!sorted_arr) {
            fprintf(stderr, "error: memory allocation failed\n");
            free(cfg.base_arr);
            return 1;
        }
        memcpy(sorted_arr, cfg.base_arr, cfg.n * sizeof(int));
        qsort(sorted_arr, cfg.n, sizeof(int), int_cmp);
        target = select_target(sorted_arr, cfg.n, cfg.search_case);
    } else if (compare_str(cfg.algorithm, "linear_search")) {
        target = select_target(cfg.base_arr, cfg.n, cfg.search_case);
    }

    int total_rows = cfg.warmup + cfg.trials;
    for (int i = 0; i < total_rows; i++) {
        uint64_t comparisons = 0;
        uint64_t elapsed_ns = 0;
        int batch_loops = 0;
        int warmup = i < cfg.warmup ? 1 : 0;
        int trial_no = i + 1;

        if (compare_str(cfg.algorithm, "quicksort")) {
            run_quicksort_trial(cfg.base_arr, cfg.n, &comparisons, &elapsed_ns, &batch_loops);
        } else if (compare_str(cfg.algorithm, "linear_search")) {
            run_linear_search_trial(cfg.base_arr, cfg.n, target, &comparisons, &elapsed_ns, &batch_loops);
        } else if (compare_str(cfg.algorithm, "binary_search")) {
            run_binary_search_trial(sorted_arr, cfg.n, target, &comparisons, &elapsed_ns, &batch_loops);
        } else {
            fprintf(stderr, "error: unknown algorithm\n");
            free(sorted_arr);
            free(cfg.base_arr);
            return 2;
        }

        printf(
            "c,%s,%s,%s,%zu,%s,%d,%d,%llu,%llu,%d\n",
            cfg.algorithm,
            cfg.distribution,
            cfg.input_id,
            cfg.n,
            cfg.search_case,
            trial_no,
            warmup,
            (unsigned long long)comparisons,
            (unsigned long long)elapsed_ns,
            batch_loops
        );
    }

    free(sorted_arr);
    free(cfg.base_arr);
    return 0;
}
