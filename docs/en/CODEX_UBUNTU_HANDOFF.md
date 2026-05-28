# Codex Ubuntu Handoff

Last updated: 2026-05-28

## Current Project Scope

This repository owns only:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

Do not implement downstream Cypher generation, Neo4j retrieval, graph matching, localization, or mapping in this repo unless the project owner explicitly changes scope.

## Current Server Context

Target runtime:

```text
OS: Ubuntu 22.04 Server
GPU: RTX 5090
Driver: 595.71.05 verified with nvidia-smi
Runtime: Ollama
Python: python3.11 installed without venv
Project install: user-site dependencies are acceptable
```

This stage is inference-only prompt engineering. It is not fine-tuning, LoRA training, distillation, or model adaptation.

## Important Files To Read First

Read these before making changes:

```text
README.md
docs/en/CONVENTIONS.md
docs/en/TODO.md
docs/en/VIEW_AWARE_GRAPH_SCHEME.md
docs/en/SCHEMA_NOTES.md
docs/en/VLM_MODEL_CANDIDATES.md
docs/en/VLM_EVALUATION_RUBRIC.md
docs/en/UBUNTU_2204_SERVER_SETUP.md
prompts/view_graph_extraction.md
schemas/view_aware_graph.schema.json
examples/outputs/smartcitylab_lobby_gt_minimal.json
```

`AGENTS.md` and `docs/ko/` are local-only and ignored by Git. If Codex needs automatic local rules on the Ubuntu server, copy or recreate `AGENTS.md` from the development machine.

## Local Data

Raw images are ignored by Git.

Expected GT image location on the Ubuntu server:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Output paths should remain ignored:

```text
data/interim/vlm_raw/
data/processed/view_graphs/
```

Do not commit raw images, raw VLM responses, generated graph outputs, credentials, or local artifacts unless explicitly promoted as small synthetic examples.

## Current Schema Policy

Node `type` must stay coarse:

```text
wall
door
window
opening
floor
ceiling
surface
panel
furniture
object
unknown
```

Specific names such as monitor, display stand, shelf, wood panel, camera, light, or sign belong in `label` and optional `subtype`, not in `type`.

People must not be extracted as graph nodes. If visible people matter for privacy or occlusion, record only a global observation.

World graph classes such as `BuildingFurniture`, `WallSurface`, or `BoundarySurface` are optional hints only through `world_candidate_types` or `world_alignment_note`.

## Current Model Plan

Free/local first:

```text
1. qwen2.5vl:7b
2. qwen2.5vl:32b, one 32B model at a time because disk is tight
3. qwen3-vl:32b only after removing the previous 32B model if needed
```

With a 64 GiB VM disk, do not keep multiple 32B models at once.

## Immediate Next Steps

1. Confirm repo is up to date:

```bash
git status
git pull origin main
```

2. Confirm Python validation:

```bash
python3.11 - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator

schema = json.loads(Path("schemas/view_aware_graph.schema.json").read_text())
data = json.loads(Path("examples/outputs/smartcitylab_lobby_gt_minimal.json").read_text())

Draft202012Validator(schema).validate(data)
print("schema validation passed")
PY
```

3. Confirm GPU:

```bash
nvidia-smi
```

4. Pull or confirm local VLM:

```bash
ollama list
ollama pull qwen2.5vl:7b
```

5. Run first GT image smoke test.

If Ollama CLI does not correctly attach/read the image, switch to the Ollama HTTP API with base64 image input rather than continuing blind text-only prompting.

## First Evaluation Criteria

A first output is useful if it:

- is valid JSON or close enough to repair
- validates against `schemas/view_aware_graph.schema.json` after minimal repair
- extracts wall, door/opening, floor, foreground monitor/display objects as `object` nodes, and at least one furniture/surface/panel node
- captures foreground occlusion
- does not extract people as nodes
- includes evidence and uncertainty
- does not include downstream matching/localization fields

## If Editing

When changing schema, prompt, or evaluation rules:

- update `docs/en/`
- update local `docs/ko/` if available on the machine
- update `docs/en/TODO.md`
- keep generated/raw outputs ignored
- do not run destructive Git commands
