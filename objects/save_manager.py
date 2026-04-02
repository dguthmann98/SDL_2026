import json
import os
from pathlib import Path


class SaveManager:
    """Verwaltet Speicherstände für das Spiel."""

    SAVE_FILE = "bossfight_save.json"

    def __init__(self):
        script_dir = Path(__file__).parent.parent
        self.save_path = script_dir / self.SAVE_FILE

    def save_game(
        self,
        current_index: int,
        champions_score: int,
        gamer_score: int,
        boss_hp: int,
    ) -> None:
        """Speichert den aktuellen Spielstand."""
        data = {
            "current_index": current_index,
            "champions_score": champions_score,
            "gamer_score": gamer_score,
            "boss_hp": boss_hp,
        }
        with open(self.save_path, "w") as f:
            json.dump(data, f, indent=2)

    def load_game(self) -> dict | None:
        """Lädt den Spielstand, falls vorhanden."""
        if not self.save_path.exists():
            return None

        try:
            with open(self.save_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def has_save(self) -> bool:
        """Prüft, ob ein Speichern existiert."""
        exists = self.save_path.exists()
        return exists

    def delete_save(self) -> None:
        """Löscht den Spielstand."""
        if self.save_path.exists():
            self.save_path.unlink()
