package bench;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class AlgorithmsTest {

    @Test
    void quickSortEmpty() {
        Algorithms.resetComparisonCount();
        Algorithms.quickSort(new int[0]);
        assertEquals(0, Algorithms.getComparisonCount());
    }

    @Test
    void quickSortSingle() {
        int[] a = {42};
        Algorithms.quickSort(a);
        assertArrayEquals(new int[] {42}, a);
    }

    @Test
    void quickSortReverse() {
        int[] a = {4, 3, 2, 1};
        Algorithms.quickSort(a);
        assertArrayEquals(new int[] {1, 2, 3, 4}, a);
    }

    @Test
    void quickSortN10FromDataSets() {
        int[] a = {73, 21, 56, 89, 12, 45, 98, 34, 67, 4};
        int[] expected = {4, 12, 21, 34, 45, 56, 67, 73, 89, 98};
        Algorithms.quickSort(a);
        assertArrayEquals(expected, a);
    }

    @Test
    void linearSearch() {
        int[] a = {1, 2, 3};
        assertEquals(0, Algorithms.linearSearch(a, 1));
        assertEquals(2, Algorithms.linearSearch(a, 3));
        assertEquals(-1, Algorithms.linearSearch(a, 99));
        assertEquals(-1, Algorithms.linearSearch(new int[0], 1));
    }

    @Test
    void binarySearch() {
        int[] a = {1, 3, 5, 7, 9};
        assertEquals(2, Algorithms.binarySearch(a, 5));
        assertEquals(-1, Algorithms.binarySearch(a, 4));
        assertEquals(-1, Algorithms.binarySearch(new int[0], 1));
        assertEquals(0, Algorithms.binarySearch(new int[] {42}, 42));
        assertEquals(-1, Algorithms.binarySearch(new int[] {42}, 1));
    }
}
