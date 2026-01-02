# app/infrastructure/storage/watermarker.py
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont


class Watermarker:
    """
    Servicio para aplicar marca de agua a imágenes.
    Soporta:
    - Marca de texto en esquina o centrada.
    - Opacidad configurable.
    - Opcional: logo semi-transparente (por ahora preparado, lo puedes activar luego).
    """

    def __init__(
        self,
        text: str = "Datilera",
        opacity: int = 90,
        position: str = "bottom-right",  # 'bottom-right', 'bottom-left', 'top-right', 'top-left', 'center'
        margin: int = 16,
        logo_path: Optional[str] = None,
        logo_scale: float = 0.25,  # proporción del ancho de la imagen
    ) -> None:
        self.text = text
        self.opacity = max(0, min(opacity, 255))
        self.position = position
        self.margin = margin
        self.logo_path = Path(logo_path).resolve() if logo_path else None
        self.logo_scale = logo_scale

    # -------- API principal --------

    def apply_watermark(self, image_path: str | Path) -> None:
        """
        Aplica watermark in-place sobre la imagen indicada.
        Si el archivo no es imagen válida, no hace nada.
        """
        path = Path(image_path)
        if not path.exists():
            return

        try:
            image = Image.open(path).convert("RGBA")
        except Exception:
            # Archivo no soportado o corrupto
            return{"Arcivo no soportado o corrupto"}


        width, height = image.size

        # Capa transparente donde dibujaremos watermark
        overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        # 1) Marca de texto
        self._draw_text_watermark(draw, width, height)

        # 2) Marca de logo (si se configuró)
        if self.logo_path and self.logo_path.exists():
            self._draw_logo_watermark(overlay, width, height)

        # Componer y guardar
        result = Image.alpha_composite(image, overlay).convert("RGB")
        result.save(path)

    # -------- Helpers internos --------

    def _draw_text_watermark(self, draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
        # Tamaño de fuente relativo al ancho
        font_size = max(16, width // 20)
        font = self._load_font(font_size)

        text_w, text_h = draw.textsize(self.text, font=font)
        x, y = self._calculate_position(width, height, text_w, text_h)

        draw.text(
            (x, y),
            self.text,
            font=font,
            fill=(255, 255, 255, self.opacity),
            stroke_width=1,
            stroke_fill=(0, 0, 0, self.opacity),
        )

    def _load_font(self, font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        # Intenta usar una fuente TTF, si no, fallback a default.
        for font_name in ["arial.ttf", "DejaVuSans.ttf"]:
            try:
                return ImageFont.truetype(font_name, font_size)
            except Exception:
                continue
        return ImageFont.load_default()

    def _calculate_position(self, width: int, height: int, w: int, h: int) -> Tuple[int, int]:
        m = self.margin
        pos = self.position

        if pos == "bottom-right":
            return width - w - m, height - h - m
        if pos == "bottom-left":
            return m, height - h - m
        if pos == "top-right":
            return width - w - m, m
        if pos == "top-left":
            return m, m
        # center
        return (width - w) // 2, (height - h) // 2

    def _draw_logo_watermark(self, overlay: Image.Image, width: int, height: int) -> None:
        try:
            logo = Image.open(self.logo_path).convert("RGBA")
        except Exception:
            return

        # Escalar logo a porcentaje del ancho
        target_width = int(width * self.logo_scale)
        ratio = target_width / logo.width
        target_height = int(logo.height * ratio)
        logo = logo.resize((target_width, target_height), Image.LANCZOS)

        # Aplicar opacidad
        alpha = logo.split()[3]
        alpha = alpha.point(lambda p: p * (self.opacity / 255.0))
        logo.putalpha(alpha)

        logo_w, logo_h = logo.size
        x, y = self._calculate_position(width, height, logo_w, logo_h)

        overlay.paste(logo, (x, y), logo)
