"""Pruebas de integración: archivo real -> análisis -> informe (src/analyzer.py)."""

import tempfile
import unittest
from pathlib import Path

from src import analyzer
from src.csv_analyzer import CsvFormatError
from src.file_handler import PROJECT_ROOT, FileAccessError


class TextFileIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write(self, name, content):
        path = self.folder / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_full_text_report(self):
        path = self.write("cuento.txt", "Hola, mundo.\n\n¡Hola   otra vez!\n")
        report = analyzer.analyze_text_file(path, top_n=2)
        data = report["data"]
        self.assertEqual(report["report_type"], "text")
        self.assertEqual(report["source_file"], "cuento.txt")
        self.assertEqual(data["words"], 5)
        self.assertEqual(data["unique_words"], 4)
        self.assertEqual(data["lines"], 3)
        self.assertEqual(data["empty_lines"], 1)
        self.assertEqual(data["characters"], 32)
        self.assertEqual(data["average_word_length"], 4.0)  # (4+5+4+4+3)/5
        self.assertEqual(data["most_common_words"][0], {"word": "hola", "count": 2})

    def test_empty_text_file(self):
        report = analyzer.analyze_text_file(self.write("vacio.txt", ""))
        data = report["data"]
        self.assertEqual(data["words"], 0)
        self.assertEqual(data["lines"], 0)
        self.assertIsNone(data["longest_word"])
        self.assertEqual(data["most_common_words"], [])

    def test_wrong_extension(self):
        with self.assertRaises(FileAccessError):
            analyzer.analyze_text_file(self.write("datos.csv", "a,b"))

    def test_missing_file(self):
        with self.assertRaises(FileAccessError):
            analyzer.analyze_text_file(self.folder / "no_existe.txt")


class CsvFileIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write(self, name, content):
        path = self.folder / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_full_csv_report(self):
        path = self.write(
            "stock.csv",
            "sku,qty,price\nA,10,2.5\nB,,abc\nC,30,7.5,extra\nD,20,4\n",
        )
        data = analyzer.analyze_csv_file(path)["data"]
        self.assertEqual(data["record_count"], 3)
        self.assertEqual(data["malformed_rows"], 1)
        self.assertEqual(data["total_empty_fields"], 1)
        columns = [statistics["column"] for statistics in data["numeric_columns"]]
        self.assertEqual(columns, ["qty", "price"])
        qty = data["numeric_columns"][0]
        self.assertEqual((qty["minimum"], qty["maximum"], qty["mean"]), (10, 20, 15))
        price = data["numeric_columns"][1]
        self.assertEqual(price["invalid_count"], 1)
        self.assertEqual(price["mean"], 3.25)

    def test_csv_with_headers_only(self):
        data = analyzer.analyze_csv_file(self.write("solo.csv", "a,b\n"))["data"]
        self.assertEqual(data["record_count"], 0)
        self.assertEqual(data["numeric_columns"], [])

    def test_invalid_headers_raise_format_error(self):
        with self.assertRaises(CsvFormatError):
            analyzer.load_csv(self.write("roto.csv", "a,a\n1,2\n"))


class SampleFilesSmokeTests(unittest.TestCase):
    """Verifica que los archivos de ejemplo del repositorio se puedan analizar."""

    def test_example_txt(self):
        data = analyzer.analyze_text_file(PROJECT_ROOT / "samples" / "example.txt")["data"]
        self.assertGreater(data["words"], 0)
        self.assertGreater(data["empty_lines"], 0)

    def test_inventory_csv(self):
        data = analyzer.analyze_csv_file(PROJECT_ROOT / "samples" / "inventory.csv")["data"]
        self.assertEqual(data["record_count"], 11)
        self.assertEqual(data["malformed_rows"], 1)
        self.assertEqual(data["total_empty_fields"], 2)


if __name__ == "__main__":
    unittest.main()
