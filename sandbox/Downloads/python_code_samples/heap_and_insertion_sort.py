"""
Heap Sort and Insertion Sort algorithms.
"""
def insertion_sort(arr):
    """In-place Insertion Sort - O(n^2)"""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr

def heap_sort(arr):
    """Heap Sort using binary heap - O(n log n)"""
    import heapq
    heap = list(arr)
    heapq.heapify(heap)
    return [heapq.heappop(heap) for _ in range(len(heap))]
