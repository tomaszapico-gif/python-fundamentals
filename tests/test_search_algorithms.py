"""Pruebas unitarias de src/search_algorithms.py."""

import unittest

from src import search_algorithms as sa


class LinearSearchTests(unittest.TestCase):
    def test_finds_element(self):
        self.assertEqual(sa.linear_search([5, 3, 8], 8), 2)

    def test_missing_element(self):
        self.assertEqual(sa.linear_search([5, 3, 8], 9), -1)

    def test_empty_collection(self):
        self.assertEqual(sa.linear_search([], 1), -1)
        self.assertEqual(sa.linear_search_all([], 1), [])

    def test_single_element(self):
        self.assertEqual(sa.linear_search([7], 7), 0)

    def test_duplicates_return_first_position(self):
        self.assertEqual(sa.linear_search([4, 2, 4, 2], 2), 1)
        self.assertEqual(sa.linear_search_all([4, 2, 4, 2], 2), [1, 3])

    def test_steps_when_missing_equal_length(self):
        self.assertEqual(sa.linear_search_with_steps([5, 3, 8], 9), (-1, 3))

    def test_steps_when_first(self):
        self.assertEqual(sa.linear_search_with_steps([5, 3, 8], 5), (0, 1))


class SortedCheckTests(unittest.TestCase):
    def test_is_sorted(self):
        self.assertTrue(sa.is_sorted([]))
        self.assertTrue(sa.is_sorted([1]))
        self.assertTrue(sa.is_sorted([1, 2, 2, 5]))
        self.assertFalse(sa.is_sorted([2, 1]))


class BinarySearchTests(unittest.TestCase):
    DATA = [1, 3, 5, 7, 9, 11]

    def test_finds_every_element(self):
        for index, value in enumerate(self.DATA):
            with self.subTest(value=value):
                self.assertEqual(sa.binary_search(self.DATA, value), index)

    def test_missing_values(self):
        for value in (0, 4, 12):
            with self.subTest(value=value):
                self.assertEqual(sa.binary_search(self.DATA, value), -1)

    def test_empty_and_single(self):
        self.assertEqual(sa.binary_search([], 3), -1)
        self.assertEqual(sa.binary_search([3], 3), 0)
        self.assertEqual(sa.binary_search([3], 4), -1)

    def test_duplicates_return_a_matching_position(self):
        data = [1, 2, 2, 2, 3]
        index = sa.binary_search(data, 2)
        self.assertEqual(data[index], 2)

    def test_unsorted_data_is_rejected(self):
        with self.assertRaises(ValueError):
            sa.binary_search([3, 1, 2], 1)

    def test_strings_sorted_by_code_point(self):
        words = sorted(["pera", "manzana", "banana", "uva"])
        self.assertEqual(sa.binary_search(words, "pera"), words.index("pera"))

    def test_steps_grow_logarithmically(self):
        data = list(range(1024))
        for target in (0, 511, 1023, 2000):
            with self.subTest(target=target):
                _index, steps = sa.binary_search_with_steps(data, target)
                self.assertLessEqual(steps, 11)  # log2(1024) + 1


class WordAndRecordSearchTests(unittest.TestCase):
    def test_search_word_case_insensitive(self):
        self.assertEqual(sa.search_word(["Hola", "mundo", "hola"], "HOLA"), [0, 2])

    def test_search_word_case_sensitive(self):
        self.assertEqual(sa.search_word(["Hola", "hola"], "Hola", case_sensitive=True), [0])

    def test_search_word_is_whole_word(self):
        self.assertEqual(sa.search_word(["sol", "solo"], "sol"), [0])

    def test_search_word_empty_target(self):
        with self.assertRaises(ValueError):
            sa.search_word(["a"], "  ")

    def test_find_records_contains_and_exact(self):
        records = [{"name": "Mate"}, {"name": "Mate de calabaza"}, {"name": "Taza"}]
        self.assertEqual(len(sa.find_records(records, "name", "mate")), 2)
        self.assertEqual(sa.find_records(records, "name", "MATE", exact=True), [{"name": "Mate"}])

    def test_find_records_ignores_records_without_field(self):
        records = [{"name": "a"}, {"other": "a"}]
        self.assertEqual(sa.find_records(records, "name", "a"), [{"name": "a"}])

    def test_find_records_empty_value(self):
        with self.assertRaises(ValueError):
            sa.find_records([{"name": "a"}], "name", "")


class CompareSearchMethodsTests(unittest.TestCase):
    def test_unsorted_input(self):
        result = sa.compare_search_methods(["perro", "árbol", "casa", "luz"], "luz")
        self.assertFalse(result["was_sorted"])
        self.assertTrue(result["linear"]["found"])
        self.assertEqual(result["linear"]["steps"], 4)
        self.assertTrue(result["binary"]["found"])

    def test_missing_target(self):
        result = sa.compare_search_methods([1, 2, 3, 4, 5, 6, 7, 8], 99)
        self.assertTrue(result["was_sorted"])
        self.assertEqual(result["linear"], {"found": False, "index": -1, "steps": 8})
        self.assertFalse(result["binary"]["found"])
        self.assertLess(result["binary"]["steps"], result["linear"]["steps"])


if __name__ == "__main__":
    unittest.main()
