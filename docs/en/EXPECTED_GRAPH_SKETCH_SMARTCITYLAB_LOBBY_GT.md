# Expected Graph Sketch: Smart City Lab Lobby GT

Last updated: 2026-05-14

## Purpose

This document defines the first human-readable expected graph sketch for:

```text
data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg
```

It is not a final annotation file, not the general schema, and not downstream matching logic. It is a compact benchmark case for schema refinement, prompt design, VLM model evaluation, and output improvement.

The general scheme is defined in [`VIEW_AWARE_GRAPH_SCHEME.md`](VIEW_AWARE_GRAPH_SCHEME.md). This GT sketch should stay a test case under that scheme.

## Image Role

This GT image is the primary early benchmark for:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

The graph should prioritize stable indoor structural and furniture elements over transient or distracting content.

Primary extraction focus:

- furniture-like objects
- walls and wall-like surfaces
- windows/openings
- doors/openings
- relations among those objects

Floor, ceiling, cameras, lights, signs, and other fixtures can be included as supporting context, but the first benchmark should not be judged mainly on those secondary nodes.

## World Graph Alignment Policy

The View-Aware Graph should be influenced by the downstream 3DCitySG/CityGML graph vocabulary, but it should not directly replace image-observed node types with CityGML world graph classes.

Reason:

- The View-Aware Graph is an observation from one image.
- The World Graph is a semantic-geometric representation from CityGML/Neo4j.
- A visible object may map to multiple possible world classes.
- Some visible image elements are only partial, occluded, or ambiguous.
- Precise world-graph relation inference should happen later in Rule-based Cypher Query Generation and World Graph Retrieval.

Recommended representation:

- Keep `type` as a coarse image-observed semantic family, such as `wall`, `door`, `object`, `panel`, or `furniture`.
- Put specific names such as monitor, display stand, ceiling camera, light fixture, sign, shelf, or wood panel in `label` and optional `subtype`.
- Add future alignment metadata such as `world_candidate_types`.
- Use candidate mappings as retrieval hints, not as final labels.
- Let downstream retrieval expand candidate pairs and resolve exact CityGML classes.

Example:

```json
{
  "id": "monitor_right",
  "type": "object",
  "subtype": "monitor",
  "world_candidate_types": ["BuildingFurniture"],
  "world_alignment_note": "Likely an indoor furniture-like object in the current 3DCitySG world graph vocabulary."
}
```

## View And Coordinate Convention

- Frame: `image`
- Origin: top-left of image
- Coordinate style for future JSON: normalized 2D bounding boxes in `[0, 1]`
- Bounding box fields: `x`, `y`, `width`, `height`
- Depth convention:
  - `near`: foreground objects close to camera
  - `mid`: central wall, door, furniture, and surface objects
  - `far`: background doorway/window/opening area
- Relation convention:
  - `left_of`, `right_of`, `above`, and `below` are image-plane relations.
  - `in_front_of` and `behind` are view-depth relations inferred from occlusion, size, and scene layout.
  - If a relation is uncertain, keep it but lower confidence and include evidence.

## Node Types Used In This GT Sketch

This sketch uses a subset of the general scheme. Phase 2 should update the schema from the general scheme first, then verify that this GT sketch can be represented.

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

People should not be extracted as graph nodes in this project. If people are visible, record only a global note such as `transient human presence ignored` when needed for privacy or occlusion context.

## World Candidate Type Hints

Initial sketch nodes should carry optional downstream candidate hints. These hints are intentionally non-exclusive.

| View Node Type / Subtype | Candidate 3DCitySG / CityGML Types | Notes |
| --- | --- | --- |
| `furniture` | `BuildingFurniture` | Generic furniture-like object when subtype is uncertain |
| `floor` | `BoundarySurface`, `FloorSurface`, `BuildingFloorSurface` | Exact subtype depends on CityGML version and indoor/outdoor context |
| `wall` | `BoundarySurface`, `WallSurface`, `InteriorWallSurface`, `BuildingWallSurface` | Interior wall vs exterior wall should be resolved downstream |
| `ceiling` | `BoundarySurface`, `CeilingSurface`, `BuildingCeilingSurface` | Image observation should stay `ceiling` |
| `panel` | `BoundarySurface`, `InteriorWallSurface` | Surface-like visual feature |
| `opening` | `Opening`, `Door`, `Window` | Generic opening when door/window distinction is uncertain |
| `door` | `Opening`, `Door` | Strong candidate mapping |
| `window` | `Opening`, `Window` | Strong candidate mapping |
| `object`, subtype `monitor` | `BuildingFurniture` | Current world graph alignment target for monitor-like indoor objects |
| `object`, subtype `display_stand` | `BuildingFurniture` | If modeled in world graph |
| `object`, subtype `ceiling_camera` | `BuildingFurniture` | Treat as furniture-like object for current world graph retrieval hints |
| `object`, subtype `light_fixture` | `BuildingFurniture` | Treat as furniture-like object for current world graph retrieval hints |
| `panel`, subtype `wood_panel` | `BoundarySurface`, `InteriorWallSurface` | Surface-like visual feature |
| `furniture`, subtype `shelf` | `BuildingFurniture` | Strong indoor furniture candidate |
| `object`, subtype `sign` | `BuildingFurniture` | Treat as furniture-like object if modeled in world graph |
| visible people | none | Do not extract as graph nodes; ignore except for privacy/occlusion notes |

## Relation Types Used In This GT Sketch

This sketch uses these relation types from the general scheme:

- `left_of`
- `right_of`
- `above`
- `below`
- `in_front_of`
- `behind`
- `adjacent_to`
- `overlaps`
- `contains`
- `part_of`
- `supports`
- `mounted_on`
- `standing_on`
- `attached_to`
- `aligned_with`

The current schema already has some of these, but Phase 2 should generalize the schema relation taxonomy before checking this image-specific sketch.

## Relation Alignment With World Graph Retrieval

View-Aware Graph relations should stay image-observed and viewpoint-aware. They should not claim exact 3D AABB relations unless the image evidence supports only a weak hint.

| View Relation | Downstream World Relation Hint | Use |
| --- | --- | --- |
| `contains` | `CONTAINS`, `INSIDE` | Useful when an object is visibly inside a larger region |
| `part_of` | `BOUNDED_BY`, `HAS_OPENING`, hierarchy edges | Useful for surface/opening decomposition hints |
| `attached_to` | `HAS_OPENING`, `BOUNDED_BY`, `TOUCHES` | Candidate expansion hint, not final topology |
| `mounted_on` | `TOUCHES`, `INSIDE` | Useful for furniture-like objects mounted on surfaces |
| `standing_on` | `TOUCHES`, `INSIDE` | Useful for furniture/stand-floor candidates |
| `adjacent_to` | `ADJACENT_TO` | Weak spatial candidate relation |
| `overlaps` | `INTERSECTS` | Use cautiously; image overlap may be occlusion, not 3D intersection |
| `in_front_of` / `behind` | retrieval ranking feature | View-depth relation, not a direct CityGML topology relation |
| `left_of` / `right_of` / `above` / `below` | retrieval ranking feature | Image-plane relation; useful for query scoring, not exact world relation |

Downstream retrieval can expand candidate pairs more aggressively than the View-Aware Graph. The View-Aware Graph should provide evidence and confidence so the retrieval stage can decide which candidate world relations to query.

## Expected Core Nodes

This sketch intentionally uses a small number of nodes. It should guide extraction without requiring exhaustive annotation.

Primary nodes are the benchmark focus. Supporting nodes provide useful context but should not dominate evaluation.

| ID | Label | Type | View Region | Depth | Priority | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `wall_center` | central white wall | `wall` | center | mid | high | Dominant wall plane extending into the interior space |
| `door_center_left` | gray door | `door` | center-left | mid | high | Door on wall near the background opening area |
| `window_far_left` | glass window or entrance | `window` | far-left background | far | medium | Bright exterior-facing glass area |
| `panel_left` | curved wood wall/ceiling panel | `panel`, subtype `wood_panel` | upper-left and left edge | near | medium | Curved wood feature partially visible |
| `shelf_right` | wood shelving | `furniture`, subtype `shelf` | right of center | mid | medium | Grid-like shelving behind/near right-side surface area |
| `monitor_left` | left foreground monitor | `object`, subtype `monitor` | lower-left to center-left | near | medium | Large foreground screen, partially occluding scene |
| `monitor_right` | right foreground monitor | `object`, subtype `monitor` | right side | near | medium | Large monitor showing digital twin content |
| `display_stand_right` | right monitor stand | `object`, subtype `display_stand` | lower-right | near | medium | Stand/wheeled support under right monitor |
| `floor_main` | glossy lobby floor | `floor` | bottom and center | near to far | support | Large reflective tiled floor plane |
| `ceiling_main` | exposed grid ceiling | `ceiling` | upper half | mid to far | support | Dark ceiling grid with tracks and fixtures |
| `ceiling_camera_center` | ceiling dome cameras | `object`, subtype `ceiling_camera` | upper center | mid | support | Two visible dome cameras hanging from ceiling |
| `ceiling_camera_right` | right ceiling dome camera | `object`, subtype `ceiling_camera` | upper-right | far | medium | Smaller dome camera near right background |
| `light_fixtures` | ceiling light fixtures | `object`, subtype `light_fixture` | upper half | mid to far | support | Multiple round/linear lights |
| `sign_center_left` | conference room sign | `object`, subtype `sign` | center-left | mid | low | Small black sign near door |

## Expected Core Relations

| Source | Relation | Target | Confidence | Evidence |
| --- | --- | --- | ---: | --- |
| `monitor_left` | `in_front_of` | `wall_center` | 0.90 | Monitor occludes left side of wall/opening area |
| `monitor_right` | `in_front_of` | `wall_center` | 0.75 | Right monitor occupies foreground in front of right-side wall/surface area |
| `monitor_right` | `right_of` | `wall_center` | 0.80 | Right monitor is on the right side of the central wall |
| `monitor_left` | `left_of` | `wall_center` | 0.70 | Left monitor is on the left side of the central wall |
| `display_stand_right` | `supports` | `monitor_right` | 0.90 | Monitor sits on stand/wheeled support |
| `display_stand_right` | `standing_on` | `floor_main` | 0.90 | Stand contacts floor |
| `door_center_left` | `left_of` | `wall_center` | 0.80 | Door is on left portion of central wall area |
| `door_center_left` | `attached_to` | `wall_center` | 0.85 | Door is embedded in wall plane |
| `window_far_left` | `left_of` | `door_center_left` | 0.65 | Bright glass/window area is farther left than the door |
| `shelf_right` | `behind` | `monitor_right` | 0.65 | Shelf is partly behind the right foreground monitor |
| `shelf_right` | `right_of` | `wall_center` | 0.70 | Shelf appears to the right of central wall |
| `ceiling_main` | `above` | `wall_center` | 0.95 | Ceiling is visibly above wall |
| `ceiling_main` | `above` | `floor_main` | 0.95 | Ceiling is upper image plane, floor lower |
| `ceiling_camera_center` | `mounted_on` | `ceiling_main` | 0.90 | Dome cameras hang from ceiling grid |
| `ceiling_camera_right` | `mounted_on` | `ceiling_main` | 0.85 | Smaller right dome camera on ceiling |
| `light_fixtures` | `mounted_on` | `ceiling_main` | 0.90 | Lights are installed in/on ceiling |
| `window_far_left` | `behind` | `monitor_left` | 0.70 | Bright glass/window or opening is in the background behind foreground monitor |
| `panel_left` | `left_of` | `ceiling_main` | 0.65 | Curved wood feature is on left upper image area |
| `sign_center_left` | `attached_to` | `wall_center` | 0.75 | Sign is near wall/door area |

## Expected Global Observations

- The scene is an indoor lobby or corridor, not an outdoor street scene.
- The camera is looking slightly upward and forward into a lobby/corridor space.
- Corridor-like space and column-like vertical structures should be described as observations or attributes, not required graph nodes, because they are not expected as explicit CityGML source nodes in the current downstream graph.
- The image contains strong foreground occlusion from two monitors.
- The floor is glossy and reflective; reflections should not become separate physical nodes unless clearly needed.
- The right monitor contains digital twin content, but the graph should mainly represent the physical monitor unless the prompt explicitly asks for screen-content extraction.
- A partial person is visible but should not be extracted as a graph node because the project focuses on stable scene structure.

## Ignore Or Down-Weight

The VLM should avoid over-weighting:

- monitor screen text
- digital twin content inside the monitor
- floor reflections
- visible people and person identity/details
- cables and tiny fixtures unless needed for a specific task
- ambiguous background details outside the lobby structure
- ceiling cameras/lights when evaluating the primary furniture-wall-window-door graph

## Uncertainty And Evidence Policy

Each node and relation should support:

- confidence in `[0, 1]`
- short evidence text grounded in visible image cues
- optional uncertainty notes when the object/relation is inferred rather than explicit
- occlusion status for partially visible objects

Recommended uncertainty categories for Phase 2:

- `occluded`
- `low_resolution`
- `glare_or_reflection`
- `ambiguous_type`
- `screen_content`
- `transient_object`

## Scheme And Schema Implications For Phase 2

The current schema should be revised against the general scheme first. This GT sketch then acts as the first benchmark to check whether the schema can express a real input.

Node types used by this sketch:

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

Specific object names are represented through `label` and optional `subtype`, not through node `type`.

Relation types used by this sketch:

- `mounted_on`
- `standing_on`
- `attached_to`

Useful field additions:

- normalized `bbox_2d` convention documentation
- `depth_hint`
- `priority`
- `occlusion`
- `uncertainty`
- `world_candidate_types`
- `world_alignment_note`
- optional relation-level `world_relation_hints`

## Success Criteria For VLM Evaluation

A VLM output for this image should be considered acceptable if it:

- extracts the main wall, door, window/opening, monitors, display stand, and shelf/furniture-like objects
- captures foreground monitor occlusion
- captures furniture/object relations to wall, door, and window/opening candidates
- captures left/right layout of window, door, central wall, monitor, shelf/furniture area
- preserves uncertainty for partial/ambiguous non-person objects
- returns valid structured JSON without downstream matching fields
