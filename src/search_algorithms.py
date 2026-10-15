"""Algoritmos de búsqueda.

- Búsqueda lineal: revisa los elementos uno por uno. Funciona con cualquier
  colección (ordenada o no). Costo O(n).
- Búsqueda binaria: divide el rango a la mitad en cada paso. Es O(log n),
  pero SOLO es correcta si los datos están ordenados con el mismo criterio
  que se usa para comparar.

Las versiones ``*_with_steps`` cuentan cuántos elementos se inspeccionaron.
Contar pasos (en lugar de medir tiempo) da resultados reproducibles y sirve
para comparar algoritmos en la guía didáctica.
"""

from __future__ import annotations

from typing import Any, Sequence


def linear_search_with_steps(items: Sequence[Any], target: Any) -> tuple[int, int]:
    """Busca ``target`` recorriendo ``items`` de izquierda a derecha.

    Returns:
        Una tupla ``(posición, pasos)``. La posición es el índice de la
        PRIMERA aparición, o -1 si no se encontró. ``pasos`` es la cantidad de
        elementos inspeccionados.

    Complejidad: O(n) en el peor caso (no está o está al final);
    O(1) en el mejor caso (está en la primera posición).
    """
    steps = 0
    for index in range(len(items)):
        steps += 1
        if items[index] == target:
            return index, steps
    return -1, steps


def linear_search(items: Sequence[Any], target: Any) -> int:
    """Devuelve el índice de la primera aparición de ``target`` o -1.

    Ejemplo: ``linear_search([5, 3, 8], 8)`` devuelve ``2``.
    """
    index, _steps = linear_search_with_steps(items, target)
    return index


def linear_search_all(items: Sequence[Any], target: Any) -> list[int]:
    """Devuelve todas las posiciones en las que aparece ``target``.

    A diferencia de ``linear_search``, no se detiene en la primera
    coincidencia: siempre recorre la colección completa. Complejidad: O(n).
    """
    positions = []
    for index in range(len(items)):
        if items[index] == target:
            positions.append(index)
    return positions


def is_sorted(items: Sequence[Any]) -> bool:
    """Indica si ``items`` está en orden ascendente (permite repetidos).

    Una colección vacía o de un elemento se considera ordenada.
    Complejidad: O(n).
    """
    for index in range(len(items) - 1):
        if items[index] > items[index + 1]:
            return False
    return True


def binary_search_with_steps(sorted_items: Sequence[Any], target: Any) -> tuple[int, int]:
    """Búsqueda binaria clásica sobre una secuencia ordenada ascendentemente.

    En cada paso se mira el elemento del medio del rango [low, high]:
    - si es el buscado, termina;
    - si es menor, el buscado solo puede estar a la derecha;
    - si es mayor, el buscado solo puede estar a la izquierda.

    IMPORTANTE: esta función NO verifica el orden. Si los datos no están
    ordenados, el resultado puede ser incorrecto. Si hay elementos repetidos,
    devuelve la posición de alguno de ellos (no necesariamente la primera).

    Returns:
        Una tupla ``(posición, pasos)``; posición -1 si no se encontró.

    Complejidad: O(log n) en el peor caso; O(1) en el mejor caso.
    """
    low = 0
    high = len(sorted_items) - 1
    steps = 0

    while low <= high:
        middle = (low + high) // 2
        steps += 1
        middle_value = sorted_items[middle]
        if middle_value == target:
            return middle, steps
        if middle_value < target:
            low = middle + 1
        else:
            high = middle - 1

    return -1, steps


def binary_search(sorted_items: Sequence[Any], target: Any, verify_order: bool = True) -> int:
    """Devuelve la posición de ``target`` en ``sorted_items`` o -1.

    Args:
        sorted_items: secuencia ordenada en forma ascendente.
        target: valor buscado.
        verify_order: si es True (por defecto), primero comprueba que los
            datos estén ordenados y lanza ``ValueError`` si no lo están.
            Esa comprobación cuesta O(n), lo que anula la ventaja de la
            búsqueda binaria; existe para evitar errores en un contexto de
            aprendizaje. Si ya sabés que los datos están ordenados, podés
            pasar ``verify_order=False``.

    Raises:
        ValueError: si ``verify_order`` es True y los datos no están ordenados.
    """
    if verify_order and not is_sorted(sorted_items):
        raise ValueError("La búsqueda binaria requiere datos ordenados de forma ascendente.")
    index, _steps = binary_search_with_steps(sorted_items, target)
    return index


def search_word(words: Sequence[str], target: str, case_sensitive: bool = False) -> list[int]:
    """Busca una palabra dentro de una colección de palabras.

    La comparación es de palabra completa: "sol" no coincide con "solo".

    Args:
        words: colección de palabras (por ejemplo, el resultado de ``tokenize``).
        target: palabra buscada. Se ignoran los espacios de los extremos.
        case_sensitive: si es False, "Hola" y "hola" se consideran iguales.

    Returns:
        Lista con las posiciones donde aparece la palabra (vacía si no está).

    Raises:
        ValueError: si ``target`` está vacío.
    """
    wanted = target.strip()
    if wanted == "":
        raise ValueError("La palabra a buscar no puede estar vacía.")
    if not case_sensitive:
        wanted = wanted.lower()

    positions = []
    for index in range(len(words)):
        current = words[index] if case_sensitive else words[index].lower()
        if current == wanted:
            positions.append(index)
    return positions


def find_records(
    records: Sequence[dict],
    field: str,
    value: str,
    exact: bool = False,
    case_sensitive: bool = False,
) -> list[dict]:
    """Búsqueda lineal de registros según el valor de un campo.

    Args:
        records: lista de diccionarios.
        field: nombre del campo a revisar. Los registros que no lo tienen se
            ignoran.
        value: valor buscado. Se ignoran los espacios de los extremos.
        exact: si es True, el campo debe ser igual al valor; si es False,
            basta con que lo contenga.
        case_sensitive: si es False, no distingue mayúsculas de minúsculas.

    Returns:
        Los registros que cumplen el criterio, en su orden original.

    Raises:
        ValueError: si ``value`` está vacío.

    Complejidad: O(n · m), con n registros y m el largo del texto comparado.
    """
    wanted = value.strip()
    if wanted == "":
        raise ValueError("El valor a buscar no puede estar vacío.")
    if not case_sensitive:
        wanted = wanted.lower()

    matches = []
    for record in records:
        raw_value = record.get(field)
        if raw_value is None:
            continue
        current = raw_value.strip()
        if not case_sensitive:
            current = current.lower()

        if exact:
            matched = current == wanted
        else:
            matched = wanted in current

        if matched:
            matches.append(record)
    return matches


def compare_search_methods(items: Sequence[Any], target: Any) -> dict:
    """Compara búsqueda lineal y binaria sobre los mismos datos.

    La búsqueda lineal se aplica a ``items`` tal como vienen. Para la binaria,
    si ``items`` no está ordenado, se ordena primero una copia con
    ``sorted()``. Ese ordenamiento tiene su propio costo (O(n log n)), que
    solo conviene pagar si después se harán muchas búsquedas.

    Returns:
        Un diccionario con el tamaño de los datos, si ya estaban ordenados y,
        para cada método, si encontró el valor, en qué posición y en cuántos
        pasos. La posición de la binaria corresponde a la lista ORDENADA.
    """
    linear_index, linear_steps = linear_search_with_steps(items, target)

    was_sorted = is_sorted(items)
    if was_sorted:
        sorted_items = list(items)
    else:
        sorted_items = sorted(items)
    binary_index, binary_steps = binary_search_with_steps(sorted_items, target)

    return {
        "target": target,
        "size": len(items),
        "was_sorted": was_sorted,
        "linear": {
            "found": linear_index != -1,
            "index": linear_index,
            "steps": linear_steps,
        },
        "binary": {
            "found": binary_index != -1,
            "index": binary_index,
            "steps": binary_steps,
        },
    }
