package bench;

import java.util.Arrays;
import java.util.Random;

/**
 * Wall time: System.nanoTime(). Comparisons: Algorithms.getComparisonCount().
 */
public final class Benchmark {

    private Benchmark() {}

    public static void main(String[] args) {
        if (args.length < 3) {
            System.err.println(
                    "usage: java bench.Benchmark <quicksort|linear_search|binary_search> "
                            + "<random|ascending|descending> <N> [--seed N]");
            System.exit(2);
        }
        String algo = args[0];
        String dist = args[1];
        int n = Integer.parseInt(args[2]);
        long seed = 42L;
        for (int i = 3; i + 1 < args.length; i++) {
            if ("--seed".equals(args[i])) {
                seed = Long.parseLong(args[i + 1]);
                break;
            }
        }
        if (n < 0) {
            System.err.println("N must be non-negative");
            System.exit(2);
        }
        int[] arr = buildArray(n, dist, seed);
        long comparisons;
        double seconds;
        if ("quicksort".equals(algo)) {
            Algorithms.resetComparisonCount();
            long t0 = System.nanoTime();
            Algorithms.quickSort(arr);
            long t1 = System.nanoTime();
            comparisons = Algorithms.getComparisonCount();
            seconds = (t1 - t0) / 1_000_000_000.0;
        } else if ("linear_search".equals(algo)) {
            int target = n > 0 ? arr[0] : 0;
            Algorithms.resetComparisonCount();
            long t0 = System.nanoTime();
            Algorithms.linearSearch(arr, target);
            long t1 = System.nanoTime();
            comparisons = Algorithms.getComparisonCount();
            seconds = (t1 - t0) / 1_000_000_000.0;
        } else if ("binary_search".equals(algo)) {
            int[] sorted = Arrays.copyOf(arr, arr.length);
            Arrays.sort(sorted);
            int target = n > 0 ? sorted[n / 2] : 0;
            Algorithms.resetComparisonCount();
            long t0 = System.nanoTime();
            Algorithms.binarySearch(sorted, target);
            long t1 = System.nanoTime();
            comparisons = Algorithms.getComparisonCount();
            seconds = (t1 - t0) / 1_000_000_000.0;
        } else {
            System.err.println("unknown algorithm");
            System.exit(2);
            return;
        }
        System.out.printf("java,%s,%s,%d,%d,%.9f%n", algo, dist, n, comparisons, seconds);
    }

    private static int[] buildArray(int n, String dist, long seed) {
        if (n == 0) {
            return new int[0];
        }
        if ("ascending".equals(dist)) {
            int[] a = new int[n];
            for (int i = 0; i < n; i++) {
                a[i] = i;
            }
            return a;
        }
        if ("descending".equals(dist)) {
            int[] a = new int[n];
            for (int i = 0; i < n; i++) {
                a[i] = n - 1 - i;
            }
            return a;
        }
        Random rng = new Random(seed);
        int[] a = new int[n];
        for (int i = 0; i < n; i++) {
            a[i] = 1 + rng.nextInt(1000);
        }
        return a;
    }
}
