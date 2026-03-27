"""Minimal ARC-AGI-3 integration example for Kaggle notebooks.

This file is intentionally small: it shows how to replace the notebook's
inline "Acontext-inspired" class with the packaged ArcSkillMemory helper.
"""

from __future__ import annotations

from acontext.integrations.arc_agi3 import ArcSkillMemory


def build_skill_memory(game_id: str, llm_call):
    return ArcSkillMemory(
        game_id=game_id,
        storage_dir="/kaggle/working/acontext_store",
        distill_fn=lambda messages: llm_call(
            messages,
            reasoning="medium",
            max_tokens=1024,
            stop=["</strategy>", "</shared>"],
        ),
    )


NOTEBOOK_PATCH = """
Replace the inline SkillMemory class in your notebook with:

    from acontext.integrations.arc_agi3 import ArcSkillMemory as SkillMemory

Then update the agent constructor to:

    self.skills = SkillMemory(
        self.game_id,
        storage_dir="/kaggle/working/acontext_store",
        distill_fn=lambda messages: llm_call(messages, reasoning="medium", max_tokens=1024),
    )

The rest of your notebook can keep using:
    self.skills.build_context(level, self.action_counter)
    self.skills.distill(self.episode, self.current_level, win)
    self.skills.update_shared(...)
"""
