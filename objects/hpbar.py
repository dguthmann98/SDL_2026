import pygame as pg

from objects.fonts import get_medieval_font


class HpBar:
	"""Zeigt die Boss-Lebenspunkte als Leiste am unteren Bildschirmrand."""

	def __init__(
		self,
		max_hp: int = 61,
		current_hp: int | None = None,
		height: int = 26,
		margin: int = 20,
		background_color=(45, 45, 45),
		fill_color=(190, 45, 45),
		border_color=(220, 220, 220),
		text_color=(245, 245, 245),
		chip_color=(230, 200, 70),
		border_width: int = 2,
		chip_speed: float = 3.0,
	):
		self.max_hp = max(1, max_hp)
		self.current_hp = self.max_hp if current_hp is None else int(current_hp)
		self.display_hp = float(self.current_hp)
		self.height = height
		self.margin = margin
		self.background_color = background_color
		self.fill_color = fill_color
		self.chip_color = chip_color
		self.border_color = border_color
		self.text_color = text_color
		self.border_width = border_width
		self.chip_speed = chip_speed
		self.font = get_medieval_font(28)
		self.current_hp = max(0, min(self.current_hp, self.max_hp))
		self.display_hp = max(float(self.current_hp), min(self.display_hp, float(self.max_hp)))

	def reset(self) -> None:
		self.current_hp = self.max_hp
		self.display_hp = float(self.max_hp)

	def set_hp(self, hp: int) -> None:
		new_hp = max(0, min(int(hp), self.max_hp))
		self.current_hp = new_hp
		self.display_hp = float(new_hp)

	def damage(self, amount: int, animate: bool = True) -> None:
		amount_value = max(0, int(amount))
		new_hp = max(0, self.current_hp - amount_value)

		if animate and new_hp < self.current_hp:
			self.display_hp = max(self.display_hp, float(self.current_hp))
			self.current_hp = new_hp
		else:
			self.current_hp = new_hp
			self.display_hp = float(new_hp)

	def update(self, dt: float) -> None:
		if self.display_hp <= self.current_hp:
			self.display_hp = float(self.current_hp)
			return

		self.display_hp -= self.chip_speed * dt
		if self.display_hp < self.current_hp:
			self.display_hp = float(self.current_hp)

	def is_animating(self) -> bool:
		return self.display_hp > self.current_hp

	def draw(self, surface: pg.Surface) -> None:
		width = surface.get_width() - (self.margin * 2)
		x = self.margin
		y = surface.get_height() - self.margin - self.height

		bar_rect = pg.Rect(x, y, width, self.height)
		pg.draw.rect(surface, self.background_color, bar_rect, border_radius=8)

		display_ratio = self.display_hp / self.max_hp
		display_width = int(width * display_ratio)
		if display_width > 0:
			display_rect = pg.Rect(x, y, display_width, self.height)
			pg.draw.rect(surface, self.fill_color, display_rect, border_radius=8)

		hp_ratio = self.current_hp / self.max_hp
		fill_width = int(width * hp_ratio)
		if fill_width > 0:
			fill_rect = pg.Rect(x, y, fill_width, self.height)
			pg.draw.rect(surface, self.fill_color, fill_rect, border_radius=8)

		chip_width = display_width - fill_width
		if chip_width > 0:
			chip_rect = pg.Rect(x + fill_width, y, chip_width, self.height)
			pg.draw.rect(surface, self.chip_color, chip_rect, border_radius=8)

		pg.draw.rect(surface, self.border_color, bar_rect, self.border_width, border_radius=8)

		label = self.font.render(f"HP: {self.current_hp}/{self.max_hp}", True, self.text_color)
		label_rect = label.get_rect(midleft=(x + 12, y + (self.height // 2)))
		surface.blit(label, label_rect)
