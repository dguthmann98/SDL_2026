import pygame as pg
from functools import lru_cache


@lru_cache(maxsize=8)
def _find_medieval_font_path(bold: bool, italic: bool):
    """Finds a decorative serif-like font and falls back safely."""
    candidates = [
        "Cinzel",
        "Old English Text MT",
        "Goudy Old Style",
        "Book Antiqua",
        "Garamond",
        "Palatino Linotype",
        "Cambria",
        "Times New Roman",
    ]

    for font_name in candidates:
        font_path = pg.font.match_font(font_name, bold=bold, italic=italic)
        if font_path:
            return font_path

    return None


def get_medieval_font(size: int, bold: bool = False, italic: bool = False) -> pg.font.Font:
    """Returns a medieval-style font when available, otherwise serif fallback."""
    font_path = _find_medieval_font_path(bold=bold, italic=italic)
    if font_path:
        return pg.font.Font(font_path, size)

    return pg.font.SysFont("serif", size, bold=bold, italic=italic)
