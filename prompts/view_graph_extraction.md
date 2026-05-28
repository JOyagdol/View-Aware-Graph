# View-Aware Graph Extraction Prompt

You are given one indoor scene image. Extract a structured View-Aware Graph that describes stable visible scene elements, their image-side spatial relationships, and any viewpoint assumptions that can be inferred from the image.

Return only JSON that conforms to `schemas/view_aware_graph.schema.json`.

Do not wrap the JSON in Markdown. Do not include comments. Do not include explanatory text before or after the JSON.

Project scope:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

Do not perform downstream CityGML retrieval, Neo4j query generation, graph matching, localization, or mapping.

Required focus:

- furniture-like objects
- walls and wall-like surfaces
- windows/openings
- doors/openings
- relations among the visible objects
- confidence for each node and relation
- short evidence text grounded in visible image cues
- explicit uncertainty when an object or relation is ambiguous

Rules:

- Use only these coarse node `type` values:
  - `wall`
  - `door`
  - `window`
  - `opening`
  - `floor`
  - `ceiling`
  - `surface`
  - `panel`
  - `furniture`
  - `object`
  - `unknown`
- Put specific visual names in `label` and optional `subtype`, not in `type`.
- Use `type: "object"` for specific devices, screens, signs, cameras, lights, stands, fixtures, and other generic physical objects.
- Use `type: "furniture"` for clear furniture-like objects such as shelves, desks, tables, chairs, cabinets, or benches.
- Use `type: "panel"` for visually distinct wall/ceiling/surface panels, including wood panels or glass panels.
- Do not use final CityGML or 3DCitySG classes as the node `type`.
- Add optional `world_candidate_types` only as downstream retrieval hints.
- Do not extract people as graph nodes. If visible people affect privacy or occlusion context, mention them only in `global_observations`.
- Do not over-focus on monitor screen contents unless the physical monitor itself is the observed object.
- Image-plane relations such as `left_of`, `right_of`, `above`, `below`, `overlaps`, and `contains` are viewpoint-dependent.
- View-depth relations such as `in_front_of` and `behind` are inferred and should include uncertainty when ambiguous.
- Physical relations such as `mounted_on`, `standing_on`, `attached_to`, and `supports` are still image observations, not final world topology.
- Use only these edge `relation` values:
  - `left_of`
  - `right_of`
  - `above`
  - `below`
  - `overlaps`
  - `contains`
  - `in_front_of`
  - `behind`
  - `attached_to`
  - `mounted_on`
  - `standing_on`
  - `supports`
  - `part_of`
  - `adjacent_to`
  - `aligned_with`
  - `unknown`
- Use `bbox_2d` only when you can estimate a normalized bounding box with `x`, `y`, `width`, and `height` values in `[0, 1]`.
- If a precise box is uncertain, omit `bbox_2d` and use `region`.
- Every node must include `id`, `label`, `type`, `confidence`, and `evidence`.
- Every edge must include `id`, `source`, `target`, `relation`, `confidence`, and `evidence`.
- Confidence must be a number from `0` to `1`.
- Use `uncertainty` only with these values:
  - `occluded`
  - `low_resolution`
  - `glare_or_reflection`
  - `ambiguous_type`
  - `screen_content`
  - `viewpoint_inferred`
  - `partial_object`
  - `transient_object`
- Use `world_candidate_types`, `world_alignment_note`, and `world_relation_hints` only as optional downstream hints, never as final matching results.
- Prefer 6 to 14 important nodes over exhaustive tiny-object extraction.
- Prefer 6 to 20 high-confidence relations over speculative relation lists.

Required top-level fields:

- `schema_version`
- `source`
- `view`
- `nodes`
- `edges`

Recommended top-level optional field:

- `global_observations`

Required `view` fields:

- `frame`
- `coordinate_origin`
- `bbox_format`
- `assumptions`

For this project, normally use:

- `frame`: `image`
- `coordinate_origin`: `top_left`
- `bbox_format`: `normalized_xywh` when using `bbox_2d`, otherwise `region_only`

Expected output shape:

This is the minimal shape. For a real image, fill `nodes`, `edges`, and `global_observations` with observed content.

```json
{
  "schema_version": "0.1.0",
  "source": {
    "image_id": "input_image"
  },
  "view": {
    "frame": "image",
    "coordinate_origin": "top_left",
    "bbox_format": "normalized_xywh",
    "assumptions": []
  },
  "nodes": [],
  "edges": [],
  "global_observations": []
}
```
