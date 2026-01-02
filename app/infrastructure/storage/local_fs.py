# app/infrastructure/storage/localfs.py
from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Optional

from app.config.settings import Settings  # Debe definir MEDIA_ROOT


class LocalFileStorage:
    """
    Storage local en disco.
    - Guarda rutas relativas en BD.
    - Maneja creación de directorios, borrado y versiones de archivo.
    """

    def __init__(self, base_dir: Optional[str] = None) -> None:
        media_dir = base_dir or getattr(Settings, "MEDIA_DIR", "media")
        self.base_path = Path(media_dir).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    # -------- Helpers internos --------

    def _to_full_path(self, relative_path: str) -> Path:
        # Evitar path traversal
        rel = Path(relative_path.lstrip("/"))
        full = (self.base_path / rel).resolve()
        if self.base_path not in full.parents and self.base_path != full:
            raise ValueError("Ruta fuera de MEDIA_ROOT")
        return full

    def ensure_dir_for(self, relative_path: str) -> Path:
        full = self._to_full_path(relative_path)
        full.parent.mkdir(parents=True, exist_ok=True)
        return full

    # -------- API pública --------

    def save_bytes(self, relative_path: str, data: bytes, overwrite: bool = False) -> str:
        """
        Guarda un archivo desde bytes.
        Si overwrite=False y existe, genera nombre versionado file(1).ext, file(2).ext, etc.
        Retorna la ruta relativa final.
        """
        full = self.ensure_dir_for(relative_path)

        if full.exists() and not overwrite:
            full = self._versioned_path(full)

        full.write_bytes(data)
        # Retornar ruta relativa normalizada respecto a base_path
        rel = full.relative_to(self.base_path).as_posix()
        return rel

    def save_fileobj(
        self,
        relative_path: str,
        fileobj: BinaryIO,
        overwrite: bool = False,
        chunk_size: int = 64 * 1024,
    ) -> str:
        """
        Guarda un archivo desde un file-like object (por ejemplo UploadFile.file).
        """
        full = self.ensure_dir_for(relative_path)

        if full.exists() and not overwrite:
            full = self._versioned_path(full)

        with full.open("wb") as f:
            while True:
                chunk = fileobj.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)

        rel = full.relative_to(self.base_path).as_posix()
        return rel

    def read_bytes(self, relative_path: str) -> bytes:
        """
        Lee un archivo y retorna sus bytes.
        Lanza FileNotFoundError si no existe.
        """
        full = self._to_full_path(relative_path)
        return full.read_bytes()

    def exists(self, relative_path: str) -> bool:
        full = self._to_full_path(relative_path)
        return full.exists()

    def delete(self, relative_path: str) -> None:
        """
        Elimina un archivo si existe. No elimina directorios.
        """
        full = self._to_full_path(relative_path)
        if full.exists():
            try:
                full.unlink()
            except Exception:
                # Se puede loguear el error, pero no romper flujo de negocio.
                pass

    def get_full_path(self, relative_path: str) -> Path:
        """
        Devuelve la ruta absoluta en disco (para pasársela a otros servicios).
        """
        return self._to_full_path(relative_path)

    # -------- Versionado --------

    def _versioned_path(self, full: Path) -> Path:
        """
        Genera un nombre versionado: file.ext -> file(1).ext, file(2).ext, ...
        """
        parent = full.parent
        stem = full.stem
        suffix = full.suffix

        index = 1
        while True:
            candidate = parent / f"{stem}({index}){suffix}"
            if not candidate.exists():
                return candidate
            index += 1
