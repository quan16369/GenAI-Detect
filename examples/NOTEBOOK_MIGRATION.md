# Notebook Migration Guide

This guide shows the smallest set of changes needed to move the notebook from
"Acontext-inspired" code to the packaged local `acontext` backend.

## 1. Install the repo inside Kaggle

If this repository is uploaded as a Kaggle dataset:

```python
!pip install -q /kaggle/input/<your-dataset-slug>
```

If the repository is copied into `/kaggle/working/acontext-local`:

```python
!pip install -q /kaggle/working/acontext-local
```

## 2. Replace the inline skill-memory implementation

Delete the large inline `SkillMemory` class from `my_agent.py` and replace it
with:

```python
from acontext.integrations.arc_agi3 import ArcSkillMemory as SkillMemory
```

## 3. Update the agent constructor

Change:

```python
self.skills = SkillMemory(self.game_id)
```

to:

```python
self.skills = SkillMemory(
    self.game_id,
    storage_dir="/kaggle/working/acontext_store",
    distill_fn=lambda messages: llm_call(
        messages,
        reasoning="medium",
        max_tokens=1024,
        stop=["</strategy>", "</shared>"],
    ),
)
```

## 4. Keep the rest of the notebook API the same

These calls still work:

```python
self.skills.build_context(level, self.action_counter)
self.skills.distill(self.episode, self.current_level, win)
self.skills.update_shared(new_pattern)
```

## 5. Result

After the change, the notebook is closer to the real Acontext model:

- memory lives in a packaged `acontext` repo
- sessions and learning spaces exist explicitly
- skills are stored as file bundles, not ad-hoc directories
- ARC memory is still offline and Kaggle-safe
