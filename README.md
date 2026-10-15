# Python Fundamentals & Algorithms — Text and Data Analyzer

Aplicación de consola en Python que analiza archivos de texto (`.txt`) y archivos de datos (`.csv`), implementa algoritmos clásicos de búsqueda y ordenamiento, y exporta informes en texto, JSON y CSV. Usa **solo la biblioteca estándar** de Python.

## Problema que resuelve

Quien empieza a programar suele aprender conceptos sueltos (un bucle, una función, un diccionario) sin ver cómo se combinan en un programa real. Este proyecto resuelve un problema concreto —obtener métricas de un texto y detectar problemas en un archivo de datos— y lo hace de una forma que se puede estudiar:

- Responde preguntas reales: ¿cuántas palabras tiene este texto?, ¿cuáles se repiten más?, ¿en qué líneas aparece una palabra?, ¿qué filas de este CSV están mal formadas?, ¿cuánto suma esta columna?
- Muestra la diferencia entre algoritmos (búsqueda lineal vs. binaria, bubble sort vs. `sorted()`) con datos propios del usuario.
- Maneja los errores esperables (archivo inexistente, codificación incorrecta, números mal escritos) sin cerrarse.

## Objetivos de aprendizaje

- Variables, tipos de datos y operaciones con strings.
- Condicionales y bucles `for` / `while`.
- Funciones con parámetros, valores de retorno y docstrings.
- Listas, tuplas, conjuntos y diccionarios.
- Búsqueda lineal y binaria; bubble sort implementado a mano.
- Lectura y escritura de archivos con `pathlib`, `json` y `csv`.
- Excepciones y validación de entradas.
- Modularización: separar interfaz, lógica y acceso a archivos.
- Pruebas automatizadas con `unittest`.
- Complejidad algorítmica básica (notación O).
- Documentación y publicación de un proyecto con Git.

## Funcionalidades

**Análisis de texto (`.txt`)**

- Conteo de caracteres (con y sin espacios en blanco), palabras, palabras distintas, líneas y líneas vacías.
- Longitud promedio de palabra; palabra más corta y más larga.
- Frecuencia de cada palabra y ranking de las más frecuentes.
- Búsqueda de una palabra completa, conteo de apariciones y listado de las líneas que la contienen.
- Conteo de un fragmento como secuencia exacta (para comparar con el conteo de palabra completa).
- Ordenamiento alfabético de las palabras distintas con bubble sort, comparado con `sorted()`.
- Comparación de búsqueda lineal y binaria (elementos inspeccionados).

**Análisis CSV (`.csv`)**

- Detección del separador (coma, punto y coma o tabulación) y de los encabezados.
- Conteo de registros; detección de filas con cantidad incorrecta de campos, filas vacías y campos vacíos.
- Búsqueda de registros por valor (en todas las columnas o en una).
- Filtros simples: `==`, `!=`, `>`, `>=`, `<`, `<=`, `contains`.
- Ordenamiento por cualquier columna (numérico o alfabético, según el contenido).
- Estadísticas de columnas numéricas: mínimo, máximo, suma, promedio y mediana, informando los valores inválidos.

**Informes**

- Exportación del resumen en `.txt` y `.json`.
- Exportación del último resultado de búsqueda, filtro u orden como `.csv`.
- Carpeta de salida configurable; los archivos existentes **nunca** se sobrescriben.

## Tecnologías utilizadas

- Python 3 (biblioteca estándar: `pathlib`, `csv`, `json`, `unicodedata`, `argparse`, `unittest`).
- Sin dependencias externas, sin base de datos, sin APIs ni servicios de inteligencia artificial.

## Requisitos previos

- **Python 3.10 o superior** (recomendado). La suite de pruebas se ejecutó con éxito en Python 3.9, 3.11, 3.12 y 3.13; Python 3.10 no se probó directamente.
- Git (opcional, para clonar el repositorio).

## Instalación paso a paso

```bash
# 1. Clonar el repositorio (o descargar el ZIP y descomprimirlo)
git clone https://github.com/<tu-usuario>/python-fundamentals.git
cd python-fundamentals

# 2. (Opcional, recomendado) Crear y activar un entorno virtual
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (cmd):
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# 3. Instalar dependencias (no hay paquetes externos; el comando no instala nada)
python -m pip install -r requirements.txt
```

> En Windows, si `python` no se reconoce, probá con `py`. Si PowerShell bloquea la activación del entorno, ejecutá una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Ejecutar la aplicación

Desde la raíz del repositorio:

```bash
python -m src.main
```

También funciona indicando la ruta del archivo desde cualquier carpeta:

```bash
python ruta/al/proyecto/src/main.py
```

Para guardar los informes en otra carpeta:

```bash
python -m src.main --reports-dir mis_informes
```

Una carpeta de informes relativa (como `mis_informes`) se interpreta desde la carpeta actual de la terminal y se crea al exportar si no existe. También se puede cambiar durante la ejecución con la opción 3 del menú principal.

Las rutas relativas de archivos que se escriben en el menú (por ejemplo `samples/example.txt`) se buscan primero desde la carpeta actual y, si no existen allí, desde la raíz del proyecto.

## Ejecutar las pruebas

```bash
# Toda la suite
python -m unittest discover -s tests -v

# Un módulo
python -m unittest tests.test_text_analyzer -v
python -m unittest tests.test_search_algorithms -v
python -m unittest tests.test_sorting_algorithms -v
python -m unittest tests.test_csv_analyzer -v
python -m unittest tests.test_file_handler -v
python -m unittest tests.test_report_generator -v
python -m unittest tests.test_analyzer -v      # integración (archivos reales)
python -m unittest tests.test_main -v          # interfaz de consola simulada
```

La prueba de "archivo sin permisos de lectura" se omite automáticamente en Windows y cuando se ejecuta como administrador/root, porque en esos casos no se puede reproducir la falta de permisos.

## Ejemplos de uso

Sesión típica:

1. Ejecutar `python -m src.main`.
2. Elegir `1` (texto) y escribir `samples/example.txt`.
3. Elegir `1` para el resumen, `3` para buscar una palabra, `8` para exportar.
4. Volver con `0`, elegir `2` (CSV) y escribir `samples/inventory.csv`.
5. Elegir `6` para filtrar (por ejemplo `quantity` `>` `20`) y `10` para exportar el resultado.
6. Salir con `0`.

## Ejemplos de entrada y salida

Las siguientes salidas se copiaron de una ejecución real con los archivos de `samples/`.

**Resumen de `samples/example.txt`:**

```text
Caracteres (incluye espacios y saltos de línea) : 945
Caracteres sin espacios en blanco               : 782
Palabras                                        : 156
Palabras distintas                              : 110
Líneas                                          : 16
Líneas vacías                                   : 5
Longitud promedio de palabra                    : 4.79
Palabra más corta                               : a
Palabra más larga                               : ingredientes

Palabras más frecuentes:
    1. un (8)
    2. una (6)
    3. y (6)
    4. el (5)
    5. con (4)
```

**Palabra completa vs. secuencia exacta** (opción 4 con `programa`):

```text
La secuencia 'programa' aparece 7 veces (sin distinguir mayúsculas).
Como palabra completa aparece 3 veces.
La diferencia corresponde a apariciones dentro de otras palabras.
```

**Bubble sort vs. `sorted()`** (opción 6):

```text
Bubble sort: 5904 comparaciones y 2964 intercambios.
El resultado coincide con sorted() (Timsort), la herramienta incorporada de Python.
```

**Resumen de `samples/inventory.csv`** (el archivo tiene errores intencionales para mostrar la validación):

```text
Separador detectado    : coma
Encabezados (6)        : sku, product, category, quantity, unit_price, supplier
Registros válidos      : 11
Filas mal formadas     : 1
Campos vacíos (total)  : 2

Problemas de formato:
  - Línea 10: Se esperaban 6 campos y se encontraron 7. La fila se excluyó del análisis.
...
Columna: quantity
  Valores numéricos válidos : 9
  Valores vacíos            : 1
  Valores no numéricos      : 1
  Mínimo                    : 5
  Máximo                    : 300
  Suma                      : 565
  Promedio                  : 62.78
  Mediana                   : 25
  ! Línea 8: 'doce' no es un número válido
```

**Filtro `quantity > 20`:**

```text
sku   | product            | category   | quantity | unit_price | supplier
------+--------------------+------------+----------+------------+-------------------
A-100 | Cuaderno rayado A4 | Librería   | 120      | 850.50     | Papelera del Sur
A-101 | Lapicera azul      | Librería   | 300      | 320        | Papelera del Sur
A-102 | Resma de papel 50… | Librería   | 45       | 5200       | Distribuidora Nor…
B-200 | Mouse inalámbrico  | Tecnología | 30       | 15999.99   | TecnoSur
C-301 | Termo de acero 1 L | Bazar      | 25       | 31000      | Bazar Total
5 registro(s).
Se omitieron 2 registro(s) cuyo valor no es un número válido.
```

**Informe JSON exportado** (fragmento; la fecha cambia en cada exportación):

```json
{
  "report_type": "text",
  "source_file": "example.txt",
  "generated_at": "2026-10-15T20:54:04",
  "data": {
    "characters": 945,
    "words": 156,
    "most_common_words": [
      { "word": "un", "count": 8 }
    ]
  }
}
```

## Reglas de análisis (resumen)

- **Caracteres:** el conteo total incluye espacios, tabulaciones y saltos de línea; el conteo "sin espacios" excluye todo carácter de espacio en blanco. El texto se normaliza a Unicode NFC (una "é" cuenta como 1).
- **Palabras:** se separan por espacios en blanco y saltos de línea; se quitan los signos de los extremos (`¿Hola?` → `hola`); se conservan los internos (`bien-estar`); se pasa a minúsculas; se conservan tildes y `ñ`; los números cuentan como palabras.
- **Palabra completa vs. secuencia:** `sol` aparece 1 vez como palabra en "sol, solo, girasol", pero la secuencia `sol` aparece 3 veces.
- **CSV:** las filas con cantidad incorrecta de campos se excluyen y se informan; los encabezados vacíos o repetidos impiden el análisis; los números aceptan punto o coma decimal, pero no separadores de miles.

El detalle completo está en los docstrings de `src/text_analyzer.py` y `src/csv_analyzer.py`.

## Estructura de carpetas

```text
python-fundamentals/
├── src/
│   ├── __init__.py
│   ├── main.py                 # interfaz de consola (menús)
│   ├── analyzer.py             # coordina archivos + análisis + informes
│   ├── text_analyzer.py        # análisis de texto (funciones puras)
│   ├── csv_analyzer.py         # análisis de registros CSV
│   ├── search_algorithms.py    # búsqueda lineal y binaria
│   ├── sorting_algorithms.py   # bubble sort y ordenamientos auxiliares
│   ├── file_handler.py         # lectura/escritura segura de archivos
│   └── report_generator.py     # formato y exportación de informes
├── tests/                      # pruebas unitarias y de integración (unittest)
├── samples/
│   ├── example.txt
│   └── inventory.csv           # inventario ficticio con errores intencionales
├── reports/                    # informes generados (ignorados por Git)
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ALGORITHMS.md
│   └── LEARNING_GUIDE.md
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Algoritmos implementados

| Algoritmo | Dónde | Complejidad temporal |
|---|---|---|
| Búsqueda lineal | `search_algorithms.linear_search` | O(n) peor caso, O(1) mejor caso |
| Búsqueda binaria | `search_algorithms.binary_search` | O(log n), requiere datos ordenados |
| Bubble sort (manual) | `sorting_algorithms.bubble_sort` | O(n²) peor caso, O(n) mejor caso |
| Conteo de frecuencias | `text_analyzer.word_frequencies` | O(n) promedio |
| Orden alfabético, por frecuencia y de registros | `sorting_algorithms` (usa `sorted()`, Timsort) | O(n log n) |

Análisis detallado en [`docs/ALGORITHMS.md`](docs/ALGORITHMS.md).

## Documentación adicional

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): componentes, flujo de datos y decisiones de diseño.
- [`docs/ALGORITHMS.md`](docs/ALGORITHMS.md): funcionamiento y complejidad de cada algoritmo.
- [`docs/LEARNING_GUIDE.md`](docs/LEARNING_GUIDE.md): guía de estudio progresiva con ejercicios.

## Limitaciones conocidas

- Los archivos se cargan completos en memoria; el máximo admitido es 10 MB (`MAX_FILE_SIZE_BYTES` en `file_handler.py`).
- Solo se leen archivos en UTF-8. Un archivo en Latin-1/ANSI se rechaza con un mensaje que pide convertirlo.
- Las palabras se separan solo por espacios: `hola,mundo` (sin espacio) cuenta como una palabra.
- El orden alfabético contempla tildes y `ñ` del español, pero no es una implementación completa de las reglas de ordenación Unicode.
- `parse_number` no acepta separadores de miles (`1.234,50`) para no interpretar mal valores ambiguos.
- El número de línea informado para un registro CSV con un campo entre comillas de varias líneas es la línea donde termina el registro.
- Los CSV exportados contienen los valores tal como estaban. Si se abren en una planilla de cálculo, un valor que empiece con `=` podría interpretarse como fórmula; conviene revisar archivos de origen desconocido.
- La comparación de algoritmos cuenta elementos inspeccionados y comparaciones, no tiempo de ejecución.

## Posibles mejoras futuras

- Procesar archivos grandes por bloques o línea por línea, en lugar de cargarlos completos.
- Elegir la codificación de lectura (por ejemplo `latin-1`).
- Lista configurable de palabras vacías ("de", "la", "y") para excluirlas del ranking.
- Implementar a mano otros algoritmos (insertion sort, merge sort) y comparar sus conteos.
- Modo no interactivo (`python -m src.main --text archivo.txt --json`).
- Integración continua (GitHub Actions) que ejecute las pruebas en cada push.
- Fuera del alcance de esta versión: interfaz gráfica, aplicación web, API REST o integración con IA.

## Licencia

Distribuido bajo la licencia MIT. Ver [`LICENSE`](LICENSE).

## Uso de herramientas de IA

El código, las pruebas y la documentación de este proyecto se desarrollaron con la asistencia de Claude (Anthropic), a partir de requisitos definidos por el autor. Las pruebas se ejecutaron en un entorno real y las salidas de ejemplo de este README provienen de ejecuciones reales. El autor es responsable de revisar, comprender y mantener el código.
