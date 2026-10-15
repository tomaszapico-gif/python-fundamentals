"""Pruebas de la interfaz de consola (src/main.py).

Se simula lo que escribe el usuario reemplazando ``input`` con
``unittest.mock.patch`` y se captura lo que el programa imprime.
"""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from src import main
from src.file_handler import PROJECT_ROOT

EXAMPLE_TXT = str(PROJECT_ROOT / "samples" / "example.txt")
INVENTORY_CSV = str(PROJECT_ROOT / "samples" / "inventory.csv")


def run_with_inputs(user_inputs, function, *args):
    """Ejecuta ``function`` simulando las respuestas del usuario.

    Returns:
        ``(valor_devuelto, texto_impreso)``.
    """
    output = io.StringIO()
    with patch("builtins.input", side_effect=list(user_inputs)), redirect_stdout(output):
        result = function(*args)
    return result, output.getvalue()


class InputValidationTests(unittest.TestCase):
    def test_menu_option_retries_until_valid(self):
        result, output = run_with_inputs(["9", "", "abc", " 2 "], main.ask_menu_option, ["1", "2"])
        self.assertEqual(result, "2")
        self.assertIn("Opción inválida: '9'", output)
        self.assertIn("No escribiste ninguna opción", output)

    def test_positive_int_validation(self):
        result, output = run_with_inputs(["-1", "cero", "50", "3"], main.ask_positive_int, "N: ", 5, 10)
        self.assertEqual(result, 3)
        self.assertIn("no es un número entero positivo", output)
        self.assertIn("entre 1 y 10", output)

    def test_positive_int_default(self):
        result, _output = run_with_inputs([""], main.ask_positive_int, "N: ", 5, 10)
        self.assertEqual(result, 5)

    def test_yes_no(self):
        result, output = run_with_inputs(["quizás", "SÍ"], main.ask_yes_no, "? ")
        self.assertTrue(result)
        self.assertIn("Respondé 's'", output)

    def test_ask_column_by_number_or_name(self):
        headers = ["sku", "price"]
        self.assertEqual(run_with_inputs(["2"], main.ask_column, headers)[0], "price")
        result, output = run_with_inputs(["stock", "SKU"], main.ask_column, headers)
        self.assertEqual(result, "sku")
        self.assertIn("La columna 'stock' no existe", output)

    def test_end_of_input_exits_cleanly(self):
        result, output = run_with_inputs([EOFError()], main.main, [])
        self.assertEqual(result, 0)
        self.assertIn("Programa interrumpido", output)


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.reports = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_main(self, user_inputs):
        return run_with_inputs(user_inputs, main.main, ["--reports-dir", self.reports])

    def test_text_session_with_export(self):
        inputs = ["1", EXAMPLE_TXT, "1", "3", "Lucía", "8", "0", "0"]
        result, output = self.run_main(inputs)
        self.assertEqual(result, 0)
        self.assertIn("Resumen general", output)
        self.assertIn("La palabra 'lucía' aparece", output)
        self.assertIn("¡Hasta luego!", output)
        created = sorted(path.suffix for path in Path(self.reports).iterdir())
        self.assertEqual(created, [".json", ".txt"])

    def test_missing_file_does_not_close_the_program(self):
        inputs = ["1", "no_existe_123.txt", "0"]
        result, output = self.run_main(inputs)
        self.assertEqual(result, 0)
        self.assertIn("El archivo no existe", output)
        self.assertIn("¡Hasta luego!", output)

    def test_wrong_extension_is_reported(self):
        _result, output = self.run_main(["2", EXAMPLE_TXT, "0"])
        self.assertIn("Se esperaba un archivo .csv", output)

    def test_csv_session_filter_and_export_result(self):
        inputs = [
            "2", INVENTORY_CSV,
            "6", "quantity", "3", "20",   # filtrar quantity > 20
            "10",                          # exportar el resultado como CSV
            "0", "0",
        ]
        _result, output = self.run_main(inputs)
        self.assertIn("Se omitieron 2 registro(s)", output)
        self.assertIn("Se exportaron 5 registro(s)", output)
        exported = list(Path(self.reports).glob("filter_inventory_*.csv"))
        self.assertEqual(len(exported), 1)
        self.assertEqual(len(exported[0].read_text(encoding="utf-8").splitlines()), 6)

    def test_export_without_previous_result(self):
        _result, output = self.run_main(["2", INVENTORY_CSV, "10", "0", "0"])
        self.assertIn("Todavía no hay resultados", output)


if __name__ == "__main__":
    unittest.main()
