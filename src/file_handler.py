"""Lectura y escritura de archivos.

Este es el único módulo que toca el sistema de archivos. Convierte los
errores técnicos (archivo inexistente, permisos, codificación) en un
``FileAccessError`` con un mensaje en español que la interfaz puede mostrar
sin cerrar la aplicación.

Decisiones:
- Se lee en UTF-8 con la variante "utf-8-sig", que además elimina la marca
  BOM que agregan algunos programas de Windows (por ejemplo Excel).
- Hay un tamaño máximo de archivo (10 MB por defecto) porque el archivo se
  carga completo en memoria. Ver "Limitaciones" en el README.
- Los informes NUNCA sobrescriben archivos existentes: se abre con el modo
  "x" (crear en exclusiva) y, si el nombre ya existe, se agrega un sufijo
  numérico (_1, _2, ...).
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Union

PathLike = Union[str, Path]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "reports"
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
READ_ENCODING = "utf-8-sig"
WRITE_ENCODING = "utf-8"
MAX_NAME_ATTEMPTS = 1000


class FileAccessError(Exception):
    """Error al leer o escribir un archivo, con un mensaje para el usuario."""


def resolve_input_path(raw_path: str, project_root: Path = PROJECT_ROOT) -> Path:
    """Convierte la ruta escrita por el usuario en un ``Path``.

    - Quita espacios y comillas de los extremos (Windows agrega comillas al
      usar "Copiar como ruta de acceso").
    - Expande ``~`` a la carpeta del usuario.
    - Si la ruta es relativa, primero se busca desde la carpeta actual y, si
      no existe ahí, desde la raíz del proyecto. Por eso
      ``samples/example.txt`` funciona aunque la terminal esté en otra carpeta.

    No verifica que el archivo exista: de eso se encarga ``read_text_file``.

    Raises:
        FileAccessError: si la ruta está vacía.
    """
    cleaned = raw_path.strip().strip('"').strip("'").strip()
    if cleaned == "":
        raise FileAccessError("No ingresaste ninguna ruta.")

    path = Path(cleaned).expanduser()
    if path.is_absolute():
        return path

    from_current_dir = Path.cwd() / path
    if from_current_dir.exists():
        return from_current_dir

    from_project_root = project_root / path
    if from_project_root.exists():
        return from_project_root

    return from_current_dir


def validate_extension(path: PathLike, allowed_extensions: Iterable[str]) -> None:
    """Verifica que el archivo tenga una de las extensiones permitidas.

    La comparación no distingue mayúsculas (".TXT" es válido para ".txt").

    Raises:
        FileAccessError: si la extensión no está permitida.
    """
    allowed = []
    for extension in allowed_extensions:
        allowed.append(extension.lower())

    suffix = Path(path).suffix.lower()
    if suffix not in allowed:
        received = suffix if suffix else "sin extensión"
        raise FileAccessError(
            f"Se esperaba un archivo {' o '.join(allowed)} y se recibió '{received}'."
        )


def read_text_file(path: PathLike, max_size_bytes: int = MAX_FILE_SIZE_BYTES) -> str:
    """Lee un archivo de texto UTF-8 completo y devuelve su contenido.

    Un archivo vacío devuelve ``""`` (no es un error).

    Raises:
        FileAccessError: si el archivo no existe, es una carpeta, supera el
            tamaño máximo, no hay permisos, no está en UTF-8 u ocurre otro
            error del sistema operativo.
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileAccessError(f"El archivo no existe: {file_path}")
    if file_path.is_dir():
        raise FileAccessError(f"La ruta corresponde a una carpeta, no a un archivo: {file_path}")

    try:
        size = file_path.stat().st_size
        if size > max_size_bytes:
            raise FileAccessError(
                f"El archivo pesa {size} bytes y el máximo admitido es {max_size_bytes} bytes."
            )
        with file_path.open("r", encoding=READ_ENCODING) as file:
            return file.read()
    except PermissionError as error:
        raise FileAccessError(f"No hay permisos para leer el archivo: {file_path}") from error
    except UnicodeDecodeError as error:
        raise FileAccessError(
            f"El archivo no está codificado en UTF-8 (byte inválido en la posición {error.start}). "
            "Guardalo como UTF-8 e intentá de nuevo."
        ) from error
    except OSError as error:
        reason = error.strerror or str(error)
        raise FileAccessError(f"No se pudo leer el archivo {file_path}: {reason}") from error


def ensure_directory(directory: PathLike) -> Path:
    """Crea la carpeta (y sus carpetas padre) si no existe.

    Raises:
        FileAccessError: si existe un archivo con ese nombre o no hay permisos.
    """
    folder = Path(directory)
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except FileExistsError as error:
        raise FileAccessError(
            f"No se puede usar '{folder}' como carpeta porque ya existe un archivo con ese nombre."
        ) from error
    except PermissionError as error:
        raise FileAccessError(f"No hay permisos para crear la carpeta: {folder}") from error
    except OSError as error:
        reason = error.strerror or str(error)
        raise FileAccessError(f"No se pudo crear la carpeta {folder}: {reason}") from error
    return folder


def write_new_text_file(directory: PathLike, filename: str, content: str) -> Path:
    """Escribe ``content`` en un archivo NUEVO dentro de ``directory``.

    Política de no sobrescritura: si ``filename`` ya existe, se prueba con
    ``nombre_1.ext``, ``nombre_2.ext``, etc. El modo "x" de ``open`` garantiza
    que nunca se pisa un archivo existente, incluso si otro programa lo crea
    al mismo tiempo.

    Returns:
        La ruta del archivo efectivamente creado.

    Raises:
        FileAccessError: si no se puede crear la carpeta o escribir el archivo.
    """
    folder = ensure_directory(directory)
    base_name = Path(filename)
    stem = base_name.stem
    suffix = base_name.suffix

    candidate = folder / filename
    attempt = 1
    while True:
        try:
            with candidate.open("x", encoding=WRITE_ENCODING) as file:
                file.write(content)
            return candidate
        except FileExistsError:
            if attempt > MAX_NAME_ATTEMPTS:
                raise FileAccessError(
                    f"No se encontró un nombre libre para '{filename}' en {folder}."
                ) from None
            candidate = folder / f"{stem}_{attempt}{suffix}"
            attempt += 1
        except PermissionError as error:
            raise FileAccessError(f"No hay permisos para escribir en: {folder}") from error
        except OSError as error:
            reason = error.strerror or str(error)
            raise FileAccessError(f"No se pudo escribir el archivo {candidate}: {reason}") from error
