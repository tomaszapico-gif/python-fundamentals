"""Pruebas unitarias de src/sorting_algorithms.py."""

import random
import unittest

from src import sorting_algorithms as so


class BubbleSortTests(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(so.bubble_sort([]), [])
        self.assertEqual(so.bubble_sort_with_stats([]), ([], 0, 0))

    def test_single_element(self):
        self.assertEqual(so.bubble_sort_with_stats([42]), ([42], 0, 0))

    def test_unsorted_list(self):
        self.assertEqual(so.bubble_sort([5, 1, 4, 2, 8]), [1, 2, 4, 5, 8])

    def test_repeated_elements(self):
        self.assertEqual(so.bubble_sort([3, 1, 3, 2, 1]), [1, 1, 2, 3, 3])

    def test_already_sorted_stops_after_one_pass(self):
        result, comparisons, swaps = so.bubble_sort_with_stats([1, 2, 3, 4, 5])
        self.assertEqual(result, [1, 2, 3, 4, 5])
        self.assertEqual(comparisons, 4)  # n - 1: mejor caso O(n)
        self.assertEqual(swaps, 0)

    def test_reversed_list_is_worst_case(self):
        result, comparisons, swaps = so.bubble_sort_with_stats([5, 4, 3, 2, 1])
        self.assertEqual(result, [1, 2, 3, 4, 5])
        self.assertEqual(comparisons, 10)  # n(n-1)/2
        self.assertEqual(swaps, 10)

    def test_descending_order(self):
        self.assertEqual(so.bubble_sort([1, 3, 2], reverse=True), [3, 2, 1])

    def test_does_not_modify_input(self):
        original = [3, 2, 1]
        so.bubble_sort(original)
        self.assertEqual(original, [3, 2, 1])

    def test_key_and_stability(self):
        people = [("Ana", 30), ("Beto", 25), ("Caro", 30), ("Dani", 25)]
        result = so.bubble_sort(people, key=lambda person: person[1])
        self.assertEqual(result, [("Beto", 25), ("Dani", 25), ("Ana", 30), ("Caro", 30)])

    def test_matches_builtin_sorted(self):
        generator = random.Random(2026)
        for size in (2, 7, 30, 100):
            data = [generator.randint(-50, 50) for _ in range(size)]
            with self.subTest(size=size):
                self.assertEqual(so.bubble_sort(data), sorted(data))
                self.assertEqual(so.bubble_sort(data, reverse=True), sorted(data, reverse=True))


class AlphabeticalSortTests(unittest.TestCase):
    def test_spanish_order(self):
        words = ["zapato", "oso", "ñandú", "Banco", "nube", "árbol"]
        self.assertEqual(
            so.sort_alphabetically(words), ["árbol", "Banco", "nube", "ñandú", "oso", "zapato"]
        )

    def test_enye_goes_after_n(self):
        self.assertEqual(so.sort_alphabetically(["año", "anual"]), ["anual", "año"])

    def test_reverse(self):
        self.assertEqual(so.sort_alphabetically(["b", "a", "c"], reverse=True), ["c", "b", "a"])

    def test_key_keeps_original_text(self):
        self.assertEqual(so.alphabetical_key("Árbol"), ("arbol", "Árbol"))

    def test_bubble_sort_with_alphabetical_key_matches_builtin(self):
        words = ["éxito", "Eco", "elefante", "ñoqui", "nido", "zorro", "árbol"]
        self.assertEqual(
            so.bubble_sort(words, key=so.alphabetical_key), so.sort_alphabetically(words)
        )


class FrequencySortTests(unittest.TestCase):
    def test_sort_by_frequency(self):
        frequencies = {"b": 1, "a": 3, "c": 1, "d": 2}
        self.assertEqual(
            so.sort_by_frequency(frequencies), [("a", 3), ("d", 2), ("b", 1), ("c", 1)]
        )

    def test_empty(self):
        self.assertEqual(so.sort_by_frequency({}), [])


class RecordSortTests(unittest.TestCase):
    RECORDS = [
        {"name": "Mate", "price": "6800"},
        {"name": "Taza", "price": "abc"},
        {"name": "Lapicera", "price": "320"},
        {"name": "Termo", "price": ""},
        {"name": "Silla", "price": "95000"},
    ]

    def test_numeric_ascending_with_invalid_at_end(self):
        records, moved = so.sort_records(self.RECORDS, "price", value_converter=float)
        names = [record["name"] for record in records]
        self.assertEqual(names, ["Lapicera", "Mate", "Silla", "Taza", "Termo"])
        self.assertEqual(moved, 2)

    def test_numeric_descending_keeps_invalid_at_end(self):
        records, _moved = so.sort_records(
            self.RECORDS, "price", descending=True, value_converter=float
        )
        names = [record["name"] for record in records]
        self.assertEqual(names, ["Silla", "Mate", "Lapicera", "Taza", "Termo"])

    def test_text_field(self):
        records, moved = so.sort_records(self.RECORDS, "name")
        self.assertEqual(records[0]["name"], "Lapicera")
        self.assertEqual(moved, 0)

    def test_missing_field_goes_to_end(self):
        records, moved = so.sort_records([{"a": "2"}, {"b": "1"}, {"a": "1"}], "a")
        self.assertEqual(records, [{"a": "1"}, {"a": "2"}, {"b": "1"}])
        self.assertEqual(moved, 1)

    def test_empty_records(self):
        self.assertEqual(so.sort_records([], "a"), ([], 0))


if __name__ == "__main__":
    unittest.main()
