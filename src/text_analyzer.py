"""Análisis de texto con funciones puras (reciben un string y devuelven datos).

Ninguna función de este módulo lee archivos ni imprime en pantalla: eso es
responsabilidad de ``file_handler`` y ``main``. Así las funciones se pueden
probar con strings simples.

POLÍTICAS DE ANÁLISIS
---------------------
Caracteres
    - ``count_characters`` cuenta TODOS los caracteres: letras, dígitos,
      signos, espacios, tabulaciones y saltos de línea.
    - ``count_characters_without_whitespace`` excluye cualquier carácter de
      espacio en blanco (espacio, tabulación, salto de línea, espacio de no
      separación, etc.).
    - Antes de contar se normaliza el texto a Unicode NFC, para que una "é"
      cuente como 1 carácter aunque venga "descompuesta" ("e" + tilde).
    - Un salto de línea de Windows (\\r\\n) leído desde un archivo llega como
      un solo "\\n", porque Python traduce los finales de línea al leer.

Palabras
    - Se separan SOLO por espacios en blanco y saltos de línea (``str.split()``),
      así que varios espacios seguidos no generan palabras vacías.
    - De cada fragmento se quitan los signos de los EXTREMOS (todo lo que no
      sea letra o dígito): "¿Hola?" -> "hola", "(casa)," -> "casa".
    - Los signos INTERNOS se conservan: "bien-estar" y "O'Higgins" son una
      sola palabra. Consecuencia: "hola,mundo" (sin espacio) es una palabra.
    - Los fragmentos que quedan vacíos (por ejemplo "—" o "...") no cuentan.
    - Se pasa todo a minúsculas para que "Casa" y "casa" sean la misma palabra.
    - Las tildes, la diéresis y la "ñ" se conservan ("canción" != "cancion").
    - Los números cuentan como palabras ("3", "2026").

Líneas
    - Un texto vacío tiene 0 líneas.
    - Un salto de línea final no crea una línea extra: "a\\n" tiene 1 línea.
    - Una línea vacía es la que no tiene caracteres o solo tiene espacios.

Palabra completa vs. secuencia de caracteres
    - ``count_word_occurrences(text, "sol")`` cuenta palabras completas:
      en "sol, solo, girasol" encuentra 1.
    - ``count_substring_occurrences(text, "sol")`` cuenta apariciones exactas
      de la secuencia: en "sol, solo, girasol" encuentra 3.
"""

from __future__ import annotations

import unicodedata
from typing import Optional

from src.search_algorithms import linear_search, linear_search_all
from src.sorting_algorithms import sort_by_frequency


def _to_nfc(text: str) -> str:
    """Normaliza el texto a la forma Unicode NFC (letras con tilde compuestas)."""
    return unicodedata.normalize("NFC", text)


def count_characters(text: str) -> int:
    """Cuenta todos los caracteres, incluidos espacios y saltos de línea.

    Ejemplo: ``count_characters("hola mundo")`` devuelve ``10``.
    Complejidad: O(n).
    """
    return len(_to_nfc(text))


def count_characters_without_whitespace(text: str) -> int:
    """Cuenta los caracteres que no son espacios en blanco.

    Se excluyen espacios, tabulaciones, saltos de línea y cualquier otro
    carácter para el cual ``str.isspace()`` sea verdadero.

    Ejemplo: ``count_characters_without_whitespace("a b\\nc")`` devuelve ``3``.
    Complejidad: O(n).
    """
    total = 0
    for character in _to_nfc(text):
        if not character.isspace():
            total += 1
    return total


def normalize_word(raw_word: str) -> str:
    """Limpia un fragmento de texto para convertirlo en palabra.

    Quita los caracteres que no son letras ni dígitos de ambos extremos y
    pasa a minúsculas. Puede devolver un string vacío si el fragmento solo
    tenía signos.

    Ejemplos:
        ``normalize_word("¿Cómo?")`` -> ``"cómo"``
        ``normalize_word("bien-estar,")`` -> ``"bien-estar"``
        ``normalize_word("...")`` -> ``""``
    """
    word = _to_nfc(raw_word)
    start = 0
    end = len(word)
    while start < end and not word[start].isalnum():
        start += 1
    while end > start and not word[end - 1].isalnum():
        end -= 1
    return word[start:end].lower()


def tokenize(text: str) -> list[str]:
    """Divide el texto en palabras normalizadas, en su orden de aparición.

    Ejemplo: ``tokenize("¡Hola,  mundo! Hola.")`` -> ``["hola", "mundo", "hola"]``.
    Complejidad: O(n), con n la cantidad de caracteres.
    """
    words = []
    for raw_word in text.split():
        word = normalize_word(raw_word)
        if word != "":
            words.append(word)
    return words


def normalize_query(word: str) -> str:
    """Prepara una palabra ingresada por el usuario para buscarla.

    Aplica la misma limpieza que ``normalize_word`` para que la búsqueda sea
    coherente con el conteo de palabras.

    Raises:
        ValueError: si la entrada está vacía, solo tiene signos o contiene
            más de una palabra.
    """
    normalized = normalize_word(word.strip())
    if normalized == "":
        raise ValueError("Ingresá una palabra que contenga al menos una letra o un número.")
    for character in normalized:
        if character.isspace():
            raise ValueError("Ingresá una sola palabra, sin espacios.")
    return normalized


def count_words(text: str) -> int:
    """Cuenta las palabras según la política descrita en el módulo.

    Ejemplo: ``count_words("  uno   dos  ")`` devuelve ``2``.
    """
    return len(tokenize(text))


def split_lines(text: str) -> list[str]:
    """Divide el texto en líneas sin incluir el carácter de salto de línea.

    Acepta finales de línea de Windows (\\r\\n), Unix (\\n) y Mac antiguo (\\r).
    Un salto de línea al final del texto no genera una línea vacía extra.
    """
    if text == "":
        return []
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    if lines[-1] == "":
        lines.pop()
    return lines


def count_lines(text: str) -> int:
    """Cuenta las líneas del texto.

    Ejemplos: ``""`` -> 0, ``"a"`` -> 1, ``"a\\n"`` -> 1, ``"a\\n\\nb"`` -> 3.
    """
    return len(split_lines(text))


def count_empty_lines(text: str) -> int:
    """Cuenta las líneas vacías o formadas solo por espacios en blanco."""
    total = 0
    for line in split_lines(text):
        if line.strip() == "":
            total += 1
    return total


def average_word_length(text: str) -> float:
    """Calcula la longitud promedio de las palabras (en caracteres).

    Los signos quitados de los extremos no cuentan: en "hola," la palabra
    mide 4. Si no hay palabras devuelve 0.0 en lugar de dividir por cero.
    """
    words = tokenize(text)
    if len(words) == 0:
        return 0.0
    total_length = 0
    for word in words:
        total_length += len(word)
    return total_length / len(words)


def shortest_and_longest_words(text: str) -> tuple[Optional[str], Optional[str]]:
    """Encuentra la palabra más corta y la más larga.

    Ante empates, gana la que aparece PRIMERO en el texto.

    Returns:
        ``(más_corta, más_larga)`` o ``(None, None)`` si no hay palabras.

    Complejidad: O(n), un único recorrido.
    """
    words = tokenize(text)
    if len(words) == 0:
        return None, None

    shortest = words[0]
    longest = words[0]
    for word in words[1:]:
        if len(word) < len(shortest):
            shortest = word
        if len(word) > len(longest):
            longest = word
    return shortest, longest


def word_frequencies(text: str) -> dict[str, int]:
    """Cuenta cuántas veces aparece cada palabra.

    El diccionario conserva el orden de la primera aparición de cada palabra.
    Ejemplo: ``word_frequencies("Casa casa perro")`` -> ``{"casa": 2, "perro": 1}``.

    Complejidad: O(n) en promedio, porque consultar y actualizar un
    diccionario cuesta O(1) en promedio.
    """
    frequencies: dict[str, int] = {}
    for word in tokenize(text):
        frequencies[word] = frequencies.get(word, 0) + 1
    return frequencies


def most_common_words(text: str, limit: int = 10) -> list[tuple[str, int]]:
    """Devuelve las ``limit`` palabras más frecuentes como (palabra, cantidad).

    Ordena de mayor a menor frecuencia; los empates se ordenan
    alfabéticamente para que el resultado sea siempre el mismo.

    Raises:
        ValueError: si ``limit`` es menor que 1.
    """
    if limit < 1:
        raise ValueError("La cantidad de palabras a mostrar debe ser al menos 1.")
    ranking = sort_by_frequency(word_frequencies(text))
    return ranking[:limit]


def contains_word(text: str, word: str) -> bool:
    """Indica si la palabra aparece en el texto como palabra completa.

    No distingue mayúsculas: ``contains_word("La Casa", "casa")`` es True.
    Usa búsqueda lineal: se detiene en la primera coincidencia.

    Raises:
        ValueError: si ``word`` no es una palabra válida (ver ``normalize_query``).
    """
    target = normalize_query(word)
    return linear_search(tokenize(text), target) != -1


def count_word_occurrences(text: str, word: str) -> int:
    """Cuenta las apariciones de una palabra completa (sin distinguir mayúsculas).

    Ejemplo: en "sol, solo, girasol, Sol." la palabra "sol" aparece 2 veces.

    Raises:
        ValueError: si ``word`` no es una palabra válida.
    """
    target = normalize_query(word)
    return len(linear_search_all(tokenize(text), target))


def count_substring_occurrences(text: str, fragment: str, case_sensitive: bool = False) -> int:
    """Cuenta las apariciones exactas de una secuencia de caracteres.

    A diferencia de ``count_word_occurrences``, encuentra la secuencia aunque
    forme parte de otra palabra: "sol" aparece 3 veces en "sol, solo, girasol".
    Las apariciones no se superponen: "aa" aparece 2 veces en "aaaa".

    Raises:
        ValueError: si ``fragment`` está vacío.
    """
    if fragment == "":
        raise ValueError("El fragmento a buscar no puede estar vacío.")

    haystack = _to_nfc(text)
    needle = _to_nfc(fragment)
    if not case_sensitive:
        haystack = haystack.lower()
        needle = needle.lower()

    count = 0
    position = haystack.find(needle)
    while position != -1:
        count += 1
        position = haystack.find(needle, position + len(needle))
    return count


def find_lines_with_word(text: str, word: str) -> list[tuple[int, str]]:
    """Devuelve las líneas que contienen la palabra (como palabra completa).

    Returns:
        Lista de tuplas ``(número_de_línea, texto_de_la_línea)``. Los números
        de línea empiezan en 1, como en un editor de texto.

    Raises:
        ValueError: si ``word`` no es una palabra válida.
    """
    target = normalize_query(word)
    matches = []
    line_number = 0
    for line in split_lines(text):
        line_number += 1
        if linear_search(tokenize(line), target) != -1:
            matches.append((line_number, line))
    return matches
