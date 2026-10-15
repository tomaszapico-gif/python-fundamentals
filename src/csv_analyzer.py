"""Análisis de datos en formato CSV.

El módulo trabaja con el TEXTO del CSV (ya leído por ``file_handler``) y lo
convierte en una "tabla": un diccionario con estas claves:

- ``"headers"``: lista con los nombres de las columnas.
- ``"delimiter"``: separador detectado ("," ";" o tabulación).
- ``"records"``: lista de registros válidos; cada registro es un diccionario
  ``{columna: valor}`` con los valores sin espacios en los extremos.
- ``"record_lines"``: número de línea del archivo de cada registro, en el
  mismo orden que ``"records"`` (sirve para informar problemas).
- ``"issues"``: lista de problemas detectados, cada uno con ``"line"``,
  ``"type"`` y ``"message"``.

Políticas:
- La primera fila no vacía es la fila de encabezados. Un encabezado vacío o
  repetido es un error fatal (``CsvFormatError``), porque no se podría saber a
  qué columna pertenece cada valor.
- Una fila con una cantidad incorrecta de campos se EXCLUYE de los registros
  y se informa como problema ("field_count").
- Las filas totalmente vacías se ignoran y se informan ("blank_line").
- Los valores numéricos se validan al usarlos (estadísticas, filtros,
  orden), nunca se asume que son correctos.
- El número de línea informado es la línea física donde TERMINA el registro
  (un campo entre comillas puede ocupar varias líneas).
"""

from __future__ import annotations

import csv
import io
import math
from typing import Optional

from src.search_algorithms import find_records
from src.sorting_algorithms import sort_records

SUPPORTED_DELIMITERS = (",", ";", "\t")
NUMERIC_OPERATORS = (">", ">=", "<", "<=")
VALID_OPERATORS = ("==", "!=", ">", ">=", "<", "<=", "contains")


class CsvFormatError(ValueError):
    """El CSV tiene un problema que impide interpretarlo."""


def _make_issue(line: int, issue_type: str, message: str) -> dict:
    """Crea el diccionario que describe un problema de formato."""
    return {"line": line, "type": issue_type, "message": message}


def detect_delimiter(text: str) -> str:
    """Detecta el separador mirando la primera línea con contenido.

    Elige, entre coma, punto y coma y tabulación, el que más veces aparece.
    Si ninguno aparece, devuelve la coma. Excel en configuración regional
    de Argentina o España suele exportar con punto y coma.
    """
    first_line = ""
    for line in text.splitlines():
        if line.strip() != "":
            first_line = line
            break

    best_delimiter = ","
    best_count = 0
    for delimiter in SUPPORTED_DELIMITERS:
        count = first_line.count(delimiter)
        if count > best_count:
            best_delimiter = delimiter
            best_count = count
    return best_delimiter


def _is_blank_row(row: list[str]) -> bool:
    """Una fila es vacía si no tiene campos o todos sus campos están vacíos."""
    for value in row:
        if value.strip() != "":
            return False
    return True


def _validate_headers(row: list[str]) -> list[str]:
    """Limpia los encabezados y verifica que no estén vacíos ni repetidos.

    Raises:
        CsvFormatError: si hay un encabezado vacío o repetido.
    """
    headers: list[str] = []
    position = 0
    for raw_header in row:
        position += 1
        name = raw_header.replace("﻿", "").strip()
        if name == "":
            raise CsvFormatError(f"El encabezado de la columna {position} está vacío.")
        if name in headers:
            raise CsvFormatError(f"El encabezado '{name}' está repetido.")
        headers.append(name)
    return headers


def parse_csv_text(text: str, delimiter: Optional[str] = None) -> dict:
    """Convierte el texto de un CSV en una tabla (ver la descripción del módulo).

    Args:
        text: contenido completo del archivo CSV.
        delimiter: separador a usar. Si es None, se detecta automáticamente.

    Returns:
        La tabla con encabezados, registros válidos y problemas detectados.

    Raises:
        CsvFormatError: si los encabezados son inválidos o el módulo ``csv``
            no puede interpretar el contenido (por ejemplo, comillas mal
            cerradas).
    """
    if delimiter is None:
        delimiter = detect_delimiter(text)

    table: dict = {
        "headers": [],
        "delimiter": delimiter,
        "records": [],
        "record_lines": [],
        "issues": [],
    }

    if text.strip() == "":
        table["issues"].append(
            _make_issue(0, "empty_file", "El archivo está vacío: no tiene encabezados ni registros.")
        )
        return table

    reader = csv.reader(io.StringIO(text), delimiter=delimiter)
    headers: Optional[list[str]] = None

    try:
        for row in reader:
            line_number = reader.line_num

            if _is_blank_row(row):
                if headers is not None:
                    table["issues"].append(
                        _make_issue(line_number, "blank_line", "Fila vacía ignorada.")
                    )
                continue

            if headers is None:
                headers = _validate_headers(row)
                table["headers"] = headers
                continue

            if len(row) != len(headers):
                table["issues"].append(
                    _make_issue(
                        line_number,
                        "field_count",
                        f"Se esperaban {len(headers)} campos y se encontraron {len(row)}. "
                        "La fila se excluyó del análisis.",
                    )
                )
                continue

            record = {}
            for header, value in zip(headers, row):
                record[header] = value.strip()
            table["records"].append(record)
            table["record_lines"].append(line_number)
    except csv.Error as error:
        raise CsvFormatError(
            f"Error de formato CSV cerca de la línea {reader.line_num}: {error}"
        ) from error

    return table


def count_records(table: dict) -> int:
    """Devuelve la cantidad de registros válidos (sin contar encabezados)."""
    return len(table["records"])


def require_column(table: dict, column: str) -> None:
    """Verifica que la columna exista en la tabla.

    Raises:
        ValueError: si la columna no existe, con la lista de columnas válidas.
    """
    if column not in table["headers"]:
        available = ", ".join(table["headers"]) if table["headers"] else "(ninguna)"
        raise ValueError(f"La columna '{column}' no existe. Columnas disponibles: {available}.")


def find_empty_fields(table: dict) -> list[dict]:
    """Lista los campos vacíos como ``{"line": n, "column": nombre}``."""
    empty_fields = []
    for index in range(len(table["records"])):
        record = table["records"][index]
        line = table["record_lines"][index]
        for header in table["headers"]:
            if record[header] == "":
                empty_fields.append({"line": line, "column": header})
    return empty_fields


def count_empty_fields_by_column(table: dict) -> dict[str, int]:
    """Cuenta los campos vacíos de cada columna (incluye columnas con 0)."""
    counts = {}
    for header in table["headers"]:
        counts[header] = 0
    for empty_field in find_empty_fields(table):
        counts[empty_field["column"]] += 1
    return counts


def parse_number(raw_value: str) -> float:
    """Convierte un texto en número de forma estricta.

    Formatos aceptados: "12", "-3", "12.5" y "12,5" (coma decimal).
    Formatos rechazados, para no adivinar: separadores de miles ("1.234,50"
    o "1,234.5"), más de una coma, guiones bajos ("1_000"), "nan" e "inf".

    Raises:
        ValueError: si el texto no representa un número válido.
    """
    cleaned = raw_value.strip()
    if cleaned == "":
        raise ValueError("El valor está vacío.")
    if "_" in cleaned:
        raise ValueError(f"'{raw_value}' no es un número válido.")

    if "," in cleaned:
        if "." in cleaned or cleaned.count(",") > 1:
            raise ValueError(f"'{raw_value}' es ambiguo: no se admiten separadores de miles.")
        cleaned = cleaned.replace(",", ".")

    try:
        number = float(cleaned)
    except ValueError:
        raise ValueError(f"'{raw_value}' no es un número válido.") from None

    if not math.isfinite(number):
        raise ValueError(f"'{raw_value}' no es un número finito.")
    return number


def _classify_column_values(table: dict, column: str) -> tuple[list[float], int, list[dict]]:
    """Separa los valores de una columna en números válidos, vacíos e inválidos.

    Returns:
        ``(números_válidos, cantidad_de_vacíos, inválidos)``, donde cada
        inválido es ``{"line": n, "value": texto}``.
    """
    numbers = []
    empty_count = 0
    invalid_values = []
    for index in range(len(table["records"])):
        raw_value = table["records"][index][column]
        if raw_value == "":
            empty_count += 1
            continue
        try:
            numbers.append(parse_number(raw_value))
        except ValueError:
            invalid_values.append({"line": table["record_lines"][index], "value": raw_value})
    return numbers, empty_count, invalid_values


def is_mostly_numeric(table: dict, column: str) -> bool:
    """Indica si una columna es "probablemente numérica".

    Criterio: tiene al menos un número válido y hay MÁS valores numéricos
    válidos que valores no numéricos (los vacíos no se cuentan).
    """
    require_column(table, column)
    numbers, _empty_count, invalid_values = _classify_column_values(table, column)
    return len(numbers) > 0 and len(numbers) > len(invalid_values)


def detect_numeric_columns(table: dict) -> list[str]:
    """Devuelve las columnas que ``is_mostly_numeric`` considera numéricas."""
    numeric_columns = []
    for header in table["headers"]:
        if is_mostly_numeric(table, header):
            numeric_columns.append(header)
    return numeric_columns


def _median(values: list[float]) -> float:
    """Calcula la mediana de una lista NO vacía."""
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def column_statistics(table: dict, column: str) -> dict:
    """Calcula estadísticas básicas de una columna numérica.

    Los valores vacíos e inválidos se excluyen del cálculo pero se informan.
    Si no hay ningún número válido, mínimo, máximo, suma, promedio y mediana
    valen None.

    Returns:
        Diccionario con ``column``, ``valid_count``, ``empty_count``,
        ``invalid_count``, ``invalid_values``, ``minimum``, ``maximum``,
        ``total``, ``mean`` y ``median``.

    Raises:
        ValueError: si la columna no existe.
    """
    require_column(table, column)
    numbers, empty_count, invalid_values = _classify_column_values(table, column)

    statistics: dict = {
        "column": column,
        "valid_count": len(numbers),
        "empty_count": empty_count,
        "invalid_count": len(invalid_values),
        "invalid_values": invalid_values,
        "minimum": None,
        "maximum": None,
        "total": None,
        "mean": None,
        "median": None,
    }
    if len(numbers) == 0:
        return statistics

    minimum = numbers[0]
    maximum = numbers[0]
    total = 0.0
    for number in numbers:
        if number < minimum:
            minimum = number
        if number > maximum:
            maximum = number
        total += number

    statistics["minimum"] = minimum
    statistics["maximum"] = maximum
    statistics["total"] = total
    statistics["mean"] = total / len(numbers)
    statistics["median"] = _median(numbers)
    return statistics


def search_records(table: dict, value: str, column: Optional[str] = None) -> list[dict]:
    """Busca registros que CONTENGAN ``value`` (sin distinguir mayúsculas).

    Args:
        table: tabla devuelta por ``parse_csv_text``.
        value: texto buscado.
        column: si se indica, busca solo en esa columna; si es None, busca en
            todas y devuelve cada registro una sola vez.

    Raises:
        ValueError: si ``value`` está vacío o la columna no existe.
    """
    query = value.strip()
    if query == "":
        raise ValueError("El valor a buscar no puede estar vacío.")

    if column is not None:
        require_column(table, column)
        return find_records(table["records"], column, query)

    lowered_query = query.lower()
    matches = []
    for record in table["records"]:
        for header in table["headers"]:
            if lowered_query in record[header].lower():
                matches.append(record)
                break
    return matches


def _values_are_equal(field_value: str, query: str) -> bool:
    """Compara como números si ambos lo son ("10" == "10.0"); si no, como texto."""
    try:
        return parse_number(field_value) == parse_number(query)
    except ValueError:
        return field_value.strip().lower() == query.strip().lower()


def _compare_numbers(left: float, operator: str, right: float) -> bool:
    """Aplica un operador de comparación numérica (sin usar eval)."""
    if operator == ">":
        return left > right
    if operator == ">=":
        return left >= right
    if operator == "<":
        return left < right
    if operator == "<=":
        return left <= right
    raise ValueError(f"Operador numérico desconocido: '{operator}'.")


def filter_records(table: dict, column: str, operator: str, value: str) -> dict:
    """Filtra registros según un criterio simple ``columna operador valor``.

    Operadores:
        - ``==`` y ``!=``: igualdad. Si ambos lados son números, se comparan
          como números; si no, como texto sin distinguir mayúsculas. Con un
          valor vacío permiten encontrar campos vacíos.
        - ``>``, ``>=``, ``<``, ``<=``: comparación numérica. Los registros
          cuyo campo no es un número válido se omiten y se cuentan.
        - ``contains``: el campo contiene el texto (sin distinguir mayúsculas).

    Returns:
        ``{"records": [...], "skipped": n}``, donde ``skipped`` es la cantidad
        de registros omitidos por no tener un número válido.

    Raises:
        ValueError: si la columna no existe, el operador no es válido, el valor
            no es numérico para un operador numérico o está vacío con ``contains``.
    """
    require_column(table, column)
    if operator not in VALID_OPERATORS:
        raise ValueError(
            f"Operador inválido: '{operator}'. Operadores válidos: {', '.join(VALID_OPERATORS)}."
        )

    query = value.strip()
    numeric_query = 0.0
    if operator in NUMERIC_OPERATORS:
        try:
            numeric_query = parse_number(query)
        except ValueError:
            raise ValueError(
                f"Para el operador '{operator}' el valor debe ser numérico y se recibió '{value}'."
            ) from None
    if operator == "contains" and query == "":
        raise ValueError("Para el operador 'contains' el valor no puede estar vacío.")

    matches = []
    skipped = 0
    for record in table["records"]:
        field_value = record[column]

        if operator == "contains":
            if query.lower() in field_value.lower():
                matches.append(record)
        elif operator == "==":
            if _values_are_equal(field_value, query):
                matches.append(record)
        elif operator == "!=":
            if not _values_are_equal(field_value, query):
                matches.append(record)
        else:
            try:
                field_number = parse_number(field_value)
            except ValueError:
                skipped += 1
                continue
            if _compare_numbers(field_number, operator, numeric_query):
                matches.append(record)

    return {"records": matches, "skipped": skipped}


def sort_records_by_field(table: dict, column: str, descending: bool = False) -> dict:
    """Ordena los registros por una columna.

    Si la columna es probablemente numérica (ver ``is_mostly_numeric``), se
    ordena por valor numérico; si no, alfabéticamente. Los registros con
    valores vacíos o inválidos quedan al final.

    Returns:
        ``{"records": [...], "numeric": bool, "moved_to_end": n}``.

    Raises:
        ValueError: si la columna no existe.
    """
    require_column(table, column)
    numeric = is_mostly_numeric(table, column)
    converter = parse_number if numeric else None
    sorted_records, moved_to_end = sort_records(table["records"], column, descending, converter)
    return {"records": sorted_records, "numeric": numeric, "moved_to_end": moved_to_end}
