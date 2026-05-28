# VLM Evaluation Rubric

Last updated: 2026-05-22

## Purpose

This rubric defines the first fast evaluation pass for VLM outputs on the Smart City Lab lobby GT image.

It evaluates only:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

It does not evaluate downstream retrieval, graph matching, localization, or mapping.

## Test Input

Primary local input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Reference documents:

- `schemas/view_aware_graph.schema.json`
- `docs/en/VIEW_AWARE_GRAPH_SCHEME.md`
- `docs/en/EXPECTED_GRAPH_SKETCH_SMARTCITYLAB_LOBBY_GT.md`
- `examples/outputs/smartcitylab_lobby_gt_minimal.json`

## Pass/Fail Gates

An output fails immediately if:

- it is not valid JSON
- it cannot validate against `schemas/view_aware_graph.schema.json`
- it extracts a person as a graph node
- it adds downstream matching, Neo4j, Cypher, localization, or mapping fields
- it replaces image-observed node `type` values with final CityGML classes

## Score Categories

Score each category from 0 to 2.

| Category | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Core objects | Misses most primary objects | Finds some core objects | Finds wall, door/opening, floor, foreground monitor/display objects as `object` nodes, and at least one furniture/surface/panel node |
| Spatial relations | Mostly absent or wrong | Some useful image-plane relations | Captures left/right, above/below, foreground occlusion, and support/attachment relations |
| Schema fit | Requires heavy repair | Minor repair needed | Valid as-is |
| Evidence | Generic or unsupported | Some visible evidence | Short, concrete evidence grounded in the image |
| Uncertainty | Missing or misleading | Partial uncertainty | Correctly marks occlusion, reflection, screen content, and inferred depth |
| Scope control | Includes downstream logic or people nodes | Mostly scoped but noisy | Strictly image-to-graph; people ignored as nodes |

Maximum score: 12.

Recommended interpretation:

- 10-12: strong baseline
- 7-9: usable with prompt/schema iteration
- 4-6: weak baseline
- 0-3: unsuitable for first implementation

## Error Labels

Use these labels when recording failures:

- `invalid_json`
- `schema_mismatch`
- `missing_core_object`
- `hallucinated_object`
- `wrong_relation`
- `people_as_nodes`
- `screen_content_overfocus`
- `weak_evidence`
- `missing_uncertainty`
- `downstream_scope_leak`

## First Candidate Run Order

1. Qwen2.5-VL-3B-Instruct for a fast free smoke test
2. Qwen2.5-VL-7B-Instruct as the primary free local baseline
3. Qwen2.5-VL-32B-Instruct quantized as the stable 32GB-class local baseline
4. Qwen3-VL-32B-Instruct quantized as the best 32GB-class local quality target if runtime/memory allows
5. SmolVLM-class lightweight model if Qwen is too heavy
6. Optional local comparison with InternVL3-8B or Gemma 3 vision-capable variants
7. Paid upgrade to OpenAI latest GPT vision-capable model after local/free failures are understood
8. Optional paid cross-provider validation with Claude or Gemini
