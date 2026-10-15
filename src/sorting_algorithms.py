"""Algoritmos de ordenamiento.

Este módulo contiene:

- ``bubble_sort`` y ``bubble_sort_with_stats``: implementación MANUAL de
  bubble sort con fines educativos. Su costo es O(n²) en el peor caso, por lo
  que no se recomienda para ordenar grandes volúmenes de datos.
- ``alphabetical_key`` y ``sort_alphabetically``: orden alfabético pensado
  para texto en español (las tildes no alteran el orden y la "ñ" va después
  de la "n").
- ``sort_by_frequency``: ordena pares (palabra, frecuencia).
- ``sort_records``: ordena registros (diccionarios) por un campo elegido.

Salvo bubble sort, las funciones usan ``sorted()``, que en CPython implementa
Timsort (O(n log n) en el peor caso). Ver ``docs/ALGORITHMS.md``.
"""

from __future__ import annotations

import unicodedata
from typing import Any, Callable, Iterable, Optional

# Carácter con un código Unicode muy alto. Se coloca después de la "n" en la
# clave de ordenamiento para que la "ñ" quede entre la "n" y la "o", como en el
# alfabeto español. Solo se usa para comparar: el texto original no cambia.
ENYE_SORT_MARKER = "￿"


def _identity(value: Any) -> Any:
    """Devuelve el mismo valor recibido. Es la clave por defecto de bubble sort."""
    return value


def bubble_sort_with_stats(
    items: Iterable[Any],
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
) -> tuple[list[Any], int, int]:
    """Ordena con bubble sort y cuenta comparaciones e intercambios.

    Funcionamiento: se recorre la lista comparando cada par de elementos
    vecinos; si están en el orden incorrecto se intercambian. Al terminar cada
    pasada, el elemento "más grande" quedó al final (como una burbuja que
    sube), así que la pasada siguiente puede revisar un elemento menos. Si en
    una pasada no hubo intercambios, la lista ya está ordenada y se corta.

    Args:
        items: elementos a ordenar. No se modifican; se trabaja sobre una copia.
        key: función opcional que obtiene el valor a comparar de cada elemento.
        reverse: si es True, ordena de mayor a menor.

    Returns:
        Una tupla ``(lista_ordenada, comparaciones, intercambios)``.

    Complejidad: O(n²) comparaciones en el peor caso y en el caso promedio;
    O(n) en el mejor caso (lista ya ordenada) gracias al corte temprano.
    Es estable: elementos con la misma clave conservan su orden original.
    """
    result = list(items)
    if key is None:
        key = _identity

    comparisons = 0
    swaps = 0
    length = len(result)

    for pass_number in range(length - 1):
        swapped = False
        # Los últimos `pass_number` elementos ya están en su posición final.
        for index in range(length - 1 - pass_number):
            comparisons += 1
            left_value = key(result[index])
            right_value = key(result[index + 1])

            # Solo se intercambia si el orden es estrictamente incorrecto;
            # así los elementos iguales no cambian de lugar (estabilidad).
            if reverse:
                out_of_order = left_value < right_value
            else:
                out_of_order = left_value > right_value

            if out_of_order:
                result[index], result[index + 1] = result[index + 1], result[index]
                swaps += 1
                swapped = True

        if not swapped:
            break

    return result, comparisons, swaps


def bubble_sort(
    items: Iterable[Any],
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
) -> list[Any]:
    """Devuelve una nueva lista ordenada con bubble sort.

    Es un atajo de ``bubble_sort_with_stats`` para cuando no interesan las
    estadísticas. Ver esa función para el detalle del algoritmo.
    """
    sorted_items, _comparisons, _swaps = bubble_sort_with_stats(items, key, reverse)
    return sorted_items


def alphabetical_key(text: str) -> tuple[str, str]:
    """Construye una clave para ordenar texto alfabéticamente en español.

    La comparación normal de strings en Python usa el código Unicode de cada
    carácter, y por eso "árbol" quedaría después de "zapato". Esta clave:

    1. Normaliza a NFC y pasa a minúsculas.
    2. Quita las tildes y diéresis solo para comparar ("á" -> "a").
    3. Mantiene la "ñ" como letra propia, ubicada entre la "n" y la "o".

    El segundo elemento de la tupla es el texto original y sirve para
    desempatar de forma determinista (por ejemplo "arbol" y "árbol").

    Args:
        text: palabra o frase a convertir en clave.

    Returns:
        Una tupla ``(texto_base, texto_original)``.
    """
    base_characters = []
    for character in unicodedata.normalize("NFC", text).lower():
        if character == "ñ":
            base_characters.append("n" + ENYE_SORT_MARKER)
            continue
        # NFD separa la letra base de su tilde: "á" -> "a" + "´".
        for part in unicodedata.normalize("NFD", character):
            if not unicodedata.combining(part):
                base_characters.append(part)
    return "".join(base_characters), text


def sort_alphabetically(words: Iterable[str], reverse: bool = False) -> list[str]:
    """Ordena palabras alfabéticamente usando ``alphabetical_key``.

    Usa ``sorted()`` (Timsort, O(n log n)). Devuelve una lista nueva.
    """
    return sorted(words, key=alphabetical_key, reverse=reverse)


def _frequency_sort_key(item: tuple[str, int]) -> tuple[int, tuple[str, str]]:
    """Clave para ordenar (palabra, frecuencia): mayor frecuencia primero.

    Se usa ``-count`` para que el orden ascendente de ``sorted()`` deje
    primero las frecuencias más altas. Los empates se resuelven por orden
    alfabético.
    """
    word, count = item
    return -count, alphabetical_key(word)


def sort_by_frequency(frequencies: dict[str, int]) -> list[tuple[str, int]]:
    """Ordena un diccionario ``{palabra: frecuencia}`` de mayor a menor.

    Ejemplo: ``{"b": 1, "a": 3, "c": 1}`` -> ``[("a", 3), ("b", 1), ("c", 1)]``.

    Complejidad: O(k log k), donde k es la cantidad de palabras distintas.
    """
    return sorted(frequencies.items(), key=_frequency_sort_key)


def _entry_value(entry: tuple[Any, dict]) -> Any:
    """Devuelve el valor de comparación de un par (valor, registro)."""
    return entry[0]


def sort_records(
    records: Iterable[dict],
    field: str,
    descending: bool = False,
    value_converter: Optional[Callable[[str], Any]] = None,
) -> tuple[list[dict], int]:
    """Ordena registros (diccionarios) según el valor de un campo.

    Política para datos problemáticos: los registros cuyo campo falta, está
    vacío o no puede convertirse (``value_converter`` lanza ``ValueError``) se
    ubican AL FINAL, en su orden original, tanto en orden ascendente como
    descendente. Así nunca se mezclan con los valores válidos.

    Args:
        records: registros a ordenar. No se modifican.
        field: nombre del campo por el cual ordenar.
        descending: si es True, ordena de mayor a menor.
        value_converter: función que convierte el texto del campo en un valor
            comparable (por ejemplo, un número). Si se omite, se usa
            ``alphabetical_key``.

    Returns:
        Una tupla ``(registros_ordenados, cantidad_ubicada_al_final)``.

    Complejidad: O(n log n) por el uso de ``sorted()``.
    """
    if value_converter is None:
        value_converter = alphabetical_key

    sortable_entries = []
    unsortable_records = []

    for record in records:
        raw_value = record.get(field)
        if raw_value is None or raw_value.strip() == "":
            unsortable_records.append(record)
            continue
        try:
            value = value_converter(raw_value)
        except ValueError:
            unsortable_records.append(record)
            continue
        sortable_entries.append((value, record))

    # Se ordena solo por el valor (no por el diccionario), y sorted() es
    # estable: los registros con el mismo valor conservan su orden original.
    sorted_entries = sorted(sortable_entries, key=_entry_value, reverse=descending)

    sorted_records = []
    for _value, record in sorted_entries:
        sorted_records.append(record)

    return sorted_records + unsortable_records, len(unsortable_records)
