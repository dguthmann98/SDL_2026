import pygame as pg

from objects.button import Button
from objects.fonts import get_medieval_font


class StandardGame:
	"""Vorlage fuer ein einzelnes Standardspiel im Bossfight."""

	PHASE_TITLE = "title"
	PHASE_RULES = "rules"
	PHASE_FRAME = "frame"
	PHASE_DAMAGE_CONFIRM = "damage_confirm"
	PHASE_RESULT = "result"
	PHASE_FINISHED = "finished"

	def __init__(self, n: int, name: str, rules_text: str, hp_bar, screen: pg.Surface):
		self.n = max(1, int(n))
		self.name = name
		self.rules_text = rules_text
		self.hp_bar = hp_bar
		self.screen = screen

		self.phase = self.PHASE_TITLE
		self.finished = False
		self.winner = None
		self._hp_before_result = self.hp_bar.current_hp
		self.points_awarded = self.n

		self.font_title = get_medieval_font(64, bold=True)
		self.font_text = get_medieval_font(36)
		self.font_hint = get_medieval_font(28)

		self.winner_buttons = []
		self._create_winner_buttons()

	def _create_winner_buttons(self) -> None:
		button_width = 270
		button_height = 64
		spacing = 22
		total_width = (button_width * 2) + spacing
		start_x = self.screen.get_width() // 2 - total_width // 2
		y = self.screen.get_height() // 2 + 35

		self.winner_buttons = [
			Button(
				start_x,
				y,
				button_width,
				button_height,
				action="champions",
				text="Champions",
				button_color=(24, 52, 98),
				hover_color=(40, 82, 150),
				border_color=(195, 220, 255),
				border_width=2,
			),
			Button(
				start_x + button_width + spacing,
				y,
				button_width,
				button_height,
				action="gamer",
				text="Gamer",
				button_color=(25, 80, 35),
				hover_color=(45, 130, 60),
				border_color=(190, 250, 200),
				border_width=2,
			),
		]

	def reset(self) -> None:
		self.phase = self.PHASE_TITLE
		self.finished = False
		self.winner = None
		self._hp_before_result = self.hp_bar.current_hp

	def handle_event(self, event: pg.event.Event) -> None:
		if self.phase == self.PHASE_FINISHED:
			return

		if event.type == pg.KEYDOWN and event.key in (pg.K_RIGHT, pg.K_BACKSPACE):
			if self.phase == self.PHASE_RULES:
				self.phase = self.PHASE_TITLE
				return
			if self.phase == self.PHASE_FRAME:
				self.phase = self.PHASE_RULES
				return
			if self.phase == self.PHASE_DAMAGE_CONFIRM:
				self._go_back_from_result()
				return
			if self.phase == self.PHASE_RESULT:
				self._go_back_from_result()
				return

		if event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
			if self.phase == self.PHASE_TITLE:
				self.phase = self.PHASE_RULES
				return
			if self.phase == self.PHASE_RULES:
				self.phase = self.PHASE_FRAME
				return
			if self.phase == self.PHASE_DAMAGE_CONFIRM:
				self._apply_damage_and_animate()
				return
			if self.phase == self.PHASE_RESULT:
				if not self.hp_bar.is_animating():
					self.phase = self.PHASE_FINISHED
					self.finished = True
				return

		if self.phase != self.PHASE_FRAME:
			return

		for button in self.winner_buttons:
			if button.handle_event(event):
				self._set_winner(button.get_action())
				return

	def _set_winner(self, winner: str) -> None:
		self._hp_before_result = self.hp_bar.current_hp
		self.winner = winner
		self.phase = self.PHASE_DAMAGE_CONFIRM

	def _apply_damage_and_animate(self) -> None:
		if self.winner == "gamer":
			self.hp_bar.damage(self.n, animate=True)
		self.phase = self.PHASE_RESULT

	def _go_back_from_result(self) -> None:
		if self.winner == "gamer":
			self.hp_bar.set_hp(self._hp_before_result)

		self.winner = None
		if self.phase == self.PHASE_DAMAGE_CONFIRM:
			self.phase = self.PHASE_FRAME
		else:
			self.phase = self.PHASE_FRAME

	def _skip_result(self) -> None:
		"""Nutzt man, um ein Spiel sofort abzuschliessen (z. B. Abbruch)."""
		self.phase = self.PHASE_FINISHED
		self.finished = True

	def update(self, dt: float = 0.0) -> None:
		self.hp_bar.update(dt)

		if self.phase == self.PHASE_FRAME:
			for button in self.winner_buttons:
				button.update()

	def is_finished(self) -> bool:
		return self.finished

	def get_result(self) -> dict:
		"""Liefert Ergebnisdaten fuer die Spielverwaltung."""
		return {
			"game_number": self.n,
			"winner": self.winner,
			"points": self.points_awarded,
			"damage_to_boss": self.n if self.winner == "gamer" else 0,
		}

	def draw(self) -> None:
		self.screen.fill((8, 10, 14))

		if self.phase == self.PHASE_TITLE:
			self._draw_title_phase()
		elif self.phase == self.PHASE_RULES:
			self._draw_rules_phase()
		elif self.phase == self.PHASE_FRAME:
			self._draw_frame_phase()
		elif self.phase == self.PHASE_DAMAGE_CONFIRM:
			self._draw_damage_confirm_phase()
		elif self.phase in (self.PHASE_RESULT, self.PHASE_FINISHED):
			self._draw_result_phase()

		self.hp_bar.draw(self.screen)

	def _draw_title_phase(self) -> None:
		title = f"Spiel {self.n}: {self.name}"
		title_surface = self.font_title.render(title, True, (235, 235, 235))
		title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 220))
		self.screen.blit(title_surface, title_rect)

		hint = self.font_hint.render("ENTER fuer Regeln", True, (200, 200, 200))
		hint_rect = hint.get_rect(center=(self.screen.get_width() // 2, 290))
		self.screen.blit(hint, hint_rect)

	def _draw_rules_phase(self) -> None:
		heading = self.font_title.render("Regeln", True, (235, 235, 235))
		heading_rect = heading.get_rect(center=(self.screen.get_width() // 2, 120))
		self.screen.blit(heading, heading_rect)

		wrapped_lines = self._wrap_text(self.rules_text, self.font_text, self.screen.get_width() - 120)
		y = 200
		for line in wrapped_lines:
			line_surface = self.font_text.render(line, True, (220, 220, 220))
			line_rect = line_surface.get_rect(center=(self.screen.get_width() // 2, y))
			self.screen.blit(line_surface, line_rect)
			y += 42

		hint = self.font_hint.render("ENTER fuer Hauptframe", True, (200, 200, 200))
		hint_rect = hint.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 80))
		self.screen.blit(hint, hint_rect)

		back_hint = self.font_hint.render("Pfeil rechts: zurueck", True, (180, 180, 180))
		back_hint_rect = back_hint.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 48))
		self.screen.blit(back_hint, back_hint_rect)

	def _draw_frame_phase(self) -> None:
		title = self.font_title.render(f"Spiel {self.n}: {self.name}", True, (235, 235, 235))
		title_rect = title.get_rect(center=(self.screen.get_width() // 2, 120))
		self.screen.blit(title, title_rect)

		prompt = self.font_text.render("Wer hat gewonnen?", True, (220, 220, 220))
		prompt_rect = prompt.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 20))
		self.screen.blit(prompt, prompt_rect)

		for button in self.winner_buttons:
			button.draw(self.screen)

		info = f"Dieses Spiel ist {self.points_awarded} Punkt(e) wert."
		info_surface = self.font_hint.render(info, True, (205, 205, 205))
		info_rect = info_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 130))
		self.screen.blit(info_surface, info_rect)

		back_hint = self.font_hint.render("Pfeil rechts: zurueck", True, (180, 180, 180))
		back_hint_rect = back_hint.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 168))
		self.screen.blit(back_hint, back_hint_rect)

	def _draw_damage_confirm_phase(self) -> None:
		title = self.font_title.render(f"Spiel {self.n}", True, (235, 235, 235))
		title_rect = title.get_rect(center=(self.screen.get_width() // 2, 120))
		self.screen.blit(title, title_rect)

		if self.winner == "gamer":
			result_text = f"Gamer gewinnen - {self.n} Schaden"
			result_color = (230, 210, 110)
		else:
			result_text = "Champions gewinnen - kein Schaden"
			result_color = (200, 220, 255)

		result_surface = self.font_text.render(result_text, True, result_color)
		result_rect = result_surface.get_rect(center=(self.screen.get_width() // 2, 280))
		self.screen.blit(result_surface, result_rect)

		hint = self.font_hint.render("ENTER fuer Schaden-Animation", True, (200, 200, 200))
		hint_rect = hint.get_rect(center=(self.screen.get_width() // 2, 370))
		self.screen.blit(hint, hint_rect)

		back_hint = self.font_hint.render("Pfeil rechts: zurueck", True, (180, 180, 180))
		back_hint_rect = back_hint.get_rect(center=(self.screen.get_width() // 2, 410))
		self.screen.blit(back_hint, back_hint_rect)

	def _draw_result_phase(self) -> None:
		title = self.font_title.render(f"Spiel {self.n} beendet", True, (235, 235, 235))
		title_rect = title.get_rect(center=(self.screen.get_width() // 2, 130))
		self.screen.blit(title, title_rect)

		if self.winner == "gamer":
			result_text = f"Gamer gewinnen - Boss erleidet {self.n} Schaden"
			result_color = (230, 210, 110)
		else:
			result_text = "Champions gewinnen - kein Boss-Schaden"
			result_color = (200, 220, 255)

		result_surface = self.font_text.render(result_text, True, result_color)
		result_rect = result_surface.get_rect(center=(self.screen.get_width() // 2, 250))
		self.screen.blit(result_surface, result_rect)

		if self.hp_bar.is_animating():
			hint_text = "Schaden wird angewendet..."
		else:
			hint_text = "ENTER fuer naechstes Spiel"

		hint_surface = self.font_hint.render(hint_text, True, (200, 200, 200))
		hint_rect = hint_surface.get_rect(center=(self.screen.get_width() // 2, 330))
		self.screen.blit(hint_surface, hint_rect)

		back_hint = self.font_hint.render("Pfeil rechts: zurueck", True, (180, 180, 180))
		back_hint_rect = back_hint.get_rect(center=(self.screen.get_width() // 2, 370))
		self.screen.blit(back_hint, back_hint_rect)

	@staticmethod
	def _wrap_text(text: str, font: pg.font.Font, max_width: int) -> list[str]:
		words = text.split()
		if not words:
			return [""]

		lines = []
		current_line = words[0]
		for word in words[1:]:
			candidate = f"{current_line} {word}"
			if font.size(candidate)[0] <= max_width:
				current_line = candidate
			else:
				lines.append(current_line)
				current_line = word
		lines.append(current_line)
		return lines
