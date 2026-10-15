# Algoritmos y complejidad

Este documento explica cada algoritmo del proyecto: qué problema resuelve, cómo funciona, qué condiciones necesita y cuánto cuesta.

## Antes de empezar: ¿qué significa O(n)?

La notación O describe **cómo crece** la cantidad de trabajo cuando crece la cantidad de datos (`n`). No mide segundos.

| Notación | Nombre | Si los datos se duplican, el trabajo... |
|---|---|---|
| O(1) | constante | no cambia |
| O(log n) | logarítmica | aumenta en un paso |
| O(n) | lineal | se duplica |
| O(n log n) | casi lineal | algo más que se duplica |
| O(n²) | cuadrática | se multiplica por 4 |

Advertencias importantes:

- La notación O ignora constantes. Un algoritmo O(n) con mucho trabajo por elemento puede ser más lento que uno O(n²) cuando `n` es chico.
- **No alcanza con la notación O para afirmar que un algoritmo es más rápido en la práctica.** Para eso hay que medir con datos reales, en una computadora concreta.
- Muchas veces el costo depende del caso: hablamos de **mejor caso**, **peor caso** y **caso promedio**.

En este proyecto se comparan algoritmos **contando operaciones** (elementos inspeccionados, comparaciones, intercambios), que es reproducible y no depende de la computadora.

---

## 1. Búsqueda lineal

**Código:** `search_algorithms.linear_search`, `linear_search_with_steps`, `linear_search_all`, `search_word`, `find_records`.

**Problema:** encontrar un valor dentro de una colección.

**Cómo funciona:** recorre los elementos de izquierda a derecha y compara cada uno con el buscado. Se detiene en la primera coincidencia (o al final, si no lo encuentra).

**Pasos:**

1. Empezar en la posición 0.
2. Si el elemento actual es el buscado, devolver la posición.
3. Si no, avanzar a la siguiente posición.
4. Si se terminó la colección, devolver -1.

**Condiciones:** ninguna. Funciona con datos ordenados o desordenados, de cualquier tipo que se pueda comparar con `==`.

| Caso | Costo | Ejemplo |
|---|---|---|
| Mejor | O(1) | el valor está en la primera posición |
| Peor | O(n) | el valor está al final o no está |
| Promedio | O(n) | en promedio se revisa la mitad |

**Espacio:** O(1) para `linear_search` (solo variables). `linear_search_all` usa O(k) para guardar las k posiciones encontradas.

**Ventajas:** simple, no requiere preparación, sirve para cualquier criterio (por ejemplo "el campo contiene este texto", que es lo que hace `find_records`).

**Limitaciones:** con muchos datos y muchas búsquedas repetidas se vuelve costosa.

**Cuándo usarla:** colecciones chicas, datos desordenados, búsquedas únicas o criterios que no son "igual a" (contiene, mayor que, etc.).

**En el proyecto:** `contains_word` y `count_word_occurrences` buscan sobre la lista de palabras; `find_records` busca registros CSV por el valor de un campo.

---

## 2. Búsqueda binaria

**Código:** `search_algorithms.binary_search`, `binary_search_with_steps`.

**Problema:** encontrar un valor en una colección **ordenada** muy rápidamente.

**Cómo funciona:** mira el elemento del medio. Si es el buscado, termina. Si el del medio es menor, descarta la mitad izquierda; si es mayor, descarta la derecha. Repite sobre la mitad que queda.

**Pasos** (buscando 7 en `[1, 3, 5, 7, 9, 11]`):

1. `low=0`, `high=5`, medio = 2 → valor 5. 5 < 7 → `low=3`.
2. `low=3`, `high=5`, medio = 4 → valor 9. 9 > 7 → `high=3`.
3. `low=3`, `high=3`, medio = 3 → valor 7. ¡Encontrado en 3 pasos!

**Condiciones (imprescindibles):**

- Los datos deben estar **ordenados de forma ascendente**.
- Deben estar ordenados **con el mismo criterio de comparación** que usa la búsqueda. Si la lista se ordenó con `alphabetical_key` (que ignora tildes) pero la búsqueda compara con `<` normal, los resultados pueden ser incorrectos. Por eso, en la opción 7 del menú, la copia para la búsqueda binaria se ordena con `sorted()` simple.
- Hace falta acceso por índice (listas, tuplas), no sirve para recorrer un archivo línea por línea.

**Si los datos no están ordenados**, la búsqueda binaria no da error por sí sola: simplemente puede decir "no está" cuando sí está. Por eso `binary_search` verifica el orden por defecto (`verify_order=True`) y lanza `ValueError`. Esa verificación cuesta O(n), lo que elimina la ventaja de la búsqueda binaria: está pensada como protección para aprender, y se puede desactivar.

| Caso | Costo |
|---|---|
| Mejor | O(1) (el buscado está justo en el medio) |
| Peor | O(log n) |
| Promedio | O(log n) |

Con 1.024 elementos, como mucho 11 pasos; con 1.000.000, como mucho 20. La prueba `test_steps_grow_logarithmically` lo verifica.

**Espacio:** O(1) (versión iterativa).

**Elementos repetidos:** la versión implementada (clásica) devuelve la posición de **alguna** aparición, no necesariamente la primera.

### Lineal vs. binaria

| | Lineal | Binaria |
|---|---|---|
| Requiere orden | No | Sí |
| Peor caso | O(n) | O(log n) |
| Preparación | Ninguna | Ordenar: O(n log n) si los datos no están ordenados |
| Criterios flexibles ("contiene") | Sí | No |

**Conclusión práctica:** si hay que buscar **una sola vez** en datos desordenados, conviene la lineal: ordenar primero (O(n log n)) cuesta más que recorrer (O(n)). Si se harán **muchas búsquedas** sobre los mismos datos, ordenar una vez y usar binaria puede convenir. En Python, para búsquedas por igualdad repetidas, un `set` o un `dict` (O(1) promedio) suele ser todavía mejor.

---

## 3. Bubble sort

**Código:** `sorting_algorithms.bubble_sort`, `bubble_sort_with_stats`.

> **Uso educativo.** Bubble sort es ineficiente para muchos datos. En código real se usa `sorted()` o `list.sort()`.

**Problema:** ordenar una lista.

**Cómo funciona:** recorre la lista comparando pares de vecinos; si están en el orden incorrecto, los **intercambia**. Al terminar una pasada, el mayor elemento quedó al final (como una burbuja que sube). Se repite sobre la parte que falta ordenar.

**Pasos** (ordenando `[5, 1, 4, 2]`):

```text
Pasada 1: [5,1,4,2] → comparar 5,1 → intercambiar → [1,5,4,2]
                     comparar 5,4 → intercambiar → [1,4,5,2]
                     comparar 5,2 → intercambiar → [1,4,2,5]   (5 ya está en su lugar)
Pasada 2:            comparar 1,4 → nada
                     comparar 4,2 → intercambiar → [1,2,4,5]   (4 en su lugar)
Pasada 3:            comparar 1,2 → nada
                     sin intercambios → la lista está ordenada, se corta
```

**Detalles de la implementación:**

- **Corte temprano:** si una pasada no hizo intercambios, la lista ya está ordenada y el algoritmo termina.
- **Pasadas más cortas:** después de la pasada `k`, los últimos `k` elementos ya están en su lugar y no se revisan.
- **Estable:** solo intercambia si el orden es *estrictamente* incorrecto, así los elementos iguales conservan su orden original.
- **Parámetros `key` y `reverse`:** permiten ordenar por un criterio (por ejemplo `alphabetical_key`) y en orden descendente.
- **No modifica la entrada:** trabaja sobre una copia.

| Caso | Comparaciones | Intercambios | Costo |
|---|---|---|---|
| Mejor (ya ordenada) | n − 1 | 0 | O(n) |
| Peor (orden inverso) | n(n − 1)/2 | n(n − 1)/2 | O(n²) |
| Promedio | ~n²/2 | ~n²/4 | O(n²) |

Las pruebas verifican estos números: con 5 elementos ordenados hace 4 comparaciones; con 5 elementos en orden inverso hace 10 comparaciones y 10 intercambios.

**Espacio:** O(n) en esta implementación, porque copia la lista para no modificar la original. El algoritmo en sí ordena "en el lugar" (O(1) adicional).

**Ventajas:** fácil de entender y de implementar; detecta en O(n) una lista ya ordenada.

**Limitaciones:** O(n²). Con 10.000 elementos, el peor caso supera los 49 millones de comparaciones.

**Cuándo usarlo:** para aprender; como mucho, para listas muy chicas o casi ordenadas.

**En el proyecto:** la opción 6 del menú de texto ordena las palabras distintas con bubble sort y verifica que el resultado coincida con `sorted()`. Se limita a 2.000 palabras por su costo cuadrático.

---

## 4. Ordenamiento incorporado de Python: Timsort

**Código:** `sorted()` y `list.sort()`, usados en `sort_alphabetically`, `sort_by_frequency`, `sort_records` y en la mediana.

Python implementa **Timsort**, un algoritmo híbrido creado en 2002 por Tim Peters para CPython:

- Busca tramos ya ordenados en los datos ("runs").
- Ordena los tramos cortos con *insertion sort*, que es muy rápido para pocos elementos.
- Combina los tramos con *merge* (como merge sort).

| Caso | Costo |
|---|---|
| Mejor (datos ya ordenados) | O(n) |
| Peor | O(n log n) |
| Promedio | O(n log n) |

Además es **estable**, y eso permite ordenar por varios criterios. **Espacio:** hasta O(n) adicional.

No hace falta implementarlo: lo importante es saber que existe, que es eficiente y que es lo que se debe usar en código real.

**Python 3.11 y posteriores** usan una variante de la estrategia de combinación (*powersort*); las garantías de complejidad y estabilidad se mantienen.

---

## 5. Ordenamientos auxiliares del proyecto

### Orden alfabético en español (`alphabetical_key`)

La comparación normal de strings usa los códigos Unicode: `"árbol" > "zapato"` es `True` porque "á" tiene un código mayor que "z". La clave `alphabetical_key`:

1. Pasa a minúsculas.
2. Quita las tildes **solo para comparar** (`"á"` → `"a"`), usando `unicodedata`.
3. Trata la "ñ" como letra propia entre "n" y "o".
4. Desempata con el texto original para que el resultado sea siempre el mismo.

Costo: O(L) por palabra (L = largo). Ordenar k palabras: O(k log k) comparaciones.

### Por frecuencia (`sort_by_frequency`)

Ordena pares `(palabra, cantidad)` con la clave `(-cantidad, clave_alfabética)`: el signo menos hace que las frecuencias altas queden primero; los empates se ordenan alfabéticamente. O(k log k).

### Registros por un campo (`sort_records`)

1. Separa los registros en "ordenables" (el campo existe y se puede convertir) y "no ordenables" (vacío o inválido).
2. Ordena los primeros con `sorted()`.
3. Agrega los no ordenables al final, en su orden original.

O(n log n). La estabilidad de Timsort garantiza que los registros con el mismo valor mantienen su orden.

---

## 6. Otros algoritmos del proyecto

| Algoritmo | Función | Costo | Comentario |
|---|---|---|---|
| Conteo de frecuencias | `word_frequencies` | O(n) promedio | Un diccionario cuesta O(1) promedio por consulta/actualización. |
| Tokenización | `tokenize` | O(n) | Un recorrido para separar y otro por palabra para limpiar extremos. |
| Mínimo / máximo / suma | `column_statistics` | O(n) | Un solo recorrido. |
| Mediana | `_median` | O(n log n) | Ordena una copia. Existen algoritmos O(n) (*quickselect*), más complejos. |
| Conteo de secuencias | `count_substring_occurrences` | O(n·m) peor caso | Usa `str.find` en un bucle; m es el largo del fragmento. |
| Verificar orden | `is_sorted` | O(n) | Compara cada elemento con el siguiente. |

## 7. Resumen

| Algoritmo | Mejor | Peor | Requiere |
|---|---|---|---|
| Búsqueda lineal | O(1) | O(n) | nada |
| Búsqueda binaria | O(1) | O(log n) | datos ordenados con el mismo criterio |
| Bubble sort | O(n) | O(n²) | nada (solo uso educativo) |
| Timsort (`sorted`) | O(n) | O(n log n) | nada |
