# Python code for sorting a list (array)

def demonstrate_sorting():
    """
    Demonstrates different ways to sort a list in Python.
    """

    # --- Example 1: Using the list.sort() method (in-place sort) ---
    print("--- Using list.sort() (in-place) ---")
    my_list_1 = [5, 1, 8, 92, -5, 0, 33]
    print(f"Original list: {my_list_1}")

    # Sort in ascending order (default)
    my_list_1.sort()
    print(f"Sorted ascending: {my_list_1}") # Original list is modified

    # Sort in descending order
    my_list_1.sort(reverse=True)
    print(f"Sorted descending: {my_list_1}") # Original list is modified again
    print("-" * 30)

    # --- Example 2: Using the sorted() function (returns a new list) ---
    print("--- Using sorted() function (returns new list) ---")
    my_list_2 = [6, 2, 7, 93, -4, 1, 32]
    print(f"Original list: {my_list_2}")

    # Sort in ascending order (default)
    sorted_list_asc = sorted(my_list_2)
    print(f"New sorted list (ascending): {sorted_list_asc}")
    print(f"Original list (unchanged): {my_list_2}")

    # Sort in descending order
    sorted_list_desc = sorted(my_list_2, reverse=True)
    print(f"New sorted list (descending): {sorted_list_desc}")
    print(f"Original list (still unchanged): {my_list_2}")
    print("-" * 30)

    # --- Example 3: Sorting a list of strings ---
    print("--- Sorting a list of strings ---")
    string_list = ["banana", "apple", "cherry", "date"]
    print(f"Original string list: {string_list}")

    # Ascending (alphabetical)
    string_list.sort()
    print(f"Sorted string list (ascending): {string_list}")

    # Descending
    sorted_string_list_desc = sorted(string_list, reverse=True)
    print(f"New sorted string list (descending): {sorted_string_list_desc}")
    print("-" * 30)

    # --- Example 4: Sorting with a custom key ---
    # For example, sorting a list of strings by their length
    print("--- Sorting with a custom key (by length of string) ---")
    words = ["kiwi", "strawberry", "fig", "blueberry"]
    print(f"Original list of words: {words}")

    # Sort by length of the string
    sorted_words_by_length = sorted(words, key=len)
    print(f"Sorted by length (ascending): {sorted_words_by_length}")

    # Sort by length in descending order
    sorted_words_by_length_desc = sorted(words, key=len, reverse=True)
    print(f"Sorted by length (descending): {sorted_words_by_length_desc}")
    print("-" * 30)

if __name__ == "__main__":
    demonstrate_sorting()
