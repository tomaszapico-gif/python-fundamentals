"""Construcción y exportación de informes.

Un "informe" es un diccionario con esta forma:

    {
        "report_type": "text" o "csv",
        "source_file": "example.txt",       # solo el nombre, sin carpetas
        "generated_at": "2026-10-15T17:36:00",
        "data": { ... resumen del análisis ... },
    }

Se guarda solo el NOMBRE del archivo analizado (no la ruta completa) para no
filtrar la estructura de carpetas del usuario si el informe se comparte.

Este módulo sabe dar formato (texto legible, JSON, tabla, CSV) y delega la
escritura en ``file_handler``.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from src.file_handler import PathLike, write_new_text_file

REPORT_TYPES = ("text", "csv")
EXPORT_FORMATS = ("txt", "json")
SEPARATOR = "=" * 60

TEXT_SUMMARY_LABELS = (
    ("characters", "Caracteres (incluye espacios y saltos de línea)"),
    ("characters_without_whitespace", "Caracteres sin espacios en blanco"),
    ("words", "Palabras"),
    ("unique_words", "Palabras distintas"),
    ("lines", "Líneas"),
    ("empty_lines", "Líneas vacías"),
    ("average_word_length", "Longitud promedio de palabra"),
    ("shortest_word", "Palabra más corta"),
    ("longest_word", "Palabra más larga"),
)


def create_report(report_type: str, source_name: str, data: dict) -> dict:
    """Arma el diccionario de informe con fecha y hora de generación.

    Raises:
        ValueError: si ``report_type`` no es "text" ni "csv".
    """
    if report_type not in REPORT_TYPES:
        raise ValueError(f"Tipo de informe desconocido: '{report_type}'.")
    return {
        "report_type": report_type,
        "source_file": source_name,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "data": data,
    }


def format_number(value: Optional[float]) -> str:
    """Muestra números de forma legible: enteros sin decimales, el resto con 2.

    ``None`` se muestra como "N/D" (no disponible).
    """
    if value is None:
        return "N/D"
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}"


def format_text_summary(summary: dict) -> str:
    """Convierte el resumen de un análisis de texto en líneas legibles."""
    label_width = 0
    for _key, label in TEXT_SUMMARY_LABELS:
        label_width = max(label_width, len(label))

    lines = []
    for key, label in TEXT_SUMMARY_LABELS:
        value = summary[key]
        if value is None:
            shown = "(no hay palabras)"
        elif isinstance(value, float):
            shown = format_number(value)
        else:
            shown = str(value)
        lines.append(f"{label.ljust(label_width)} : {shown}")

    lines.append("")
    lines.append("Palabras más frecuentes:")
    if len(summary["most_common_words"]) == 0:
        lines.append("  (no hay palabras)")
    position = 0
    for item in summary["most_common_words"]:
        position += 1
        lines.append(f"  {position:>3}. {item['word']} ({item['count']})")
    return "\n".join(lines)


def format_issues(issues: list[dict]) -> str:
    """Lista los problemas de formato de un CSV, uno por línea."""
    if len(issues) == 0:
        return "  No se detectaron problemas de formato."
    lines = []
    for issue in issues:
        if issue["line"] > 0:
            lines.append(f"  - Línea {issue['line']}: {issue['message']}")
        else:
            lines.append(f"  - {issue['message']}")
    return "\n".join(lines)


def format_statistics(statistics: dict) -> str:
    """Convierte las estadísticas de una columna en texto legible."""
    lines = [
        f"Columna: {statistics['column']}",
        f"  Valores numéricos válidos : {statistics['valid_count']}",
        f"  Valores vacíos            : {statistics['empty_count']}",
        f"  Valores no numéricos      : {statistics['invalid_count']}",
        f"  Mínimo                    : {format_number(statistics['minimum'])}",
        f"  Máximo                    : {format_number(statistics['maximum'])}",
        f"  Suma                      : {format_number(statistics['total'])}",
        f"  Promedio                  : {format_number(statistics['mean'])}",
        f"  Mediana                   : {format_number(statistics['median'])}",
    ]
    for invalid in statistics["invalid_values"]:
        lines.append(f"  ! Línea {invalid['line']}: '{invalid['value']}' no es un número válido")
    return "\n".join(lines)


def format_csv_summary(summary: dict) -> str:
    """Convierte el resumen de un análisis CSV en texto legible."""
    delimiter_names = {",": "coma", ";": "punto y coma", "\t": "tabulación"}
    delimiter_name = delimiter_names.get(summary["delimiter"], repr(summary["delimiter"]))
    headers_text = ", ".join(summary["headers"]) if summary["headers"] else "(ninguno)"

    lines = [
        f"Separador detectado    : {delimiter_name}",
        f"Encabezados ({summary['column_count']})        : {headers_text}",
        f"Registros válidos      : {summary['record_count']}",
        f"Filas mal formadas     : {summary['malformed_rows']}",
        f"Campos vacíos (total)  : {summary['total_empty_fields']}",
        "",
        "Problemas de formato:",
        format_issues(summary["issues"]),
        "",
        "Campos vacíos por columna:",
    ]
    if len(summary["empty_fields_by_column"]) == 0:
        lines.append("  (sin columnas)")
    for column, count in summary["empty_fields_by_column"].items():
        lines.append(f"  - {column}: {count}")

    lines.append("")
    lines.append("Estadísticas de columnas numéricas:")
    if len(summary["numeric_columns"]) == 0:
        lines.append("  No se detectaron columnas numéricas.")
    for statistics in summary["numeric_columns"]:
        lines.append(format_statistics(statistics))
    return "\n".join(lines)


def format_report_as_text(report: dict) -> str:
    """Genera el contenido de un informe en texto plano (.txt)."""
    if report["report_type"] == "text":
        title = "INFORME DE ANÁLISIS DE TEXTO"
        body = format_text_summary(report["data"])
    else:
        title = "INFORME DE ANÁLISIS CSV"
        body = format_csv_summary(report["data"])

    lines = [
        SEPARATOR,
        title,
        SEPARATOR,
        f"Archivo analizado: {report['source_file']}",
        f"Generado: {report['generated_at']}",
        SEPARATOR,
        body,
        "",
    ]
    return "\n".join(lines)


def format_report_as_json(report: dict) -> str:
    """Genera el contenido de un informe en JSON (UTF-8 legible, con sangría)."""
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def _truncate(value: str, max_width: int) -> str:
    """Recorta un texto largo y agrega "…" para que entre en una columna."""
    if len(value) <= max_width:
        return value
    return value[: max_width - 1] + "…"


def format_records_table(
    headers: list[str],
    records: list[dict],
    max_rows: Optional[int] = None,
    max_column_width: int = 18,
) -> str:
    """Muestra registros como una tabla de texto con columnas alineadas.

    Args:
        headers: columnas a mostrar, en orden.
        records: registros a mostrar.
        max_rows: cantidad máxima de filas (None = todas).
        max_column_width: ancho máximo de cada columna; los valores más
            largos se recortan con "…".
    """
    if len(records) == 0:
        return "(sin registros)"

    visible_records = records if max_rows is None else records[:max_rows]

    widths = []
    for header in headers:
        width = len(_truncate(header, max_column_width))
        for record in visible_records:
            value = _truncate(record.get(header, ""), max_column_width)
            width = max(width, len(value))
        widths.append(width)

    def build_row(values: list[str]) -> str:
        cells = []
        for index in range(len(values)):
            cells.append(_truncate(values[index], max_column_width).ljust(widths[index]))
        return " | ".join(cells).rstrip()

    lines = [build_row(headers)]
    separator_parts = []
    for width in widths:
        separator_parts.append("-" * width)
    lines.append("-+-".join(separator_parts))
    for record in visible_records:
        row_values = []
        for header in headers:
            row_values.append(record.get(header, ""))
        lines.append(build_row(row_values))
    return "\n".join(lines)


def records_to_csv_text(headers: list[str], records: list[dict]) -> str:
    """Convierte registros en texto CSV (separado por comas, con encabezados).

    Se usa "\\n" como fin de línea; al escribir el archivo, Python lo adapta
    al sistema operativo.
    """
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=headers, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for record in records:
        writer.writerow(record)
    return buffer.getvalue()


def safe_file_stem(name: str) -> str:
    """Convierte un nombre de archivo en un fragmento seguro para otro nombre.

    Toma el nombre sin extensión y reemplaza todo lo que no sea letra, dígito,
    guion o guion bajo por "_". Ejemplo: "mi informe (v2).txt" -> "mi_informe__v2_".
    """
    stem = Path(name).stem
    characters = []
    for character in stem:
        if character.isalnum() or character in "-_":
            characters.append(character)
        else:
            characters.append("_")
    cleaned = "".join(characters)
    return cleaned if cleaned else "archivo"


def build_report_filename(
    source_name: str, report_type: str, extension: str, moment: Optional[datetime] = None
) -> str:
    """Construye un nombre de archivo descriptivo con fecha y hora.

    Ejemplo: ``text_report_example_20261015-173600.txt``.
    """
    if moment is None:
        moment = datetime.now()
    timestamp = moment.strftime("%Y%m%d-%H%M%S")
    return f"{report_type}_report_{safe_file_stem(source_name)}_{timestamp}.{extension}"


def export_report(
    report: dict, output_dir: PathLike, formats: Iterable[str] = EXPORT_FORMATS
) -> list[Path]:
    """Guarda el informe en los formatos pedidos y devuelve las rutas creadas.

    Los formatos se validan ANTES de escribir, para no dejar exportaciones a
    medias. Nunca sobrescribe archivos (ver ``write_new_text_file``).

    Raises:
        ValueError: si algún formato no es "txt" ni "json".
        FileAccessError: si no se puede escribir en ``output_dir``.
    """
    requested = list(formats)
    for export_format in requested:
        if export_format not in EXPORT_FORMATS:
            raise ValueError(f"Formato de exportación no soportado: '{export_format}'.")

    moment = datetime.now()
    created_paths = []
    for export_format in requested:
        if export_format == "txt":
            content = format_report_as_text(report)
        else:
            content = format_report_as_json(report)
        filename = build_report_filename(
            report["source_file"], report["report_type"], export_format, moment
        )
        created_paths.append(write_new_text_file(output_dir, filename, content))
    return created_paths


def export_records_to_csv(
    headers: list[str], records: list[dict], output_dir: PathLike, source_name: str, label: str
) -> Path:
    """Guarda registros (por ejemplo, el resultado de un filtro) en un CSV nuevo.

    Args:
        label: palabra que describe el resultado ("search", "filter", "sort").
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{safe_file_stem(label)}_{safe_file_stem(source_name)}_{timestamp}.csv"
    return write_new_text_file(output_dir, filename, records_to_csv_text(headers, records))
