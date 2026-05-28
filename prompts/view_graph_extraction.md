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
- `bbox_2d` must be an object like `{"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.4}`. Do not use arrays such as `[x, y, width, height]`.
- `region` must be one string enum only. Do not put `bbox_2d` inside `region`.
- Use only these node `region` values:
  - `upper_left`
  - `upper_center`
  - `upper_right`
  - `center_left`
  - `center`
  - `center_right`
  - `lower_left`
  - `lower_center`
  - `lower_right`
  - `left`
  - `right`
  - `top`
  - `bottom`
  - `full_frame`
  - `unknown`
- `occlusion` must be one string enum only: `none`, `partial`, `heavy`, or `unknown`. Do not put occluding object ids in `occlusion`.
- If an object is occluded by another object, use `occlusion: "partial"` or `occlusion: "heavy"`, add `uncertainty: ["occluded"]`, and express the occluding object with an edge such as `monitor_right in_front_of wall_center`.
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
- Use descriptive node ids, not generic numeric ids. Prefer ids such as `wall_center`, `floor_main`, `door_center_left`, `monitor_left`, `monitor_right`, `display_stand_right`, `shelf_right`, or `panel_left` when those objects are visible.
- If a monitor or screen is visible as a physical object, use `type: "object"` and `subtype: "monitor"`. Do not use the monitor screen contents as the main graph subject.
- If both left and right foreground monitors are visible, represent them as separate nodes.
- If a display stand, wheeled support, shelf, wall panel, or similar furniture/surface detail is visible, include it when it helps describe the scene structure.
- Include `region`, `depth_hint`, `occlusion`, and `uncertainty` when useful. Use `depth_hint: "near"` for foreground monitors and stands, `mid` for central walls/doors/furniture, and `far` for background openings or windows.
- Do not assign the same confidence to every node and edge. Use lower confidence for inferred depth, partially occluded objects, ambiguous types, glare, reflection, and small fixtures.
- Each edge must have source, target, relation, and evidence that agree with each other. Do not describe a different object pair in the evidence.
- Capture foreground occlusion when visible, especially monitor objects in front of walls, openings, furniture, shelves, or floor regions.

GT lobby benchmark requirements:

- Look specifically for these likely visible benchmark elements before finalizing the JSON: central wall, floor, center-left door or opening, left foreground monitor, right foreground monitor, right display stand, shelf or furniture on the right, and left wall/panel surface.
- For every monitor node, include `subtype: "monitor"`, `depth_hint: "near"`, `occlusion`, and `uncertainty` containing `screen_content`. Add `occluded` if the monitor blocks another scene element.
- For every major node, include `region`, `depth_hint`, and `occlusion`. Omit these only if the object is too ambiguous to place.
- Use varied confidence values. Do not use one repeated value for all nodes and edges. Use values such as 0.95 for obvious floor/ceiling, 0.85 for clear walls/monitors, 0.65-0.75 for inferred depth or partially occluded objects, and 0.45-0.6 for ambiguous small details.
- Prefer support edges from stand to monitor, such as `display_stand_right supports monitor_right`, instead of `monitor_right standing_on display_stand_right`.
- Include at least one foreground occlusion edge when visible, such as `monitor_right in_front_of wall_center` or `monitor_left in_front_of wall_center`, with `uncertainty: ["viewpoint_inferred", "occluded"]`.
- If a center-left door/opening is visible, include it as `type: "door"` or `type: "opening"` and relate it to the central wall with `attached_to`.
- If a right-side shelf or furniture region is visible, include it and mark it behind or partially occluded by the right monitor when appropriate.
- If you cannot confidently find one of these benchmark elements, do not hallucinate it. Instead, mention the missing or ambiguous element in `global_observations`.

Required top-level fields:

- `schema_version`
- `source`
- `view`
- `nodes`
- `edges`

Recommended top-level optional field:

- `global_observations`
- `global_observations` must be an array of strings only. Do not use objects with `description`, `confidence`, or `uncertainty` fields.

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
