import json
from pathlib import Path


class DialogueManager:
    def __init__(self, dialogue_file_name="old_man.json"):
        self.dialogues_dir = Path(__file__).resolve().parents[1] / "dialogues"
        self.dialogue_file_name = dialogue_file_name
        self.npc_name = "NPC"
        self.dialogues = []
        self.dialogue_index = 0
        self.load_dialogues(dialogue_file_name)

    def load_dialogues(self, dialogue_file_name):
        config_path = self.dialogues_dir / dialogue_file_name
        if not config_path.exists():
            self.npc_name = "NPC"
            self.dialogues = ["..."]
            return

        with config_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.npc_name = data.get("npc_name", "NPC")
        self.dialogues = data.get("dialogues", ["..."])
        self.dialogue_index = 0

    def get_next_line(self):
        if not self.dialogues:
            return "..."

        text = self.dialogues[self.dialogue_index]
        self.dialogue_index = (self.dialogue_index + 1) % len(self.dialogues)
        return text
