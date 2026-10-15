"""Pruebas de src/report_generator.py."""

import csv
import io
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from src import report_generator as rg


def sample_text_summary():
    return {
        "characters": 10,
        "characters_without_whitespace": 9,
        "words": 2,
        "unique_words": 2,
        "lines": 1,
        "empty_lines": 0,
        "average_word_length": 4.5,
        "shortest_word": "hola",
        "longest_word": "canción",
        "most_common_words": [{"word": "canción", "count": 1}, {"word": "hola", "count": 1}],
    }


class FormattingTests(unittest.TestCase):
    def test_format_number(self):
        self.assertEqual(rg.format_number(None), "N/D")
        self.assertEqual(rg.format_number(25.0), "25")
        self.assertEqual(rg.format_number(2.5), "2.50")
        self.assertEqual(rg.format_number(3.14159), "3.14")

    def test_text_summary_contains_values(self):
        text = rg.format_text_summary(sample_text_summary())
        self.assertIn("Palabras", text)
        self.assertIn("canción (1)", text)
        self.assertIn("4.50", text)

    def test_text_summary_without_words(self):
        summary = sample_text_summary()
        summary["shortest_word"] = None
        summary["most_common_words"] = []
        self.assertIn("(no hay palabras)", rg.format_text_summary(summary))

    def test_records_table_truncates_long_values(self):
        records = [{"name": "Auriculares inalámbricos con micrófono", "qty": "5"}]
        table = rg.format_records_table(["name", "qty"], records, max_column_width=10)
        self.assertIn("Auricular…", table)
        self.assertNotIn("micrófono", table)

    def test_records_table_limits_rows_and_handles_empty(self):
        records = [{"n": str(number)} for number in range(5)]
        table = rg.format_records_table(["n"], records, max_rows=2)
        self.assertEqual(len(table.splitlines()), 4)  # encabezado + separador + 2 filas
        self.assertEqual(rg.format_records_table(["n"], []), "(sin registros)")

    def test_records_to_csv_roundtrip_with_commas(self):
        records = [{"name": "Taza, grande", "qty": "3"}]
        text = rg.records_to_csv_text(["name", "qty"], records)
        rows = list(csv.DictReader(io.StringIO(text)))
        self.assertEqual(rows, records)

    def test_safe_file_stem(self):
        self.assertEqual(rg.safe_file_stem("mi informe (v2).txt"), "mi_informe__v2_")
        self.assertEqual(rg.safe_file_stem(".txt"), "_txt")

    def test_build_report_filename(self):
        moment = datetime(2026, 10, 15, 17, 36, 5)
        self.assertEqual(
            rg.build_report_filename("example.txt", "text", "json", moment),
            "text_report_example_20261015-173605.json",
        )

    def test_unknown_report_type(self):
        with self.assertRaises(ValueError):
            rg.create_report("pdf", "a.txt", {})


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp_dir.name)
        self.report = rg.create_report("text", "ejemplo.txt", sample_text_summary())

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_exports_txt_and_json(self):
        paths = rg.export_report(self.report, self.folder)
        self.assertEqual([path.suffix for path in paths], [".txt", ".json"])
        text_content = paths[0].read_text(encoding="utf-8")
        self.assertIn("INFORME DE ANÁLISIS DE TEXTO", text_content)
        data = json.loads(paths[1].read_text(encoding="utf-8"))
        self.assertEqual(data["source_file"], "ejemplo.txt")
        self.assertEqual(data["data"]["longest_word"], "canción")
        self.assertIn("canción", paths[1].read_text(encoding="utf-8"))  # sin escapes \\u

    def test_exporting_twice_does_not_overwrite(self):
        first = rg.export_report(self.report, self.folder, formats=["json"])
        second = rg.export_report(self.report, self.folder, formats=["json"])
        self.assertNotEqual(first[0], second[0])
        self.assertEqual(len(list(self.folder.iterdir())), 2)

    def test_invalid_format_writes_nothing(self):
        with self.assertRaises(ValueError):
            rg.export_report(self.report, self.folder, formats=["txt", "pdf"])
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_export_records_to_csv(self):
        path = rg.export_records_to_csv(
            ["sku"], [{"sku": "A1"}, {"sku": "A2"}], self.folder, "inventory.csv", "filter"
        )
        self.assertTrue(path.name.startswith("filter_inventory_"))
        self.assertEqual(path.read_text(encoding="utf-8").splitlines(), ["sku", "A1", "A2"])


if __name__ == "__main__":
    unittest.main()
