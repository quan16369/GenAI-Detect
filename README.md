# Acontext Local for Kaggle ARC-AGI-3

This repository is a lightweight, filesystem-backed subset of the official
[`memodb-io/Acontext`](https://github.com/memodb-io/Acontext) Python SDK.
It is designed for offline environments such as Kaggle competition reruns,
where you cannot rely on a running Acontext server, Docker, or network access.

What this repo keeps from upstream:

- `from acontext import AcontextClient`
- `client.sessions.create(...)`
- `client.sessions.store_message(...)`
- `client.learning_spaces.create(...)`
- `client.learning_spaces.learn(...)`
- `client.learning_spaces.list_skills(...)`
- `client.skills.get_file(...)`
- skill bundles stored as readable Markdown files
- ARC-specific progressive disclosure memory via `ArcSkillMemory`

What it intentionally does not try to reproduce:

- the REST backend
- async workers / message queues
- embeddings or semantic search
- dashboards, sandboxes, or cloud auth

## Why this fits your notebook better

Your current notebook uses an "Acontext-inspired" pattern, but all memory logic
is embedded directly into `my_agent.py`. This repo moves that logic into a local
`acontext` package with an ARC-AGI-3 integration layer:

- one learning space shared across games
- one skill bundle per game
- one shared cross-game skill bundle
- Markdown files for mechanic / failures / strategy
- optional LLM-based distillation callback for smarter updates

## Kaggle usage

Upload this repo as a Kaggle dataset or keep it inside your notebook workspace,
then install it locally:

```bash
pip install -q /kaggle/input/<your-dataset-slug>
```

or, if the repo is already in `/kaggle/working/acontext-local`:

```bash
pip install -q /kaggle/working/acontext-local
```

Then in the notebook agent code:

```python
from acontext.integrations.arc_agi3 import ArcSkillMemory

skills = ArcSkillMemory(
    game_id=game_id,
    storage_dir="/kaggle/working/acontext_store",
    distill_fn=lambda messages: llm_call(messages, reasoning="medium", max_tokens=1024),
)
```

If the organizer-provided public environments are available locally, `ArcSkillMemory`
can also inject verified public knowledge:

```python
skills = ArcSkillMemory(
    game_id=game_id,
    storage_dir="/kaggle/working/acontext_store",
    public_environment_root="/kaggle/input/arc-prize-2026-arc-agi-3/environment_files",
    distill_fn=lambda messages: llm_call(messages, reasoning="medium", max_tokens=1024),
)
```

This adds a `VERIFIED PUBLIC KNOWLEDGE` section for public games while leaving
private games on the learned-memory path.

## Filesystem layout

The local backend writes everything under `ACONTEXT_STORAGE_DIR` or the
`storage_dir` you pass in:

```text
.acontext_store/
  sessions/
  learning_spaces/
  skills/
```

Each skill remains a readable file bundle, so you can inspect and export it in
the same spirit as upstream Acontext.
