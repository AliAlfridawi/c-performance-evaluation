package bench;

/**
 * Comparison metric (match Python/C): one increment per scalar comparison between two values
 * that drives the algorithm (partition loop, search).
 */
public final class Algorithms {

    private static long comparisonCount;

    private Algorithms() {}

    public static void resetComparisonCount() {
        comparisonCount = 0;
    }

    public static long getComparisonCount() {
        return comparisonCount;
    }

    private static void inc() {
        comparisonCount++;
    }

    public static void quickSort(int[] arr) {
        if (arr == null || arr.length == 0) {
            return;
        }
        quickSortRange(arr, 0, arr.length - 1);
    }

    private static void quickSortRange(int[] arr, int low, int high) {
        if (low >= high) {
            return;
        }
        int p = partition(arr, low, high);
        quickSortRange(arr, low, p - 1);
        quickSortRange(arr, p + 1, high);
    }

    private static int partition(int[] arr, int low, int high) {
        int pivot = arr[high];
        int i = low - 1;
        for (int j = low; j < high; j++) {
            inc();
            if (arr[j] <= pivot) {
                i++;
                swap(arr, i, j);
            }
        }
        swap(arr, i + 1, high);
        return i + 1;
    }

    private static void swap(int[] arr, int i, int j) {
        int t = arr[i];
        arr[i] = arr[j];
        arr[j] = t;
    }

    public static int linearSearch(int[] arr, int target) {
        if (arr == null) {
            return -1;
        }
        for (int i = 0; i < arr.length; i++) {
            inc();
            if (arr[i] == target) {
                return i;
            }
        }
        return -1;
    }

    public static int binarySearch(int[] arr, int target) {
        if (arr == null || arr.length == 0) {
            return -1;
        }
        int lo = 0;
        int hi = arr.length - 1;
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;
            inc();
            if (arr[mid] == target) {
                return mid;
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
}
