"""
Sorting Algorithms Implementation and Benchmarks
Contains: Quick Sort, Merge Sort, and Bubble Sort
"""
import random
import time

def bubble_sort(arr):
    """Classic Bubble Sort algorithm - O(n^2)"""
    n = len(arr)
    arr = list(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def quick_sort(arr):
    """Divide and Conquer Quick Sort - O(n log n) average"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

def merge_sort(arr):
    """Stable Merge Sort algorithm - O(n log n)"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged

if __name__ == "__main__":
    test_data = [random.randint(1, 1000) for _ in range(50)]
    print("Bubble sorted:", bubble_sort(test_data[:10]))
    print("Quick sorted:", quick_sort(test_data[:10]))
    print("Merge sorted:", merge_sort(test_data[:10]))
