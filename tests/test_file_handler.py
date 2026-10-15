"""Pruebas de src/file_handler.py usando carpetas temporales."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

from src import file_handler as fh


class ReadTextFileTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_reads_utf8_with_accents(self):
        path = self.folder / "texto.txt"
        path.write_text("Canción del ñandú\n", encoding="utf-8")
        self.assertEqual(fh.read_text_file(path), "Canción del ñandú\n")

    def test_bom_is_removed(self):
        path = self.folder / "bom.txt"
        path.write_bytes("\ufeffhola".encode("utf-8"))
        self.assertEqual(fh.read_text_file(path), "hola")

    def test_empty_file_returns_empty_string(self):
        path = self.folder / "vacio.txt"
        path.write_text("", encoding="utf-8")
        self.assertEqual(fh.read_text_file(path), "")

    def test_missing_file(self):
        with self.assertRaises(fh.FileAccessError) as context:
            fh.read_text_file(self.folder / "no_existe.txt")
        self.assertIn("no existe", str(context.exception))

    def test_directory_is_rejected(self):
        with self.assertRaises(fh.FileAccessError):
            fh.read_text_file(self.folder)

    def test_non_utf8_file(self):
        path = self.folder / "latin1.txt"
        path.write_bytes("canción".encode("latin-1"))
        with self.assertRaises(fh.FileAccessError) as context:
            fh.read_text_file(path)
        self.assertIn("UTF-8", str(context.exception))

    def test_file_too_large(self):
        path = self.folder / "grande.txt"
        path.write_text("x" * 100, encoding="utf-8")
        with self.assertRaises(fh.FileAccessError):
            fh.read_text_file(path, max_size_bytes=10)

    @unittest.skipIf(sys.platform.startswith("win"), "chmod no restringe la lectura en Windows")
    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root puede leer cualquier archivo")
    def test_file_without_read_permission(self):
        path = self.folder / "privado.txt"
        path.write_text("secreto", encoding="utf-8")
        path.chmod(0o000)
        try:
            with self.assertRaises(fh.FileAccessError) as context:
                fh.read_text_file(path)
            self.assertIn("permisos", str(context.exception))
        finally:
            path.chmod(0o600)


class PathTests(unittest.TestCase):
    def test_validate_extension(self):
        fh.validate_extension("datos.CSV", [".csv"])
        with self.assertRaises(fh.FileAccessError):
            fh.validate_extension("datos.xlsx", [".csv"])
        with self.assertRaises(fh.FileAccessError):
            fh.validate_extension("sin_extension", [".txt"])

    def test_resolve_strips_spaces_and_quotes(self):
        with tempfile.TemporaryDirectory() as folder:
            absolute = Path(folder).resolve() / "archivo.txt"
            self.assertEqual(fh.resolve_input_path(f'  "{absolute}"  '), absolute)
            self.assertEqual(fh.resolve_input_path(f"'{absolute}'"), absolute)

    def test_resolve_empty_path(self):
        with self.assertRaises(fh.FileAccessError):
            fh.resolve_input_path("   ")

    def test_resolve_relative_path_from_project_root(self):
        with tempfile.TemporaryDirectory() as fake_root:
            sample = Path(fake_root) / "samples" / "solo_en_raiz_xyz.txt"
            sample.parent.mkdir()
            sample.write_text("hola", encoding="utf-8")
            resolved = fh.resolve_input_path("samples/solo_en_raiz_xyz.txt", project_root=Path(fake_root))
            self.assertEqual(resolved, sample)


class WriteTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_creates_missing_directory_and_file(self):
        target_dir = self.folder / "nuevo" / "informes"
        path = fh.write_new_text_file(target_dir, "informe.txt", "contenido ñ")
        self.assertEqual(path, target_dir / "informe.txt")
        self.assertEqual(path.read_text(encoding="utf-8"), "contenido ñ")

    def test_never_overwrites(self):
        first = fh.write_new_text_file(self.folder, "informe.txt", "primero")
        second = fh.write_new_text_file(self.folder, "informe.txt", "segundo")
        third = fh.write_new_text_file(self.folder, "informe.txt", "tercero")
        self.assertEqual(second.name, "informe_1.txt")
        self.assertEqual(third.name, "informe_2.txt")
        self.assertEqual(first.read_text(encoding="utf-8"), "primero")

    def test_directory_path_that_is_a_file(self):
        blocking_file = self.folder / "ocupado"
        blocking_file.write_text("x", encoding="utf-8")
        with self.assertRaises(fh.FileAccessError):
            fh.ensure_directory(blocking_file)


if __name__ == "__main__":
    unittest.main()
