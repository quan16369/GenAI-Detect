from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from acontext import AcontextClient
from acontext.integrations.arc_agi3 import ArcSkillMemory


class SmokeTests(unittest.TestCase):
    def test_client_and_learning(self) -> None:
        with tempfile.TemporaryDirectory(prefix="acontext-client-") as tmp:
            client = AcontextClient(storage_dir=tmp)
            space = client.learning_spaces.create(meta={"name": "demo"})
            session = client.sessions.create(configs={"agent": "demo"})
            client.sessions.store_message(
                session.id,
                blob={"role": "user", "content": "Remember that ACTION1 changed the board."},
            )
            record = client.learning_spaces.learn(space.id, session_id=session.id)
            self.assertEqual(record.status, "completed")
            skills = client.learning_spaces.list_skills(space.id)
            self.assertEqual(len(skills), 1)
            summary = client.skills.get_file(skill_id=skills[0].id, file_path="summary.md")
            self.assertIsNotNone(summary.content)
            self.assertIn("ACTION1", summary.content.raw)

    def test_arc_skill_memory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="acontext-arc-") as tmp:
            memory = ArcSkillMemory("demo-game", storage_dir=tmp)
            context = memory.build_context(level=0, actions_taken=0)
            self.assertIn("CROSS-GAME KNOWLEDGE", context)
            episode = [
                {"action": "ACTION1", "diff": "(first frame)", "reward": 0.0},
                {"action": "ACTION1", "diff": "NO CHANGE", "reward": 0.0},
                {"action": "ACTION6", "diff": "(3,4):0->2", "reward": 1.0},
            ]
            memory.distill(episode, level=0, win=False)
            self.assertIn("ACTION6", memory.read("game_mechanic.md"))
            self.assertIn("ACTION1", memory.read("failure_log.md"))


if __name__ == "__main__":
    unittest.main()
