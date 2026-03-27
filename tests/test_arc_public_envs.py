from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from acontext.arc_public_envs import (
    find_public_knowledge,
    scan_environment_files,
    summarize_environment,
    write_reports,
)
from acontext.integrations.arc_agi3 import ArcSkillMemory


REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_ROOT = REPO_ROOT / "arc-prize-2026-arc-agi-3" / "environment_files"


class ArcPublicEnvScanTests(unittest.TestCase):
    def test_ft09_summary(self) -> None:
        summary = summarize_environment(ENV_ROOT / "ft09" / "0d8bbf25")
        self.assertEqual(summary.game_id, "ft09-0d8bbf25")
        self.assertEqual(summary.available_actions, [6])
        self.assertEqual(summary.level_count, 6)
        self.assertIn("gOi", summary.clickable_tags)
        self.assertTrue(summary.has_hidden_state)
        self.assertTrue(summary.uses_color_remap)
        self.assertEqual(summary.win_method, "cgj")

    def test_scan_and_report(self) -> None:
        summaries = scan_environment_files(ENV_ROOT)
        self.assertEqual(len(summaries), 25)
        with tempfile.TemporaryDirectory(prefix="arc-public-report-") as tmp:
            json_out = Path(tmp) / "arc_public_env_summary.json"
            md_out = Path(tmp) / "arc_public_env_summary.md"
            write_reports(summaries, json_out, md_out, ENV_ROOT)
            self.assertTrue(json_out.exists())
            self.assertTrue(md_out.exists())

    def test_public_knowledge_lookup_supports_short_game_name(self) -> None:
        knowledge = find_public_knowledge(environment_root=str(ENV_ROOT))
        self.assertIsNotNone(knowledge)
        summary = knowledge.get("ft09")
        self.assertIsNotNone(summary)
        self.assertEqual(summary.game_id, "ft09-0d8bbf25")
        markdown = knowledge.render_markdown("ft09")
        self.assertIsNotNone(markdown)
        self.assertIn("click-only", markdown)
        self.assertIn("gOi", markdown)

    def test_arc_skill_memory_includes_verified_public_context(self) -> None:
        with tempfile.TemporaryDirectory(prefix="arc-public-memory-") as tmp:
            memory = ArcSkillMemory(
                "ft09",
                storage_dir=tmp,
                public_environment_root=str(ENV_ROOT),
            )
            verified = memory.read_verified()
            self.assertIn("ft09-0d8bbf25", verified)
            self.assertIn("gOi", verified)
            context = memory.build_context(level=0, actions_taken=0)
            self.assertIn("VERIFIED PUBLIC KNOWLEDGE", context)
            self.assertIn("Action style: `click-only`", verified)


if __name__ == "__main__":
    unittest.main()
