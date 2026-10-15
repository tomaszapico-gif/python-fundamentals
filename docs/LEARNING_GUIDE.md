# Guía de aprendizaje

Esta guía está pensada para estudiar el proyecto **de menor a mayor dificultad**. Leer el código no es lo mismo que entenderlo: en cada etapa vas a encontrar preguntas para responder y ejercicios para resolver **sin mirar la solución**.

## Cómo usar esta guía

1. Seguí las etapas en orden. Cada una se apoya en la anterior.
2. Antes de leer una función, leé su docstring y tratá de adivinar cómo está implementada.
3. Usá el intérprete interactivo para experimentar. Desde la raíz del proyecto:

   ```bash
   python
   >>> from src import text_analyzer as ta
   >>> ta.tokenize("¡Hola,   mundo!")
   ['hola', 'mundo']
   ```

4. Después de cada etapa, ejecutá las pruebas del módulo y leelas: **las pruebas son ejemplos de uso**.
5. Hacé los ejercicios en un archivo aparte (por ejemplo `practice/etapa1.py`). No modifiques `src/` hasta la etapa 14.

## Mapa del proyecto

| Archivo | Dificultad | Qué enseña |
|---|---|---|
| `src/text_analyzer.py` | ★☆☆ | strings, bucles, funciones, diccionarios |
| `src/search_algorithms.py` | ★☆☆ | bucles con índices, `while`, búsqueda |
| `src/sorting_algorithms.py` | ★★☆ | algoritmos, intercambios, claves de orden |
| `src/file_handler.py` | ★★☆ | archivos, `pathlib`, excepciones |
| `src/csv_analyzer.py` | ★★☆ | registros, validación, módulo `csv` |
| `src/report_generator.py` | ★★☆ | formato de texto, JSON, CSV |
| `src/analyzer.py` | ★★☆ | modularización, coordinación |
| `src/main.py` | ★★★ | interfaz, bucles de menú, validación de entrada |
| `tests/` | ★★☆ | pruebas automatizadas |

**Orden recomendado de lectura:** `text_analyzer.py` → `search_algorithms.py` → `sorting_algorithms.py` → `file_handler.py` → `csv_analyzer.py` → `report_generator.py` → `analyzer.py` → `main.py`.

---

## Etapa 1 — Variables y strings

**Conceptos:** variables, `str`, `len()`, métodos `lower()`, `strip()`, `split()`, `replace()`, `find()`, slicing (`texto[1:4]`).

**Conocimientos previos:** ninguno, más allá de ejecutar Python.

**Dónde verlo:**

- `count_characters`: `len()` sobre un string.
- `split_lines`: `replace()` y `split("\n")`.
- `normalize_word`: slicing con `word[start:end]`.

**Preguntas para responder:**

- ¿Por qué `count_characters("a\nb")` devuelve 3?
- ¿Qué diferencia hay entre `"hola mundo".split()` y `"hola  mundo".split(" ")`? Probalo.

**Errores comunes:**

- Creer que los strings se modifican: `texto.lower()` **devuelve** un string nuevo; `texto` sigue igual.
- Confundir `split()` (sin argumentos: cualquier espacio en blanco, sin vacíos) con `split(" ")` (genera strings vacíos con espacios repetidos).

**Ejercicios:**

1. Escribí `count_vowels(text)` que cuente las vocales (incluidas las acentuadas).
2. Escribí `reverse_words(text)` que invierta el orden de las palabras: `"hola mundo"` → `"mundo hola"`.

## Etapa 2 — Condicionales

**Conceptos:** `if`, `elif`, `else`, operadores de comparación y lógicos (`and`, `or`, `not`).

**Dónde verlo:**

- `bubble_sort_with_stats`: `if reverse: ... else: ...` para decidir el sentido de la comparación.
- `filter_records`: una cadena `if/elif` según el operador elegido.
- `_compare_numbers`: alternativa segura a `eval()` para aplicar un operador.

**Pregunta:** ¿por qué el proyecto nunca usa `eval("10 > 5")`? (Pista: ¿qué pasaría si el usuario escribiera código en lugar de un número?)

**Errores comunes:** usar `=` (asignación) en lugar de `==` (comparación); olvidar que el orden de los `elif` importa.

**Ejercicios:**

1. Escribí `classify_word_length(word)` que devuelva `"corta"` (≤ 3), `"media"` (4–7) o `"larga"` (≥ 8).
2. Agregá a tu versión de `_compare_numbers` el operador `"=="` con números.

## Etapa 3 — Bucles `for` (y `while`)

**Conceptos:** `for` sobre strings y listas, `range()`, acumuladores, contadores, `break`, `while`.

**Dónde verlo:**

- `count_characters_without_whitespace`: contador dentro de un `for`.
- `normalize_word`: dos bucles `while` que avanzan desde los extremos.
- `count_substring_occurrences`: `while` que se repite mientras `find()` encuentre algo.

**Pregunta:** en `normalize_word`, ¿qué pasaría si la condición del primer `while` fuera solo `not word[start].isalnum()` (sin `start < end`)? Probá con `"..."`.

**Errores comunes:** bucles infinitos con `while` (olvidar avanzar la variable); modificar una lista mientras se recorre.

**Ejercicios:**

1. Reescribí `count_empty_lines` usando `while` en lugar de `for`.
2. Escribí `count_sentences(text)` que cuente los signos `.`, `!` y `?`.

## Etapa 4 — Funciones y valores de retorno

**Conceptos:** parámetros, valores por defecto, `return`, devolver tuplas, type hints, docstrings.

**Dónde verlo:**

- `most_common_words(text, limit=10)`: parámetro con valor por defecto.
- `shortest_and_longest_words`: devuelve **dos** valores en una tupla.
- `linear_search` reutiliza `linear_search_with_steps`: una función que llama a otra.

**Pregunta:** ¿por qué `average_word_length("")` devuelve `0.0` en vez de fallar? ¿Qué error se evita?

**Errores comunes:** usar `print()` dentro de una función de lógica en lugar de `return` (después no se puede probar ni reutilizar el resultado); listas mutables como valor por defecto (`def f(x=[])`).

**Ejercicios:**

1. Escribí `longest_line(text)` que devuelva `(número_de_línea, línea)` de la línea más larga.
2. Escribí la docstring de tu función: qué recibe, qué devuelve y qué pasa con un texto vacío.

## Etapa 5 — Listas y diccionarios (y tuplas y conjuntos)

**Conceptos:** listas (`append`, índices, slicing), diccionarios (`get`, recorrer `items()`), tuplas, conjuntos.

**Dónde verlo:**

- `word_frequencies`: el patrón `frequencies[word] = frequencies.get(word, 0) + 1`.
- `count_empty_fields_by_column`: inicializar un diccionario con ceros y luego sumar.
- Cada registro CSV es un diccionario `{columna: valor}`.
- Las tuplas `(palabra, cantidad)` en `most_common_words`.

**Pregunta:** ¿cuántas palabras distintas hay en un texto? Se puede calcular con `len(set(tokenize(texto)))`. ¿Por qué el proyecto usa `len(word_frequencies(texto))`?

**Errores comunes:** `diccionario[clave]` lanza `KeyError` si la clave no existe; `get()` no.

**Ejercicios:**

1. Escribí `words_by_first_letter(text)` → `{"h": ["hola", "hoy"], ...}`.
2. Escribí `common_words(text_a, text_b)` que devuelva las palabras presentes en ambos textos usando conjuntos.

## Etapa 6 — Búsqueda y frecuencia

**Conceptos:** búsqueda lineal, devolver -1 o una lista de posiciones, buscar con criterio.

**Dónde verlo:** `search_algorithms.py` completo; `contains_word`, `count_word_occurrences` y `find_lines_with_word` en `text_analyzer.py`.

**Pregunta clave:** ¿por qué `count_word_occurrences(texto, "sol")` y `count_substring_occurrences(texto, "sol")` dan resultados distintos en "sol, solo, girasol"?

**Errores comunes:** confundir "contiene" con "es igual"; olvidar normalizar mayúsculas en ambos lados de la comparación.

**Ejercicios:**

1. Escribí `linear_search_last(items, target)` que devuelva la **última** posición.
2. Escribí `find_words_starting_with(text, prefix)`.

## Etapa 7 — Algoritmos de ordenamiento

**Conceptos:** comparar e intercambiar (`a, b = b, a`), bucles anidados, claves de ordenamiento, `sorted(key=...)`.

**Dónde verlo:** `sorting_algorithms.py`.

**Actividad:** ordená a mano `[4, 2, 5, 1]` con bubble sort en papel, anotando cada comparación e intercambio. Después verificalo:

```python
>>> from src.sorting_algorithms import bubble_sort_with_stats
>>> bubble_sort_with_stats([4, 2, 5, 1])
```

**Preguntas:**

- ¿Por qué el bucle interno usa `range(length - 1 - pass_number)`?
- ¿Qué cambia si se cambia `>` por `>=` en la comparación? (Pista: estabilidad.)

**Errores comunes:** salirse de la lista con `result[index + 1]`; modificar la lista original sin querer.

**Ejercicios:**

1. Implementá **selection sort** (busca el mínimo y lo pone al principio) contando comparaciones.
2. Implementá **insertion sort** y compará sus conteos con bubble sort sobre una lista casi ordenada.

## Etapa 8 — Lectura de archivos

**Conceptos:** `pathlib.Path`, `open()` con `with`, codificación UTF-8, rutas relativas y absolutas.

**Dónde verlo:** `file_handler.read_text_file`, `resolve_input_path`, `write_new_text_file`.

**Preguntas:**

- ¿Para qué sirve `with`? ¿Qué pasaría si el programa falla entre `open()` y `close()`?
- ¿Qué diferencia hay entre el modo `"w"` y el modo `"x"`? ¿Por qué el proyecto usa `"x"`?

**Errores comunes:** no indicar `encoding="utf-8"` (en Windows el valor por defecto puede ser otro); asumir que la ruta relativa se calcula desde el archivo `.py` (se calcula desde la carpeta actual de la terminal).

**Ejercicios:**

1. Escribí un script que lea `samples/example.txt` y guarde en `practice/upper.txt` el texto en mayúsculas.
2. Escribí `count_files_by_extension(folder)` usando `Path.iterdir()`.

## Etapa 9 — Manejo de excepciones

**Conceptos:** `try/except`, excepciones específicas, excepciones propias (`class FileAccessError(Exception)`), `raise ... from error`.

**Dónde verlo:** `file_handler.py` (traducción de errores), `parse_number` (`ValueError`), `main.py` (captura y muestra).

**Preguntas:**

- ¿Por qué en `read_text_file` el `except PermissionError` va **antes** que `except OSError`?
- ¿Por qué no se usa `except Exception:` para "atrapar todo"?

**Errores comunes:** capturar excepciones demasiado generales y ocultar errores de programación; capturar una excepción y no hacer nada (`pass`).

**Ejercicios:**

1. Escribí `safe_divide(a, b)` que lance `ValueError` con un mensaje claro si `b` es 0.
2. Escribí `read_number_list(path)` que lea un número por línea e informe en qué línea hay un valor inválido.

## Etapa 10 — Modularización

**Conceptos:** módulos, paquetes (`__init__.py`), `import`, separación de responsabilidades, `if __name__ == "__main__":`.

**Dónde verlo:** la estructura completa; `docs/ARCHITECTURE.md`.

**Actividad:** dibujá en papel qué módulo importa a cuál. Compará con el diagrama de `ARCHITECTURE.md`.

**Preguntas:**

- ¿Por qué `text_analyzer.py` no tiene ningún `print()`?
- ¿Qué tendrías que cambiar para agregar una interfaz gráfica? ¿Qué archivos **no** tocarías?

**Ejercicio:** mové tus funciones de las etapas 1–5 a un módulo `practice/my_text_tools.py` e importalas desde otro archivo.

## Etapa 11 — CSV y procesamiento de registros

**Conceptos:** módulo `csv`, registros como diccionarios, validación de datos, estadísticas.

**Dónde verlo:** `csv_analyzer.py`, `samples/inventory.csv`.

**Actividad:** abrí `samples/inventory.csv` y encontrá a mano los 5 problemas intencionales (fila con un campo de más, dos campos vacíos y dos números inválidos). Después ejecutá la opción 1 del menú CSV y compará.

**Preguntas:**

- ¿Por qué no se separa el CSV con `linea.split(",")`? (Pista: `"Auriculares, con micrófono"`.)
- ¿Por qué `parse_number("1.234,50")` se rechaza?

**Errores comunes:** asumir que todas las filas tienen la misma cantidad de campos; convertir con `float()` sin capturar `ValueError`.

**Ejercicios:**

1. Escribí `total_stock_value(table)` que sume `quantity * unit_price` de los registros válidos e informe cuántos se omitieron.
2. Escribí `group_count(table, column)` → `{"Librería": 3, "Tecnología": 3, ...}`.

## Etapa 12 — Pruebas automatizadas

**Conceptos:** `unittest.TestCase`, `assertEqual`, `assertRaises`, `subTest`, `setUp`/`tearDown`, carpetas temporales, `unittest.mock.patch`.

**Dónde verlo:** `tests/`. Empezá por `test_text_analyzer.py` (pruebas unitarias simples) y terminá con `test_main.py` (simula el teclado).

**Actividad:** rompé a propósito una función (por ejemplo, cambiá `>` por `>=` en `bubble_sort_with_stats`) y ejecutá las pruebas. ¿Cuál falla? ¿El mensaje te ayuda a encontrar el error? Después deshacé el cambio.

**Errores comunes:** pruebas que repiten la implementación (calculan el resultado esperado con el mismo código); probar solo el "caso feliz".

**Ejercicio:** escribí pruebas para todas tus funciones de práctica, incluidos casos vacíos, con tildes y con signos de puntuación.

## Etapa 13 — Complejidad algorítmica

**Conceptos:** notación O, mejor/peor caso, contar operaciones.

**Dónde verlo:** `docs/ALGORITHMS.md`; las funciones `*_with_steps` y `bubble_sort_with_stats`.

**Actividad:** completá esta tabla ejecutando `bubble_sort_with_stats(list(range(n, 0, -1)))` y `binary_search_with_steps(list(range(n)), -1)`:

| n | comparaciones bubble sort (peor caso) | pasos búsqueda binaria |
|---|---|---|
| 10 | | |
| 100 | | |
| 1000 | | |

¿Cómo crece cada columna cuando n se multiplica por 10?

**Ejercicio:** escribí un script que mida el tiempo de `bubble_sort` y `sorted` con `time.perf_counter()` para 100, 1.000 y 3.000 elementos aleatorios. Anotá tus resultados y explicá por qué varían entre ejecuciones.

## Etapa 14 — Git y mantenimiento del proyecto

**Conceptos:** repositorio, commits, `.gitignore`, ramas, README.

**Actividad:**

```bash
git init
git add .
git commit -m "Versión inicial del analizador"
git switch -c feature/sentence-count
# ... agregar count_sentences con su prueba ...
python -m unittest discover -s tests
git add .
git commit -m "Agrega conteo de oraciones"
```

**Preguntas:** ¿por qué `reports/` está en `.gitignore`? ¿Qué pasaría si se subiera la carpeta `.venv/`?

**Buenas prácticas:** commits pequeños con mensajes descriptivos; ejecutar las pruebas antes de cada commit; actualizar el README cuando cambia el comportamiento.

---

## Plan para reconstruir el proyecto por tu cuenta

Cuando termines las etapas, intentá rehacer el proyecto **desde una carpeta vacía**, consultando el original solo cuando te trabes:

1. **Día 1:** `text_analyzer.py` con `tokenize`, `count_words`, `count_lines` y sus pruebas.
2. **Día 2:** frecuencias, palabra más corta/larga, promedio. Pruebas con tildes y signos.
3. **Día 3:** `search_algorithms.py` (lineal y binaria) con pruebas.
4. **Día 4:** `sorting_algorithms.py` (bubble sort) con pruebas de lista vacía, un elemento, repetidos y ya ordenada.
5. **Día 5:** `file_handler.py`: leer un archivo y manejar los errores.
6. **Día 6:** un `main.py` mínimo con un menú de 3 opciones.
7. **Día 7:** `csv_analyzer.py`: leer, validar, contar.
8. **Día 8:** estadísticas, búsqueda y filtros en CSV.
9. **Día 9:** exportación a TXT/JSON sin sobrescribir.
10. **Día 10:** README propio y comparación con el original: ¿qué resolviste distinto? ¿qué mejorarías?

## Ejercicios progresivos de integración

Estos ejercicios modifican el proyecto real. Hacelos en una rama de Git y agregá pruebas para cada uno.

1. **(Fácil)** Agregá `count_sentences` al resumen de texto y al informe.
2. **(Fácil)** Agregá una opción de menú que muestre las palabras que aparecen una sola vez.
3. **(Media)** Agregá un parámetro `stop_words` a `most_common_words` para excluir palabras como "de", "la", "y".
4. **(Media)** Implementá `insertion_sort_with_stats` y agregalo a la opción 6 para comparar con bubble sort.
5. **(Media)** Agregá a las estadísticas CSV la cantidad de valores distintos de cada columna.
6. **(Difícil)** Permití combinar dos filtros (`quantity > 10` **y** `category == Bazar`).
7. **(Difícil)** Hacé que `read_text_file` acepte un parámetro `encoding` y agregá una opción de menú para elegirlo.
8. **(Difícil)** Procesá archivos grandes línea por línea para contar palabras sin cargarlos completos en memoria.
