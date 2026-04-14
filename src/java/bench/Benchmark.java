package bench;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Random;

/**
 * Emit raw benchmark trial rows as CSV.
 */
public final class Benchmark {

    private static final long MIN_BATCH_TIME_NS = 500_000L;

    private Benchmark() {}

    public static void main(String[] args) {
        Config config;
        int[] base;
        try {
            config = Config.parse(args);
            base = config.inputFile != null
                    ? loadArray(config.inputFile, config.n)
                    : buildArray(config.n, config.distribution, config.seed);
        } catch (IllegalArgumentException e) {
            System.err.println(e.getMessage());
            System.exit(2);
            return;
        } catch (IOException e) {
            System.err.println("error: " + e.getMessage());
            System.exit(1);
            return;
        }
        String inputId = deriveInputId(config.inputFile, config.distribution, config.n);
        int[] sorted = "binary_search".equals(config.algorithm) ? sortedCopy(base) : null;
        int target = 0;
        if ("linear_search".equals(config.algorithm)) {
            target = selectTarget(base, config.searchCase);
        } else if ("binary_search".equals(config.algorithm)) {
            target = selectTarget(sorted, config.searchCase);
        }

        int totalRows = config.warmup + config.trials;
        for (int i = 0; i < totalRows; i++) {
            TrialResult result;
            if ("quicksort".equals(config.algorithm)) {
                result = runQuickSortTrial(base);
            } else if ("linear_search".equals(config.algorithm)) {
                result = runLinearSearchTrial(base, target);
            } else if ("binary_search".equals(config.algorithm)) {
                result = runBinarySearchTrial(sorted, target);
            } else {
                throw new IllegalStateException("unknown algorithm: " + config.algorithm);
            }

            int warmup = i < config.warmup ? 1 : 0;
            int trialNo = i + 1;
            System.out.printf(
                    "java,%s,%s,%s,%d,%s,%d,%d,%d,%d,%d%n",
                    config.algorithm,
                    config.distribution,
                    inputId,
                    config.n,
                    config.searchCase,
                    trialNo,
                    warmup,
                    result.comparisons,
                    result.elapsedNs,
                    result.batchLoops);
        }
    }

    private static int[] buildArray(int n, String distribution, long seed) {
        if (n == 0) {
            return new int[0];
        }
        int[] a = new int[n];
        if ("ascending".equals(distribution)) {
            for (int i = 0; i < n; i++) {
                a[i] = i;
            }
            return a;
        }
        if ("descending".equals(distribution)) {
            for (int i = 0; i < n; i++) {
                a[i] = n - 1 - i;
            }
            return a;
        }
        for (int i = 0; i < n; i++) {
            a[i] = i;
        }
        Random rng = new Random(seed);
        for (int i = n - 1; i > 0; i--) {
            int j = rng.nextInt(i + 1);
            int temp = a[i];
            a[i] = a[j];
            a[j] = temp;
        }
        return a;
    }

    private static int[] loadArray(Path inputFile, int expectedN) throws IOException {
        if (!Files.isRegularFile(inputFile)) {
            throw new IllegalArgumentException("input file not found: " + inputFile);
        }
        String text = Files.readString(inputFile).trim();
        if (text.isEmpty()) {
            if (expectedN != 0) {
                throw new IllegalArgumentException(
                        "N mismatch: expected " + expectedN + ", input file contains 0 values");
            }
            return new int[0];
        }
        String[] tokens = text.split("\\s+");
        if (tokens.length != expectedN) {
            throw new IllegalArgumentException(
                    "N mismatch: expected " + expectedN + ", input file contains " + tokens.length + " values");
        }
        int[] arr = new int[tokens.length];
        for (int i = 0; i < tokens.length; i++) {
            arr[i] = Integer.parseInt(tokens[i]);
        }
        return arr;
    }

    private static String deriveInputId(Path inputFile, String distribution, int n) {
        if (inputFile == null) {
            return distribution + "_n" + n;
        }
        String name = inputFile.getFileName().toString();
        int dot = name.lastIndexOf('.');
        return dot >= 0 ? name.substring(0, dot) : name;
    }

    private static int[] sortedCopy(int[] arr) {
        int[] sorted = Arrays.copyOf(arr, arr.length);
        Arrays.sort(sorted);
        return sorted;
    }

    private static int selectTarget(int[] arr, String searchCase) {
        if (arr.length == 0) {
            return 0;
        }
        return switch (searchCase) {
            case "first_hit" -> arr[0];
            case "middle_hit" -> arr[arr.length / 2];
            case "last_hit" -> arr[arr.length - 1];
            case "miss" -> Arrays.stream(arr).max().orElse(0) + 1;
            default -> throw new IllegalArgumentException("unsupported search case: " + searchCase);
        };
    }

    private static TrialResult runQuickSortTrial(int[] base) {
        long elapsedNs = 0L;
        int comparisons = 0;
        int batchLoops = 0;

        while (batchLoops == 0 || elapsedNs < MIN_BATCH_TIME_NS) {
            int[] work = Arrays.copyOf(base, base.length);
            Algorithms.resetComparisonCount();
            long t0 = System.nanoTime();
            Algorithms.quickSort(work);
            long t1 = System.nanoTime();
            comparisons = (int) Algorithms.getComparisonCount();
            elapsedNs += t1 - t0;
            batchLoops++;
        }

        return new TrialResult(comparisons, elapsedNs, batchLoops);
    }

    private static TrialResult runLinearSearchTrial(int[] base, int target) {
        long elapsedNs = 0L;
        int comparisons = 0;
        int batchLoops = 0;

        while (batchLoops == 0 || elapsedNs < MIN_BATCH_TIME_NS) {
            Algorithms.resetComparisonCount();
            long t0 = System.nanoTime();
            Algorithms.linearSearch(base, target);
            long t1 = System.nanoTime();
            comparisons = (int) Algorithms.getComparisonCount();
            elapsedNs += t1 - t0;
            batchLoops++;
        }

        return new TrialResult(comparisons, elapsedNs, batchLoops);
    }

    private static TrialResult runBinarySearchTrial(int[] sorted, int target) {
        long elapsedNs = 0L;
        int comparisons = 0;
        int batchLoops = 0;

        while (batchLoops == 0 || elapsedNs < MIN_BATCH_TIME_NS) {
            Algorithms.resetComparisonCount();
            long t0 = System.nanoTime();
            Algorithms.binarySearch(sorted, target);
            long t1 = System.nanoTime();
            comparisons = (int) Algorithms.getComparisonCount();
            elapsedNs += t1 - t0;
            batchLoops++;
        }

        return new TrialResult(comparisons, elapsedNs, batchLoops);
    }

    private record TrialResult(int comparisons, long elapsedNs, int batchLoops) {}

    private static final class Config {
        private final String algorithm;
        private final String distribution;
        private final int n;
        private final long seed;
        private final Path inputFile;
        private final int trials;
        private final int warmup;
        private final String searchCase;

        private Config(
                String algorithm,
                String distribution,
                int n,
                long seed,
                Path inputFile,
                int trials,
                int warmup,
                String searchCase) {
            this.algorithm = algorithm;
            this.distribution = distribution;
            this.n = n;
            this.seed = seed;
            this.inputFile = inputFile;
            this.trials = trials;
            this.warmup = warmup;
            this.searchCase = searchCase;
        }

        private static Config parse(String[] args) {
            if (args.length < 3) {
                throw new IllegalArgumentException(
                        "usage: java bench.Benchmark <quicksort|linear_search|binary_search> "
                                + "<random|ascending|descending> <N> [--seed N] [--input-file PATH] "
                                + "[--trials N] [--warmup N] [--search-case CASE]");
            }

            String algorithm = args[0];
            String distribution = args[1];
            int n = Integer.parseInt(args[2]);
            long seed = 42L;
            Path inputFile = null;
            int trials = 1;
            int warmup = 0;
            String searchCase = null;

            for (int i = 3; i < args.length; i++) {
                if ("--seed".equals(args[i]) && i + 1 < args.length) {
                    seed = Long.parseLong(args[++i]);
                } else if ("--input-file".equals(args[i]) && i + 1 < args.length) {
                    inputFile = Path.of(args[++i]);
                } else if ("--trials".equals(args[i]) && i + 1 < args.length) {
                    trials = Integer.parseInt(args[++i]);
                } else if ("--warmup".equals(args[i]) && i + 1 < args.length) {
                    warmup = Integer.parseInt(args[++i]);
                } else if ("--search-case".equals(args[i]) && i + 1 < args.length) {
                    searchCase = args[++i];
                } else {
                    throw new IllegalArgumentException("error: unknown option: " + args[i]);
                }
            }

            if (n < 0) {
                throw new IllegalArgumentException("N must be non-negative");
            }
            if (!"quicksort".equals(algorithm)
                    && !"linear_search".equals(algorithm)
                    && !"binary_search".equals(algorithm)) {
                throw new IllegalArgumentException("error: unknown algorithm");
            }
            if (!"random".equals(distribution)
                    && !"ascending".equals(distribution)
                    && !"descending".equals(distribution)) {
                throw new IllegalArgumentException("error: unknown distribution");
            }
            if (trials <= 0) {
                throw new IllegalArgumentException("trials must be positive");
            }
            if (warmup < 0) {
                throw new IllegalArgumentException("warmup must be non-negative");
            }

            if (searchCase == null) {
                if ("quicksort".equals(algorithm)) {
                    searchCase = "sort";
                } else if ("linear_search".equals(algorithm)) {
                    searchCase = "first_hit";
                } else {
                    searchCase = "middle_hit";
                }
            }

            if ("quicksort".equals(algorithm) && !"sort".equals(searchCase)) {
                throw new IllegalArgumentException("quicksort only supports --search-case sort");
            }
            if (!"quicksort".equals(algorithm) && "sort".equals(searchCase)) {
                throw new IllegalArgumentException("search algorithms require a hit/miss search case");
            }

            return new Config(algorithm, distribution, n, seed, inputFile, trials, warmup, searchCase);
        }
    }
}
