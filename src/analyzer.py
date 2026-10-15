"""Coordinación entre archivos, análisis e informes.

``main.py`` (la interfaz) no debería saber cómo se lee un archivo ni cómo se
arma un resumen. Este módulo ofrece operaciones de "alto nivel" que combinan:

    file_handler (leer)  ->  text_analyzer / csv_analyzer (analizar)
                         ->  report_generator (armar el informe)

Gracias a esta capa, el flujo completo se puede probar sin la consola
(ver ``tests/test_analyzer.py``).
"""

from __future__ import annotations

from pathlib import Path

from src import csv_analyzer, text_analyzer
from src.file_handler import PathLike, read_text_file, validate_extension
from src.report_generator import create_report

TEXT_EXTENSIONS = (".txt",)
CSV_EXTENSIONS = (".csv",)
DEFAULT_TOP_WORDS = 10


def load_text(path: PathLike) -> str:
    """Valida la extensión y lee un archivo de texto.

    Raises:
        FileAccessError: si la extensión no es .txt o el archivo no se puede leer.
    """
    validate_extension(path, TEXT_EXTENSIONS)
    return read_text_file(path)


def summarize_text(text: str, top_n: int = DEFAULT_TOP_WORDS) -> dict:
    """Reúne todas las métricas de texto en un diccionario.

    El promedio se redondea a 2 decimales para el informe.
    """
    shortest, longest = text_analyzer.shortest_and_longest_words(text)
    most_common = []
    for word, count in text_analyzer.most_common_words(text, top_n):
        most_common.append({"word": word, "count": count})

    return {
        "characters": text_analyzer.count_characters(text),
        "characters_without_whitespace": text_analyzer.count_characters_without_whitespace(text),
        "words": text_analyzer.count_words(text),
        "unique_words": len(text_analyzer.word_frequencies(text)),
        "lines": text_analyzer.count_lines(text),
        "empty_lines": text_analyzer.count_empty_lines(text),
        "average_word_length": round(text_analyzer.average_word_length(text), 2),
        "shortest_word": shortest,
        "longest_word": longest,
        "most_common_words": most_common,
    }


def build_text_report(source: PathLike, text: str, top_n: int = DEFAULT_TOP_WORDS) -> dict:
    """Arma el informe de un texto ya leído."""
    return create_report("text", Path(source).name, summarize_text(text, top_n))


def analyze_text_file(path: PathLike, top_n: int = DEFAULT_TOP_WORDS) -> dict:
    """Lee un .txt y devuelve su informe completo."""
    text = load_text(path)
    return build_text_report(path, text, top_n)


def load_csv(path: PathLike) -> dict:
    """Valida la extensión, lee el archivo e interpreta el CSV.

    Raises:
        FileAccessError: si la extensión no es .csv o el archivo no se puede leer.
        CsvFormatError: si el contenido no se puede interpretar como CSV.
    """
    validate_extension(path, CSV_EXTENSIONS)
    return csv_analyzer.parse_csv_text(read_text_file(path))


def _rounded(value):
    """Redondea a 2 decimales si el valor es un número; deja None como está."""
    if value is None:
        return None
    return round(value, 2)


def summarize_csv(table: dict) -> dict:
    """Reúne la información general de una tabla CSV en un diccionario."""
    malformed_rows = 0
    for issue in table["issues"]:
        if issue["type"] == "field_count":
            malformed_rows += 1

    empty_by_column = csv_analyzer.count_empty_fields_by_column(table)
    total_empty = 0
    for count in empty_by_column.values():
        total_empty += count

    numeric_columns = []
    for column in csv_analyzer.detect_numeric_columns(table):
        statistics = csv_analyzer.column_statistics(table, column)
        for key in ("minimum", "maximum", "total", "mean", "median"):
            statistics[key] = _rounded(statistics[key])
        numeric_columns.append(statistics)

    return {
        "delimiter": table["delimiter"],
        "headers": list(table["headers"]),
        "column_count": len(table["headers"]),
        "record_count": csv_analyzer.count_records(table),
        "malformed_rows": malformed_rows,
        "issues": list(table["issues"]),
        "empty_fields_by_column": empty_by_column,
        "total_empty_fields": total_empty,
        "numeric_columns": numeric_columns,
    }


def build_csv_report(source: PathLike, table: dict) -> dict:
    """Arma el informe de una tabla CSV ya interpretada."""
    return create_report("csv", Path(source).name, summarize_csv(table))


def analyze_csv_file(path: PathLike) -> dict:
    """Lee un .csv y devuelve su informe completo."""
    table = load_csv(path)
    return build_csv_report(path, table)
