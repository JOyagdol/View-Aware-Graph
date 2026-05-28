# Prompt Trial Checklist

Last updated: 2026-05-28

## Purpose

This checklist defines what to inspect when running the View-Aware Graph extraction prompt on the GT and DT lobby inputs.

It is limited to:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

It does not evaluate downstream Cypher generation, Neo4j retrieval, graph matching, localization, or mapping.

## Trial Inputs

Primary GT input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Secondary DT input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_DT.png
```

## Before Each Trial

- Confirm the selected VLM model is recorded.
- Confirm the prompt file path is recorded.
- Confirm the input image path is recorded.
- Confirm raw VLM output will be saved under `data/interim/vlm_raw/`.
- Confirm extracted graph JSON will be saved under `data/processed/view_graphs/`.
- Confirm generated outputs remain ignored unless explicitly promoted as small examples.

## Required Output Checks

- Output is valid JSON.
- Output validates against `schemas/view_aware_graph.schema.json`.
- Output uses `schema_version: "0.1.0"`.
- Output includes `source`, `view`, `nodes`, and `edges`.
- Output does not include downstream matching, retrieval, Cypher, Neo4j, localization, or mapping fields.
- Output does not extract people as graph nodes.
- Node `type` values stay in the coarse schema taxonomy.
- Specific object names use `label` and optional `subtype`, not custom `type` values.

## GT Quality Checks

- Captures a central wall or wall-like background region.
- Captures the floor.
- Captures a door or opening near the center-left area.
- Captures foreground monitor/display objects as `type: "object"` with `subtype: "monitor"` when visible.
- Separates left and right foreground monitors when both are visible enough.
- Captures a monitor stand or display support when visible.
- Captures at least one furniture, shelf, panel, or surface-like node beyond wall/floor/door.
- Records foreground monitor occlusion with `in_front_of`, `overlaps`, or uncertainty where appropriate.
- Uses meaningful node ids such as `wall_center`, `monitor_right`, or `display_stand_right`.
- Uses `region`, `depth_hint`, `occlusion`, or `uncertainty` when the visual evidence supports them.
- Avoids uniform confidence values when observations differ in certainty.
- Keeps evidence short, visible, and aligned with the node or relation it describes.

## DT Quality Checks

- Captures coarse geometry even when texture and lighting are weak.
- Does not hallucinate GT-only objects if they are absent from the DT render.
- Marks low-contrast or ambiguous elements with uncertainty.
- Separates DT image limitations from model failures when recording errors.

## Error Labels

Use the labels from `VLM_EVALUATION_RUBRIC.md`:

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

Additional prompt-trial notes may use:

- `generic_node_ids`
- `missing_subtype`
- `uniform_confidence`
- `source_target_evidence_mismatch`

## First Qwen2.5-VL-7B GT Trial Result

Date: 2026-05-28

Input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Model:

```text
qwen2.5vl:7b
```

Outputs:

```text
data/interim/vlm_raw/qwen2_5vl_7b_smartcitylab_lobby_gt_raw.json
data/processed/view_graphs/qwen2_5vl_7b_smartcitylab_lobby_gt.json
```

Result:

- JSON extraction succeeded.
- Project owner confirmed schema validation passed.
- The output stayed within image-to-graph scope.
- People were not extracted as nodes.
- Core graph quality was weak: monitors, display stand, shelf/panel details, occlusion, uncertainty, and meaningful node ids need prompt improvement.

Observed error labels:

- `missing_core_object`
- `wrong_relation`
- `weak_evidence`
- `missing_uncertainty`
- `missing_subtype`
- `uniform_confidence`
- `source_target_evidence_mismatch`

## Qwen2.5-VL-32B GT CLI Trial Schema Drift

Date: 2026-05-28

Input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Model:

```text
qwen2.5vl:32b
```

Result:

- The model returned graph-shaped JSON, but the first CLI attempt failed schema validation.
- `global_observations` used objects with `description`, `uncertainty`, and `confidence` instead of strings.
- Node `region` used object-style `{"bbox_2d": [x, y, width, height]}` instead of a region enum plus schema `bbox_2d` object.
- Node `occlusion` used occluder id lists such as `["monitor_right"]` instead of `none`, `partial`, `heavy`, or `unknown`.
- Prompt instructions were tightened for these field shapes.
- Deterministic repair coverage was added for these field-shape drifts without changing the schema.

Observed error labels:

- `schema_mismatch`
- `field_shape_drift`
- `object_style_global_observation`
- `bbox_array_in_region`
- `occlusion_id_list`

## Qwen2.5-VL-32B GT CLI Baseline Result

Date: 2026-05-28

Input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Model:

```text
qwen2.5vl:32b
```

Outputs:

```text
data/interim/vlm_raw/smartcitylab_lobby_gt_qwen2_5vl_32b_cli_raw.json
data/processed/view_graphs/smartcitylab_lobby_gt_qwen2_5vl_32b_cli.json
data/processed/view_graphs/smartcitylab_lobby_gt_qwen2_5vl_32b_cli.png
```

Result:

- Final CLI output validated successfully.
- Output contains 8 nodes and 6 edges.
- Visualization was switched from bbox rectangles to center-point nodes with edge arrows to keep the image readable.
- 32B captured major right-side monitor/furniture structure, but still missed the left monitor and did not localize wall/door geometry strongly.

Observed error labels:

- `missing_core_object`
- `missing_required_optional_detail`
- `weak_evidence`
- `coarse_region_only`
- `sparse_relation_graph`

## Qwen2.5-VL-7B GT Prompt V3 Trial Result

Date: 2026-05-28

Input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Model:

```text
qwen2.5vl:7b
```

Outputs:

```text
data/interim/vlm_raw/qwen2_5vl_7b_smartcitylab_lobby_gt_prompt_v3_raw.json
data/processed/view_graphs/qwen2_5vl_7b_smartcitylab_lobby_gt_prompt_v3.json
data/processed/view_graphs/qwen2_5vl_7b_smartcitylab_lobby_gt_prompt_v3_repaired.json
```

Result:

- JSON extraction succeeded.
- Original output failed schema validation because `partially_occluded_by` is not an allowed relation.
- Minimal repair changed `partially_occluded_by` to `behind` and added `uncertainty: ["occluded", "viewpoint_inferred"]`.
- Project owner confirmed the repaired output passed schema validation.
- Core graph quality improved: central wall, floor, center-left door, left/right monitors, right display stand, and right shelf/furniture were captured.

Observed error labels:

- `schema_mismatch`
- `weak_evidence`
- `missing_uncertainty`
- `missing_required_optional_detail`

## Qwen2.5-VL-7B GT Prompt V2 Trial Result

Date: 2026-05-28

Input:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

Model:

```text
qwen2.5vl:7b
```

Outputs:

```text
data/interim/vlm_raw/qwen2_5vl_7b_smartcitylab_lobby_gt_prompt_v2_raw.json
data/processed/view_graphs/qwen2_5vl_7b_smartcitylab_lobby_gt_prompt_v2.json
```

Result:

- JSON extraction succeeded.
- Project owner confirmed schema validation passed.
- Node ids improved from numeric ids to descriptive ids.
- Left and right monitor nodes were separated.
- Display stand nodes were included.
- Core graph quality remains limited because subtype, uncertainty, occlusion, varied confidence, and central door/wall/furniture details are still weak.

Observed error labels:

- `missing_core_object`
- `wrong_relation`
- `weak_evidence`
- `missing_uncertainty`
- `missing_subtype`
- `uniform_confidence`
- `source_target_evidence_mismatch`
