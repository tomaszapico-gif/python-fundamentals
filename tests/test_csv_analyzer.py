"""Pruebas unitarias de src/csv_analyzer.py."""

import unittest

from src import csv_analyzer as ca

INVENTORY = (
    "sku,product,quantity,price\n"
    "A1,Cuaderno,10,850.50\n"
    "A2, Lapicera ,,320\n"
    "A3,Taza,doce,4500\n"
    "A4,Mate,40,6800,EXTRA\n"
    "A5,Termo,25,\n"
    "A6,\"Auriculares, con micrófono\",5,22000\n"
)


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.table = ca.parse_csv_text(INVENTORY)

    def test_headers_and_record_count(self):
        self.assertEqual(self.table["headers"], ["sku", "product", "quantity", "price"])
        self.assertEqual(ca.count_records(self.table), 5)

    def test_values_are_stripped(self):
        self.assertEqual(self.table["records"][1]["product"], "Lapicera")

    def test_quoted_field_with_comma(self):
        self.assertEqual(self.table["records"][4]["product"], "Auriculares, con micrófono")

    def test_malformed_row_is_excluded_and_reported(self):
        issues = self.table["issues"]
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["type"], "field_count")
        self.assertEqual(issues[0]["line"], 5)
        skus = [record["sku"] for record in self.table["records"]]
        self.assertNotIn("A4", skus)

    def test_record_lines(self):
        self.assertEqual(self.table["record_lines"], [2, 3, 4, 6, 7])

    def test_row_with_fewer_fields(self):
        table = ca.parse_csv_text("a,b,c\n1,2\n")
        self.assertEqual(ca.count_records(table), 0)
        self.assertIn("Se esperaban 3 campos y se encontraron 2", table["issues"][0]["message"])


class SpecialFileTests(unittest.TestCase):
    def test_empty_file(self):
        table = ca.parse_csv_text("")
        self.assertEqual(table["headers"], [])
        self.assertEqual(table["records"], [])
        self.assertEqual(table["issues"][0]["type"], "empty_file")

    def test_headers_without_records(self):
        table = ca.parse_csv_text("sku,product\n")
        self.assertEqual(table["headers"], ["sku", "product"])
        self.assertEqual(ca.count_records(table), 0)
        self.assertEqual(table["issues"], [])

    def test_blank_line_is_reported(self):
        table = ca.parse_csv_text("a,b\n1,2\n\n3,4\n")
        self.assertEqual(ca.count_records(table), 2)
        self.assertEqual(table["issues"][0]["type"], "blank_line")

    def test_semicolon_delimiter_detected(self):
        table = ca.parse_csv_text("producto;precio\nMate;12,5\n")
        self.assertEqual(table["delimiter"], ";")
        self.assertEqual(table["records"][0], {"producto": "Mate", "precio": "12,5"})

    def test_bom_is_removed_from_first_header(self):
        table = ca.parse_csv_text("﻿sku,name\n1,a\n")
        self.assertEqual(table["headers"], ["sku", "name"])

    def test_duplicate_header_is_an_error(self):
        with self.assertRaises(ca.CsvFormatError):
            ca.parse_csv_text("a,b,a\n1,2,3\n")

    def test_empty_header_is_an_error(self):
        with self.assertRaises(ca.CsvFormatError):
            ca.parse_csv_text("a,,c\n1,2,3\n")


class EmptyFieldTests(unittest.TestCase):
    def test_find_empty_fields(self):
        table = ca.parse_csv_text(INVENTORY)
        self.assertEqual(
            ca.find_empty_fields(table),
            [{"line": 3, "column": "quantity"}, {"line": 6, "column": "price"}],
        )

    def test_count_by_column_includes_zeros(self):
        table = ca.parse_csv_text(INVENTORY)
        self.assertEqual(
            ca.count_empty_fields_by_column(table),
            {"sku": 0, "product": 0, "quantity": 1, "price": 1},
        )


class ParseNumberTests(unittest.TestCase):
    def test_valid_numbers(self):
        cases = {"12": 12.0, "12.5": 12.5, "12,5": 12.5, " -3 ": -3.0, "1e3": 1000.0}
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(ca.parse_number(raw), expected)

    def test_invalid_numbers(self):
        for raw in ("", "   ", "abc", "doce", "1.234,5", "1,2,3", "1_000", "nan", "inf", "12 kg"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    ca.parse_number(raw)


class StatisticsTests(unittest.TestCase):
    def setUp(self):
        self.table = ca.parse_csv_text(INVENTORY)

    def test_statistics_with_invalid_and_empty_values(self):
        stats = ca.column_statistics(self.table, "quantity")
        self.assertEqual(stats["valid_count"], 3)  # 10, 25, 5
        self.assertEqual(stats["empty_count"], 1)
        self.assertEqual(stats["invalid_values"], [{"line": 4, "value": "doce"}])
        self.assertEqual(stats["minimum"], 5)
        self.assertEqual(stats["maximum"], 25)
        self.assertEqual(stats["total"], 40)
        self.assertAlmostEqual(stats["mean"], 40 / 3)
        self.assertEqual(stats["median"], 10)

    def test_median_with_even_count(self):
        stats = ca.column_statistics(self.table, "price")  # 850.5, 320, 4500, 22000
        self.assertEqual(stats["median"], (850.5 + 4500) / 2)

    def test_column_without_numbers(self):
        stats = ca.column_statistics(self.table, "product")
        self.assertEqual(stats["valid_count"], 0)
        self.assertIsNone(stats["mean"])
        self.assertIsNone(stats["median"])

    def test_unknown_column(self):
        with self.assertRaises(ValueError):
            ca.column_statistics(self.table, "stock")

    def test_numeric_column_detection(self):
        self.assertEqual(ca.detect_numeric_columns(self.table), ["quantity", "price"])
        self.assertFalse(ca.is_mostly_numeric(self.table, "sku"))


class SearchFilterSortTests(unittest.TestCase):
    def setUp(self):
        self.table = ca.parse_csv_text(INVENTORY)

    def test_search_in_all_columns(self):
        matches = ca.search_records(self.table, "TAZA")
        self.assertEqual([record["sku"] for record in matches], ["A3"])

    def test_search_returns_each_record_once(self):
        table = ca.parse_csv_text("a,b\nmate,mate\n")
        self.assertEqual(len(ca.search_records(table, "mate")), 1)

    def test_search_in_one_column(self):
        matches = ca.search_records(self.table, "ER", column="product")
        self.assertEqual([record["product"] for record in matches], ["Cuaderno", "Lapicera", "Termo"])
        self.assertEqual(ca.search_records(self.table, "A1", column="product"), [])

    def test_search_errors(self):
        with self.assertRaises(ValueError):
            ca.search_records(self.table, "   ")
        with self.assertRaises(ValueError):
            ca.search_records(self.table, "x", column="missing")

    def test_numeric_filter_skips_invalid_values(self):
        result = ca.filter_records(self.table, "quantity", ">=", "10")
        self.assertEqual([record["sku"] for record in result["records"]], ["A1", "A5"])
        self.assertEqual(result["skipped"], 2)  # vacío y "doce"

    def test_numeric_equality(self):
        result = ca.filter_records(self.table, "quantity", "==", "10.0")
        self.assertEqual([record["sku"] for record in result["records"]], ["A1"])

    def test_equality_with_empty_value_finds_empty_fields(self):
        result = ca.filter_records(self.table, "price", "==", "")
        self.assertEqual([record["sku"] for record in result["records"]], ["A5"])

    def test_not_equal_and_contains(self):
        not_equal = ca.filter_records(self.table, "sku", "!=", "a1")
        self.assertEqual(len(not_equal["records"]), 4)
        contains = ca.filter_records(self.table, "product", "contains", "micró")
        self.assertEqual(len(contains["records"]), 1)

    def test_filter_input_errors(self):
        with self.assertRaises(ValueError):
            ca.filter_records(self.table, "quantity", "=>", "1")
        with self.assertRaises(ValueError):
            ca.filter_records(self.table, "quantity", ">", "diez")
        with self.assertRaises(ValueError):
            ca.filter_records(self.table, "product", "contains", "")

    def test_sort_numeric_column(self):
        result = ca.sort_records_by_field(self.table, "quantity")
        self.assertTrue(result["numeric"])
        self.assertEqual([record["sku"] for record in result["records"]], ["A6", "A1", "A5", "A2", "A3"])
        self.assertEqual(result["moved_to_end"], 2)

    def test_sort_text_column_descending(self):
        result = ca.sort_records_by_field(self.table, "product", descending=True)
        self.assertFalse(result["numeric"])
        self.assertEqual(result["records"][0]["product"], "Termo")


if __name__ == "__main__":
    unittest.main()
