import pygame as pg

from games.standard_game import StandardGame
from objects.button import Button
from objects.fonts import get_medieval_font
from objects.hpbar import HpBar
from objects.save_manager import SaveManager

class Game:
    def __init__(self):
        """Initialize the game and create menu buttons."""
        pg.init()
        pg.display.set_caption("Bossfight")
        self.screen = pg.display.set_mode((800, 600))
        self.clock = pg.time.Clock()
        self.delta_time = 1 / 60
        self.running = True

        self.state = "menu"
        self.font_title = get_medieval_font(72, bold=True)
        self.font_text = get_medieval_font(34)
        self.font_small = get_medieval_font(28)
        self.buttons = []
        self.boss_hp_bar = HpBar(max_hp=61)
        self.save_manager = SaveManager()
        self.standard_game_templates = [
            {"n": 1, "name": "Schnellraten", "rules": "Ein Begriff wird gezeigt. Das Team mit der schnelleren richtigen Antwort gewinnt das Spiel."},
            {"n": 2, "name": "Reaktionsduell", "rules": "Bei Signal sofort klicken. Das schnellere Team gewinnt dieses Spiel."},
            {"n": 3, "name": "Gedaechtnis-Challenge", "rules": "Bilder oder Symbole werden kurz gezeigt. Das Team mit mehr korrekten Erinnerungen gewinnt."},
            {"n": 4, "name": "Geschwindigkeit", "rules": "Schnelle Aufgaben loesen. Das schnellere Team gewinnt dieses Spiel."},
            {"n": 5, "name": "Quizduell", "rules": "Fragen beantworten. Das Team mit mehr richtigen Antworten gewinnt dieses Spiel."},
            {"n": 6, "name": "Logik-Raetsel", "rules": "Logische Aufgaben sofort loesen. Das schnellere Team gewinnt dieses Spiel."},
            {"n": 7, "name": "Reaktions-Sprint", "rules": "Extreme Geschwindigkeit erforderlich. Das Team mit der schnellsten Reaktion gewinnt."},
            {"n": 8, "name": "Wort-Challenge", "rules": "Woerter in kurzer Zeit sammeln. Das Team mit den meisten Woertern gewinnt."},
            {"n": 9, "name": "Zahlen-Spiel", "rules": "Schnelle Rechnung oder Kombinationen. Das Team mit den korrekten Loesungen gewinnt."},
            {"n": 10, "name": "Finale Challenge", "rules": "Kombiniert alle vorherigen Skills. Das schnellere und bessere Team gewinnt das Finale."},
        ]
        self.current_standard_index = 0
        self.active_standard_game = None
        self.score = {"champions": 0, "gamer": 0}
        self._create_main_menu_buttons()

    def _create_main_menu_buttons(self):
        button_width = 240
        button_height = 60
        center_x = self.screen.get_width() // 2 - button_width // 2

        self.buttons = [
            Button(
                center_x,
                200,
                button_width,
                button_height,
                action="start",
                text="Start",
                button_color=(25, 60, 30),
                hover_color=(40, 100, 50),
                border_color=(180, 240, 190),
                border_width=2,
            ),
        ]

        if self.save_manager.has_save():
            self.buttons.append(
                Button(
                    center_x,
                    270,
                    button_width,
                    button_height,
                    action="continue",
                    text="Weiter",
                    button_color=(30, 50, 80),
                    hover_color=(50, 80, 120),
                    border_color=(180, 200, 240),
                    border_width=2,
                )
            )

        self.buttons.append(
            Button(
                center_x,
                340 if self.save_manager.has_save() else 270,
                button_width,
                button_height,
                action="quit",
                text="Beenden",
                button_color=(70, 25, 25),
                hover_color=(120, 40, 40),
                border_color=(240, 185, 185),
                border_width=2,
            )
        )

    def _handle_menu_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                action = button.get_action()
                if action == "start":
                    self._start_standard_game_series()
                elif action == "continue":
                    self._continue_from_save()
                elif action == "quit":
                    self.running = False

    def _handle_game_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.state = "menu"

    def _start_standard_game_series(self):
        self.boss_hp_bar.reset()
        self.current_standard_index = 0
        self.score = {"champions": 0, "gamer": 0}
        self.save_manager.delete_save()
        self._load_active_standard_game()
        self.state = "game"

    def _continue_from_save(self):
        save_data = self.save_manager.load_game()
        if save_data is None:
            self._start_standard_game_series()
            return

        self.current_standard_index = save_data["current_index"]
        self.score = {"champions": save_data["champions_score"], "gamer": save_data["gamer_score"]}
        self.boss_hp_bar.set_hp(save_data["boss_hp"])
        self._load_active_standard_game()
        self.state = "game"

    def _load_active_standard_game(self):
        if self.current_standard_index >= len(self.standard_game_templates):
            self.active_standard_game = None
            self.save_manager.delete_save()
            self.state = "series_result"
            return

        template = self.standard_game_templates[self.current_standard_index]
        self.active_standard_game = StandardGame(
            n=template["n"],
            name=template["name"],
            rules_text=template["rules"],
            hp_bar=self.boss_hp_bar,
            screen=self.screen,
        )

    def _finish_active_standard_game(self):
        if self.active_standard_game is None:
            return

        result = self.active_standard_game.get_result()
        winner = result["winner"]
        points = result["points"]
        if winner in self.score:
            self.score[winner] += points

        self.current_standard_index += 1

        self.save_manager.save_game(
            self.current_standard_index,
            self.score["champions"],
            self.score["gamer"],
            self.boss_hp_bar.current_hp,
        )

        self._load_active_standard_game()

    def _handle_standard_series_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.state = "menu"
            return

        if self.active_standard_game is None:
            return

        self.active_standard_game.handle_event(event)
        if self.active_standard_game.is_finished():
            self._finish_active_standard_game()

    def _handle_series_result_event(self, event):
        if event.type == pg.KEYDOWN and event.key in (pg.K_RETURN, pg.K_ESCAPE):
            self.state = "menu"

    def _draw_menu(self):
        self.screen.fill((12, 16, 22))

        self._create_main_menu_buttons()

        title_surface = self.font_title.render("Hauptmenu", True, (235, 235, 235))
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 140))
        self.screen.blit(title_surface, title_rect)

        for button in self.buttons:
            button.update()
            button.draw(self.screen)

    def _draw_game(self):
        if self.active_standard_game is None:
            self.screen.fill((0, 0, 0))
            self.boss_hp_bar.draw(self.screen)
            return

        self.active_standard_game.update(self.delta_time)
        self.active_standard_game.draw()

    def _draw_series_result(self):
        self.screen.fill((8, 10, 14))

        title = self.font_title.render("10 Standardspiele fertig", True, (235, 235, 235))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title, title_rect)

        champions_line = self.font_text.render(f"Champions: {self.score['champions']} Punkte", True, (210, 225, 255))
        champions_rect = champions_line.get_rect(center=(self.screen.get_width() // 2, 260))
        self.screen.blit(champions_line, champions_rect)

        gamer_line = self.font_text.render(f"Gamer: {self.score['gamer']} Punkte", True, (210, 255, 220))
        gamer_rect = gamer_line.get_rect(center=(self.screen.get_width() // 2, 310))
        self.screen.blit(gamer_line, gamer_rect)

        hp_line = self.font_text.render(f"Boss HP: {self.boss_hp_bar.current_hp}/{self.boss_hp_bar.max_hp}", True, (240, 240, 240))
        hp_rect = hp_line.get_rect(center=(self.screen.get_width() // 2, 360))
        self.screen.blit(hp_line, hp_rect)

        hint = self.font_small.render("ENTER oder ESC fuer Hauptmenu", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(self.screen.get_width() // 2, 460))
        self.screen.blit(hint, hint_rect)

        self.boss_hp_bar.draw(self.screen)

    def run(self):
        """Main game loop."""
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                if self.state == "menu":
                    self._handle_menu_event(event)
                elif self.state == "game":
                    self._handle_standard_series_event(event)
                elif self.state == "series_result":
                    self._handle_series_result_event(event)

            if self.state == "menu":
                self._draw_menu()
            elif self.state == "game":
                self._draw_game()
            elif self.state == "series_result":
                self._draw_series_result()

            pg.display.flip()
            self.delta_time = self.clock.tick(60) / 1000.0

        pg.quit()
        

if __name__ == "__main__":
    game = Game()
    game.run()

