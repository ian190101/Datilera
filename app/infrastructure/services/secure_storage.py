from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config.settings import get_settings


@dataclass(frozen=True, slots=True)
class StoredFile:
    relative_path: str
    public_url: str
    size: int
    mime_type: str


class SecureStorageService:
    """Almacena archivos con nombres propios y valida contenido, tamaño y destino."""

    MIME_SIGNATURES = {
        "image/jpeg": (b"\xff\xd8\xff",),
        "image/png": (b"\x89PNG\r\n\x1a\n",),
        "image/webp": (b"RIFF",),
        "application/pdf": (b"%PDF-",),
        "video/mp4": (b"",),
    }
    EXTENSIONS = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "application/pdf": ".pdf",
        "video/mp4": ".mp4",
    }

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or get_settings().MEDIA_DIR).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    async def save_upload(
        self,
        upload: UploadFile,
        subdirectory: str,
        *,
        allowed_mime_types: set[str] | None = None,
        max_bytes: int = 10 * 1024 * 1024,
        url_prefix: str = "/media",
    ) -> StoredFile:
        allowed = allowed_mime_types or set(self.MIME_SIGNATURES)
        first_chunk = await upload.read(64 * 1024)
        detected = self._detect_mime(first_chunk)
        if detected not in allowed:
            raise HTTPException(status_code=415, detail="Tipo de archivo no permitido")

        safe_directory = self._safe_directory(subdirectory)
        filename = f"{uuid.uuid4().hex}{self.EXTENSIONS[detected]}"
        destination = (safe_directory / filename).resolve()
        self._ensure_within_root(destination)

        size = 0
        try:
            with destination.open("xb") as output:
                chunk = first_chunk
                while chunk:
                    size += len(chunk)
                    if size > max_bytes:
                        raise HTTPException(status_code=413, detail="El archivo supera el tamaño permitido")
                    output.write(chunk)
                    chunk = await upload.read(64 * 1024)
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        finally:
            await upload.close()

        relative = destination.relative_to(self.root).as_posix()
        return StoredFile(
            relative_path=relative,
            public_url=f"{url_prefix}/{relative}",
            size=size,
            mime_type=detected,
        )

    def resolve_for_read(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        self._ensure_within_root(candidate)
        if not candidate.is_file():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")
        return candidate

    def _safe_directory(self, subdirectory: str) -> Path:
        clean_parts = [part for part in Path(subdirectory).parts if part not in {"", ".", ".."}]
        directory = (self.root.joinpath(*clean_parts)).resolve()
        self._ensure_within_root(directory)
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def _ensure_within_root(self, path: Path) -> None:
        if path != self.root and self.root not in path.parents:
            raise HTTPException(status_code=400, detail="Ruta de archivo inválida")

    def _detect_mime(self, content: bytes) -> str:
        if len(content) >= 12 and content[4:8] == b"ftyp":
            return "video/mp4"
        for mime, signatures in self.MIME_SIGNATURES.items():
            if mime == "video/mp4":
                continue
            if mime == "image/webp":
                if len(content) >= 12 and content.startswith(b"RIFF") and content[8:12] == b"WEBP":
                    return mime
                continue
            if any(content.startswith(signature) for signature in signatures):
                return mime
        return "application/octet-stream"
