"""Interfaz de consola (CLI) del analizador de textos y datos.

Este módulo SOLO se ocupa de conversar con el usuario: mostrar menús, pedir
datos, validar lo que se escribe y mostrar resultados. Todo el cálculo está
en los demás módulos.

Formas de ejecutarlo (ver README):

    python -m src.main          (desde la raíz del repositorio)
    python src/main.py          (desde la raíz o con la ruta completa)

Opciones de línea de comandos:

    --reports-dir CARPETA   carpeta donde se guardan los informes
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

if __package__ in (None, ""):
    # Al ejecutar "python src/main.py", Python no sabe que "src" es un paquete.
    # Agregamos la raíz del proyecto a la ruta de búsqueda de módulos para que
    # los imports "from src import ..." funcionen desde cualquier carpeta.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import analyzer, csv_analyzer, report_generator, search_algorithms
from src import sorting_algorithms, text_analyzer
from src.csv_analyzer import CsvFormatError
from src.file_handler import DEFAULT_REPORTS_DIR, FileAccessError, resolve_input_path

MAIN_MENU = (
    ("1", "Analizar un archivo de texto (.txt)"),
    ("2", "Analizar un archivo CSV (.csv)"),
    ("3", "Cambiar la carpeta de informes"),
    ("0", "Salir"),
)

TEXT_MENU = (
    ("1", "Ver resumen general"),
    ("2", "Ver palabras más frecuentes"),
    ("3", "Buscar una palabra (palabra completa)"),
    ("4", "Contar un fragmento (secuencia exacta de caracteres)"),
    ("5", "Mostrar líneas que contienen una palabra"),
    ("6", "Ordenar palabras distintas (bubble sort vs. sorted)"),
    ("7", "Comparar búsqueda lineal y binaria"),
    ("8", "Exportar informe (TXT y JSON)"),
    ("0", "Volver al menú principal"),
)

CSV_MENU = (
    ("1", "Ver resumen (encabezados, registros, estadísticas)"),
    ("2", "Ver problemas de formato"),
    ("3", "Ver campos vacíos"),
    ("4", "Mostrar registros"),
    ("5", "Buscar registros por valor"),
    ("6", "Filtrar registros por un criterio"),
    ("7", "Ordenar registros por un campo"),
    ("8", "Estadísticas de una columna numérica"),
    ("9", "Exportar informe (TXT y JSON)"),
    ("10", "Exportar el último resultado como CSV"),
    ("0", "Volver al menú principal"),
)

OPERATOR_MENU = (
    ("1", "=="),
    ("2", "!="),
    ("3", ">"),
    ("4", ">="),
    ("5", "<"),
    ("6", "<="),
    ("7", "contains"),
)

PREVIEW_ROWS = 10
PREVIEW_WORDS = 30
PREVIEW_LINES = 50
# Bubble sort es O(n²): con 2000 palabras hace como mucho ~2 millones de
# comparaciones, lo que todavía responde rápido. Con más, se usa una muestra.
BUBBLE_SORT_DEMO_LIMIT = 2000


class UserExit(Exception):
    """El usuario cerró la entrada estándar (Ctrl+D en Linux/macOS, Ctrl+Z en Windows)."""


# ---------------------------------------------------------------------------
# Entrada y salida básica
# ---------------------------------------------------------------------------


def read_input(prompt: str) -> str:
    """Lee una línea del usuario. Convierte el fin de entrada en ``UserExit``."""
    try:
        return input(prompt)
    except EOFError as error:
        raise UserExit from error


def times(count: int) -> str:
    """Devuelve "1 vez" o "N veces" según la cantidad."""
    return f"{count} vez" if count == 1 else f"{count} veces"


def print_title(title: str) -> None:
    """Muestra un título con una línea debajo."""
    print()
    print(title)
    print("-" * len(title))


def print_menu(title: str, options: tuple[tuple[str, str], ...]) -> None:
    """Muestra un menú numerado."""
    print_title(title)
    for key, label in options:
        print(f"  {key.rjust(2)}. {label}")


def option_keys(options: tuple[tuple[str, str], ...]) -> list[str]:
    """Devuelve las teclas válidas de un menú."""
    keys = []
    for key, _label in options:
        keys.append(key)
    return keys


def ask_menu_option(valid_options: list[str], prompt: str = "Elegí una opción: ") -> str:
    """Pide una opción hasta que el usuario escriba una válida."""
    while True:
        answer = read_input(prompt).strip()
        if answer in valid_options:
            return answer
        if answer == "":
            print("No escribiste ninguna opción.")
        else:
            print(f"Opción inválida: '{answer}'.")
        print(f"Opciones válidas: {', '.join(valid_options)}.")


def ask_text(prompt: str) -> Optional[str]:
    """Pide un texto. Devuelve None si el usuario deja la respuesta vacía (cancelar)."""
    answer = read_input(prompt).strip()
    if answer == "":
        return None
    return answer


def ask_positive_int(prompt: str, default: int, maximum: int) -> int:
    """Pide un entero entre 1 y ``maximum``. Enter acepta el valor por defecto."""
    while True:
        answer = read_input(prompt).strip()
        if answer == "":
            return default
        if not answer.isdigit():
            print(f"'{answer}' no es un número entero positivo.")
            continue
        number = int(answer)
        if number < 1 or number > maximum:
            print(f"Ingresá un número entre 1 y {maximum}.")
            continue
        return number


def ask_yes_no(prompt: str) -> bool:
    """Pide una respuesta s/n hasta que sea válida."""
    while True:
        answer = read_input(prompt).strip().lower()
        if answer in ("s", "si", "sí"):
            return True
        if answer in ("n", "no"):
            return False
        print("Respondé 's' (sí) o 'n' (no).")


def ask_column(headers: list[str], marks: Optional[dict[str, str]] = None) -> Optional[str]:
    """Muestra las columnas numeradas y pide una por número o por nombre.

    Args:
        headers: columnas disponibles.
        marks: texto opcional para mostrar junto a algunas columnas.

    Returns:
        El nombre de la columna elegida, o None si el usuario cancela.
    """
    if marks is None:
        marks = {}
    print("Columnas disponibles:")
    position = 0
    for header in headers:
        position += 1
        print(f"  {position}. {header}{marks.get(header, '')}")

    while True:
        answer = ask_text("Columna (número o nombre, Enter para cancelar): ")
        if answer is None:
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(headers):
            return headers[int(answer) - 1]
        for header in headers:
            if header.lower() == answer.lower():
                return header
        print(f"La columna '{answer}' no existe.")


def ask_file_path(kind_description: str) -> Optional[Path]:
    """Pide la ruta de un archivo. Devuelve None si el usuario cancela."""
    raw_path = ask_text(f"Ruta del archivo {kind_description} (Enter para cancelar): ")
    if raw_path is None:
        return None
    try:
        return resolve_input_path(raw_path)
    except FileAccessError as error:
        print(f"Error: {error}")
        return None


# ---------------------------------------------------------------------------
# Análisis de texto
# ---------------------------------------------------------------------------


def show_text_summary(text: str) -> None:
    """Muestra todas las métricas del texto."""
    print_title("Resumen general")
    print(report_generator.format_text_summary(analyzer.summarize_text(text)))


def show_most_common_words(text: str) -> None:
    """Pide cuántas palabras mostrar y muestra el ranking de frecuencias."""
    unique_count = len(text_analyzer.word_frequencies(text))
    if unique_count == 0:
        print("El texto no contiene palabras.")
        return
    default = min(analyzer.DEFAULT_TOP_WORDS, unique_count)
    limit = ask_positive_int(
        f"¿Cuántas palabras mostrar? (1-{unique_count}, Enter = {default}): ", default, unique_count
    )
    print_title(f"Las {limit} palabras más frecuentes")
    position = 0
    for word, count in text_analyzer.most_common_words(text, limit):
        position += 1
        print(f"  {position:>3}. {word} ({count})")


def search_word_in_text(text: str) -> None:
    """Indica si una palabra completa aparece y cuántas veces."""
    word = ask_text("Palabra a buscar (Enter para cancelar): ")
    if word is None:
        return
    try:
        normalized = text_analyzer.normalize_query(word)
        count = text_analyzer.count_word_occurrences(text, word)
    except ValueError as error:
        print(f"Error: {error}")
        return
    if count == 0:
        print(f"La palabra '{normalized}' no aparece en el texto.")
    else:
        print(f"La palabra '{normalized}' aparece {times(count)} (como palabra completa).")


def count_fragment_in_text(text: str) -> None:
    """Cuenta una secuencia exacta y la compara con el conteo de palabra completa."""
    fragment = read_input("Fragmento a contar (Enter para cancelar): ")
    if fragment.strip() == "":
        return
    occurrences = text_analyzer.count_substring_occurrences(text, fragment)
    print(f"La secuencia '{fragment}' aparece {times(occurrences)} (sin distinguir mayúsculas).")
    try:
        whole_words = text_analyzer.count_word_occurrences(text, fragment)
    except ValueError:
        return
    print(f"Como palabra completa aparece {times(whole_words)}.")
    if occurrences > whole_words:
        print("La diferencia corresponde a apariciones dentro de otras palabras.")


def show_lines_with_word(text: str) -> None:
    """Muestra las líneas (con su número) que contienen una palabra."""
    word = ask_text("Palabra a buscar (Enter para cancelar): ")
    if word is None:
        return
    try:
        matches = text_analyzer.find_lines_with_word(text, word)
    except ValueError as error:
        print(f"Error: {error}")
        return
    if len(matches) == 0:
        print("Ninguna línea contiene esa palabra.")
        return
    print_title(f"Líneas que contienen la palabra ({len(matches)})")
    for line_number, line in matches[:PREVIEW_LINES]:
        print(f"  Línea {line_number}: {line}")
    if len(matches) > PREVIEW_LINES:
        print(f"  ... y {len(matches) - PREVIEW_LINES} línea(s) más.")


def sort_words_demo(text: str) -> None:
    """Ordena las palabras distintas con bubble sort y con sorted() y compara."""
    unique_words = list(text_analyzer.word_frequencies(text).keys())
    if len(unique_words) == 0:
        print("El texto no contiene palabras.")
        return
    descending = ask_menu_option(["1", "2"], "Orden: 1 = A→Z, 2 = Z→A: ") == "2"

    sample = unique_words[:BUBBLE_SORT_DEMO_LIMIT]
    bubble_result, comparisons, swaps = sorting_algorithms.bubble_sort_with_stats(
        sample, key=sorting_algorithms.alphabetical_key, reverse=descending
    )
    builtin_result = sorting_algorithms.sort_alphabetically(sample, reverse=descending)

    print_title(f"Palabras distintas ordenadas ({len(sample)})")
    print("  " + ", ".join(bubble_result[:PREVIEW_WORDS]))
    if len(bubble_result) > PREVIEW_WORDS:
        print(f"  ... y {len(bubble_result) - PREVIEW_WORDS} palabra(s) más.")
    if len(unique_words) > BUBBLE_SORT_DEMO_LIMIT:
        print(
            f"Nota: el texto tiene {len(unique_words)} palabras distintas; bubble sort se aplicó "
            f"a las primeras {BUBBLE_SORT_DEMO_LIMIT} porque su costo crece como n²."
        )
    print()
    print(f"Bubble sort: {comparisons} comparaciones y {swaps} intercambios.")
    if bubble_result == builtin_result:
        print("El resultado coincide con sorted() (Timsort), la herramienta incorporada de Python.")
    else:
        print("ATENCIÓN: el resultado NO coincide con sorted().")


def compare_searches(text: str) -> None:
    """Compara búsqueda lineal y binaria sobre las palabras distintas del texto."""
    unique_words = list(text_analyzer.word_frequencies(text).keys())
    if len(unique_words) == 0:
        print("El texto no contiene palabras.")
        return
    word = ask_text("Palabra a buscar (Enter para cancelar): ")
    if word is None:
        return
    try:
        target = text_analyzer.normalize_query(word)
    except ValueError as error:
        print(f"Error: {error}")
        return

    result = search_algorithms.compare_search_methods(unique_words, target)
    print_title(f"Búsqueda de '{target}' entre {result['size']} palabras distintas")
    linear = result["linear"]
    binary = result["binary"]
    print(
        f"  Lineal (orden de aparición): {'encontrada' if linear['found'] else 'no encontrada'}, "
        f"{linear['steps']} elemento(s) inspeccionado(s)."
    )
    print(
        f"  Binaria (lista ordenada)   : {'encontrada' if binary['found'] else 'no encontrada'}, "
        f"{binary['steps']} elemento(s) inspeccionado(s)."
    )
    if not result["was_sorted"]:
        print(
            "  Para la búsqueda binaria primero se ordenó una copia con sorted() "
            "(costo O(n log n)), porque la binaria solo funciona con datos ordenados."
        )
    print("  Nota: se cuentan elementos inspeccionados, no tiempo de ejecución.")


def export_text_report(source: Path, text: str, reports_dir: Path) -> None:
    """Exporta el resumen del texto en TXT y JSON."""
    report = analyzer.build_text_report(source, text)
    export_and_print(report, reports_dir)


def export_and_print(report: dict, reports_dir: Path) -> None:
    """Exporta un informe y muestra dónde quedó guardado (o el error)."""
    try:
        paths = report_generator.export_report(report, reports_dir)
    except FileAccessError as error:
        print(f"Error al exportar: {error}")
        return
    print("Informe exportado:")
    for path in paths:
        print(f"  - {path}")


def run_text_menu(source: Path, text: str, reports_dir: Path) -> None:
    """Bucle del menú de análisis de texto."""
    if text.strip() == "":
        print("Aviso: el archivo está vacío. Los resultados serán 0.")
    keys = option_keys(TEXT_MENU)
    while True:
        print_menu(f"Análisis de texto — {source.name}", TEXT_MENU)
        option = ask_menu_option(keys)
        if option == "0":
            return
        if option == "1":
            show_text_summary(text)
        elif option == "2":
            show_most_common_words(text)
        elif option == "3":
            search_word_in_text(text)
        elif option == "4":
            count_fragment_in_text(text)
        elif option == "5":
            show_lines_with_word(text)
        elif option == "6":
            sort_words_demo(text)
        elif option == "7":
            compare_searches(text)
        elif option == "8":
            export_text_report(source, text, reports_dir)


# ---------------------------------------------------------------------------
# Análisis CSV
# ---------------------------------------------------------------------------


def show_records_preview(headers: list[str], records: list[dict]) -> None:
    """Muestra hasta ``PREVIEW_ROWS`` registros en forma de tabla."""
    print(report_generator.format_records_table(headers, records, max_rows=PREVIEW_ROWS))
    if len(records) > PREVIEW_ROWS:
        print(f"Mostrando {PREVIEW_ROWS} de {len(records)} registros.")
    else:
        print(f"{len(records)} registro(s).")


def show_csv_summary(table: dict) -> None:
    """Muestra el resumen completo del CSV."""
    print_title("Resumen del CSV")
    print(report_generator.format_csv_summary(analyzer.summarize_csv(table)))


def show_csv_issues(table: dict) -> None:
    """Muestra los problemas de formato detectados."""
    print_title("Problemas de formato")
    print(report_generator.format_issues(table["issues"]))


def show_empty_fields(table: dict) -> None:
    """Muestra cada campo vacío con su línea y columna."""
    empty_fields = csv_analyzer.find_empty_fields(table)
    print_title(f"Campos vacíos ({len(empty_fields)})")
    if len(empty_fields) == 0:
        print("  No hay campos vacíos.")
    for empty_field in empty_fields:
        print(f"  - Línea {empty_field['line']}, columna '{empty_field['column']}'")


def show_records(table: dict) -> None:
    """Muestra los primeros N registros que elija el usuario."""
    total = csv_analyzer.count_records(table)
    if total == 0:
        print("El archivo no tiene registros válidos.")
        return
    default = min(PREVIEW_ROWS, total)
    limit = ask_positive_int(f"¿Cuántos registros mostrar? (1-{total}, Enter = {default}): ", default, total)
    print(report_generator.format_records_table(table["headers"], table["records"], max_rows=limit))
    print(f"Mostrando {limit} de {total} registros.")


def search_csv_records(table: dict) -> Optional[list[dict]]:
    """Busca registros que contengan un valor. Devuelve los encontrados."""
    value = ask_text("Valor a buscar (Enter para cancelar): ")
    if value is None:
        return None
    in_one_column = ask_yes_no("¿Buscar solo en una columna? (s/n): ")
    column = None
    if in_one_column:
        column = ask_column(table["headers"])
        if column is None:
            return None
    try:
        matches = csv_analyzer.search_records(table, value, column)
    except ValueError as error:
        print(f"Error: {error}")
        return None
    print_title(f"Registros que contienen '{value}'")
    show_records_preview(table["headers"], matches)
    return matches


def filter_csv_records(table: dict) -> Optional[list[dict]]:
    """Filtra registros con un criterio columna-operador-valor."""
    column = ask_column(table["headers"])
    if column is None:
        return None
    print("Operadores:")
    for key, symbol in OPERATOR_MENU:
        print(f"  {key}. {symbol}")
    operator_key = ask_menu_option(option_keys(OPERATOR_MENU), "Operador: ")
    operator = dict(OPERATOR_MENU)[operator_key]
    value = read_input("Valor (para '==' o '!=' puede quedar vacío): ")
    try:
        result = csv_analyzer.filter_records(table, column, operator, value)
    except ValueError as error:
        print(f"Error: {error}")
        return None
    print_title(f"Filtro: {column} {operator} '{value.strip()}'")
    show_records_preview(table["headers"], result["records"])
    if result["skipped"] > 0:
        print(f"Se omitieron {result['skipped']} registro(s) cuyo valor no es un número válido.")
    return result["records"]


def sort_csv_records(table: dict) -> Optional[list[dict]]:
    """Ordena los registros por una columna elegida."""
    column = ask_column(table["headers"])
    if column is None:
        return None
    descending = ask_menu_option(["1", "2"], "Orden: 1 = ascendente, 2 = descendente: ") == "2"
    result = csv_analyzer.sort_records_by_field(table, column, descending)
    kind = "numérico" if result["numeric"] else "alfabético"
    print_title(f"Registros ordenados por '{column}' (orden {kind})")
    show_records_preview(table["headers"], result["records"])
    if result["moved_to_end"] > 0:
        print(f"{result['moved_to_end']} registro(s) con valor vacío o inválido quedaron al final.")
    return result["records"]


def show_column_statistics(table: dict) -> None:
    """Muestra estadísticas de una columna elegida por el usuario."""
    marks = {}
    for column in csv_analyzer.detect_numeric_columns(table):
        marks[column] = "  (numérica)"
    column = ask_column(table["headers"], marks)
    if column is None:
        return
    statistics = csv_analyzer.column_statistics(table, column)
    print_title("Estadísticas")
    print(report_generator.format_statistics(statistics))
    if statistics["valid_count"] == 0:
        print("La columna no tiene valores numéricos válidos.")


def export_last_result(
    table: dict, last_result: Optional[tuple[str, list[dict]]], source: Path, reports_dir: Path
) -> None:
    """Exporta como CSV el último resultado de búsqueda, filtro u orden."""
    if last_result is None:
        print("Todavía no hay resultados. Primero buscá, filtrá u ordená registros.")
        return
    label, records = last_result
    try:
        path = report_generator.export_records_to_csv(
            table["headers"], records, reports_dir, source.name, label
        )
    except FileAccessError as error:
        print(f"Error al exportar: {error}")
        return
    print(f"Se exportaron {len(records)} registro(s) en: {path}")


def run_csv_menu(source: Path, table: dict, reports_dir: Path) -> None:
    """Bucle del menú de análisis CSV."""
    if len(table["issues"]) > 0:
        print(f"Aviso: problemas de formato detectados: {len(table['issues'])} (ver opción 2).")
    last_result: Optional[tuple[str, list[dict]]] = None
    keys = option_keys(CSV_MENU)

    while True:
        print_menu(f"Análisis CSV — {source.name}", CSV_MENU)
        option = ask_menu_option(keys)
        if option == "0":
            return

        if option in ("4", "5", "6", "7", "8") and len(table["headers"]) == 0:
            print("El archivo no tiene encabezados ni registros para analizar.")
            continue

        if option == "1":
            show_csv_summary(table)
        elif option == "2":
            show_csv_issues(table)
        elif option == "3":
            show_empty_fields(table)
        elif option == "4":
            show_records(table)
        elif option == "5":
            records = search_csv_records(table)
            if records is not None:
                last_result = ("search", records)
        elif option == "6":
            records = filter_csv_records(table)
            if records is not None:
                last_result = ("filter", records)
        elif option == "7":
            records = sort_csv_records(table)
            if records is not None:
                last_result = ("sort", records)
        elif option == "8":
            show_column_statistics(table)
        elif option == "9":
            export_and_print(analyzer.build_csv_report(source, table), reports_dir)
        elif option == "10":
            export_last_result(table, last_result, source, reports_dir)


# ---------------------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------------------


def open_text_file(reports_dir: Path) -> None:
    """Pide un .txt, lo lee y abre su menú. Los errores no cierran el programa."""
    path = ask_file_path("de texto (por ejemplo samples/example.txt)")
    if path is None:
        return
    try:
        text = analyzer.load_text(path)
    except FileAccessError as error:
        print(f"Error: {error}")
        return
    run_text_menu(path, text, reports_dir)


def open_csv_file(reports_dir: Path) -> None:
    """Pide un .csv, lo interpreta y abre su menú."""
    path = ask_file_path("CSV (por ejemplo samples/inventory.csv)")
    if path is None:
        return
    try:
        table = analyzer.load_csv(path)
    except FileAccessError as error:
        print(f"Error: {error}")
        return
    except CsvFormatError as error:
        print(f"Error en el formato del CSV: {error}")
        return
    run_csv_menu(path, table, reports_dir)


def change_reports_dir(current: Path) -> Path:
    """Pide una nueva carpeta de informes. Devuelve la carpeta vigente."""
    print(f"Carpeta actual: {current}")
    answer = ask_text("Nueva carpeta (Enter para mantener la actual): ")
    if answer is None:
        return current
    new_dir = Path(answer.strip('"').strip("'")).expanduser().resolve()
    if new_dir.exists() and not new_dir.is_dir():
        print("Error: esa ruta corresponde a un archivo, no a una carpeta.")
        return current
    print(f"Los informes se guardarán en: {new_dir} (se creará al exportar si no existe).")
    return new_dir


def parse_arguments(argv: Optional[list[str]]) -> argparse.Namespace:
    """Interpreta los argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Analizador de archivos de texto (.txt) y datos (.csv) por consola."
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=DEFAULT_REPORTS_DIR,
        help="carpeta donde se guardan los informes (por defecto: reports/ del proyecto)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    """Punto de entrada. Devuelve el código de salida del programa."""
    arguments = parse_arguments(argv)
    reports_dir = arguments.reports_dir.expanduser().resolve()

    print("=" * 50)
    print(" Python Fundamentals & Algorithms")
    print(" Text and Data Analyzer")
    print("=" * 50)

    keys = option_keys(MAIN_MENU)
    try:
        while True:
            print_menu("Menú principal", MAIN_MENU)
            print(f"  (Informes en: {reports_dir})")
            option = ask_menu_option(keys)
            if option == "0":
                break
            if option == "1":
                open_text_file(reports_dir)
            elif option == "2":
                open_csv_file(reports_dir)
            elif option == "3":
                reports_dir = change_reports_dir(reports_dir)
    except (KeyboardInterrupt, UserExit):
        print("\nPrograma interrumpido por el usuario.")
        return 0

    print("¡Hasta luego!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
