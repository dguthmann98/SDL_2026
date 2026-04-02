import pygame as pg
from typing import Callable, Optional, Tuple

from objects.fonts import get_medieval_font

class Button:
    """Wiederverwendbarer UI-Button fuer Menues und andere Screens."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        action: Optional[str] = None,
        text: str = "",
        font_size: int = 30,
        text_color: Tuple[int, int, int] = (255, 255, 255),
        button_color: Tuple[int, int, int] = (30, 30, 30),
        hover_color: Tuple[int, int, int] = (55, 55, 55),
        disabled_color: Tuple[int, int, int] = (90, 90, 90),
        border_color: Optional[Tuple[int, int, int]] = None,
        border_width: int = 0,
        border_radius: int = 8,
        sound=None,
        on_click: Optional[Callable[["Button"], None]] = None,
        enabled: bool = True,
    ):
        self.rect = pg.Rect(x, y, width, height)
        self.action = action
        self.text = text or ""
        self.font_size = font_size
        self.text_color = text_color
        self.button_color = button_color
        self.hover_color = hover_color
        self.disabled_color = disabled_color
        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.sound = sound
        self.on_click = on_click
        self.enabled = enabled

        self._hovered = False
        self._font = get_medieval_font(self.font_size)

    def update(self, mouse_pos: Optional[Tuple[int, int]] = None) -> None:
        """Aktualisiert den Hover-Status des Buttons."""
        if mouse_pos is None:
            mouse_pos = pg.mouse.get_pos()
        self._hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pg.Surface) -> None:
        """Zeichnet den Button inklusive Text."""
        if not self.enabled:
            current_color = self.disabled_color
        elif self._hovered:
            current_color = self.hover_color
        else:
            current_color = self.button_color

        pg.draw.rect(surface, current_color, self.rect, border_radius=self.border_radius)

        if self.border_color is not None and self.border_width > 0:
            pg.draw.rect(
                surface,
                self.border_color,
                self.rect,
                width=self.border_width,
                border_radius=self.border_radius,
            )

        if self.text:
            text_surface = self._font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

    def handle_event(self, event: pg.event.Event) -> bool:
        """Verarbeitet Events. Gibt True zurueck, wenn geklickt wurde."""
        if not self.enabled:
            return False

        if event.type == pg.MOUSEMOTION:
            self.update(event.pos)

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.sound:
                    self.sound.play()
                if self.on_click:
                    self.on_click(self)
                return True

        return False

    def get_action(self) -> Optional[str]:
        """Gibt die verknuepfte Action-ID zurueck."""
        return self.action

    def set_enabled(self, enabled: bool) -> None:
        """Aktiviert oder deaktiviert den Button."""
        self.enabled = enabled




    
