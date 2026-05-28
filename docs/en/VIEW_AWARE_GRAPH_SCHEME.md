# View-Aware Graph Scheme

Last updated: 2026-05-14

## Purpose

This document defines the general scheme for View-Aware Graph outputs.

It is intentionally more general than any single expected graph sketch. A sketch such as `EXPECTED_GRAPH_SKETCH_SMARTCITYLAB_LOBBY_GT.md` is a benchmark case for evaluation, not the schema itself.

Current project scope:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

## Design Principle

The scheme should describe what is visible from an input image while staying useful for downstream World Graph Retrieval.

It should avoid two failure modes:

- overfitting the schema to one image, such as the Smart City Lab lobby GT photo
- forcing image-observed objects into exact CityGML/3DCitySG world classes too early

## General Output Layers

A View-Aware Graph output should have these layers:

1. Source metadata
   - image id/path
   - capture metadata if available
   - image dimensions if known

2. View metadata
   - coordinate frame
   - camera/view assumptions
   - viewpoint confidence or uncertainty

3. Observed nodes
   - image-observed semantic type
   - bbox or region cue when available
   - confidence
   - evidence text
   - occlusion/uncertainty
   - optional world graph candidate hints

4. Observed relations
   - source node
   - target node
   - view-aware relation type
   - confidence
   - evidence text
   - optional world relation hints

5. Global observations
   - scene-level notes
   - ignored transient objects
   - known limitations

## General Node Taxonomy

The first general taxonomy should be compact and stable. It should support indoor lobby/corridor images while staying extensible.

Primary node families:

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

Specific visible names should not become primary node types. Use `label` and optional `subtype` for specific objects:

- `type`: `object`, `subtype`: `monitor`
- `type`: `object`, `subtype`: `display_stand`
- `type`: `object`, `subtype`: `ceiling_camera`
- `type`: `object`, `subtype`: `light_fixture`
- `type`: `object`, `subtype`: `sign`
- `type`: `panel`, `subtype`: `wood_panel`
- `type`: `furniture`, `subtype`: `shelf`

Rules:

- Use coarse `type` values for schema stability.
- Use `subtype` for image-specific labels when the evidence supports it.
- Fall back to a family type such as `object`, `furniture`, `surface`, or `opening` when subtype is uncertain.
- Do not extract people as graph nodes.
- Do not add source-specific classes such as `BuildingFurniture` as the primary node `type`.

## General Relation Taxonomy

Image-plane relations:

- `left_of`
- `right_of`
- `above`
- `below`
- `overlaps`
- `contains`

View-depth relations:

- `in_front_of`
- `behind`

Physical or semantic support relations:

- `attached_to`
- `mounted_on`
- `standing_on`
- `supports`
- `part_of`
- `adjacent_to`
- `aligned_with`
- `unknown`

Rules:

- Image-plane relations are view-dependent.
- View-depth relations are inferred and should carry uncertainty when ambiguous.
- Physical/topological relations are still image observations, not final world graph topology.
- Exact world relations such as `TOUCHES`, `INTERSECTS`, or `ADJACENT_TO` should appear only as optional downstream hints.

## World Graph Alignment Hints

Each node may include optional downstream hints:

```json
{
  "world_candidate_types": ["BuildingFurniture"],
  "world_alignment_note": "Candidate only; final class resolved downstream."
}
```

Each relation may include optional downstream hints:

```json
{
  "world_relation_hints": ["TOUCHES", "INSIDE"]
}
```

Rules:

- Hints are non-exclusive.
- Hints are not final labels.
- Hints should help candidate retrieval, not restrict it too early.
- The downstream Rule-based Cypher Query Generator and Neo4j World Graph Retrieval stages resolve exact candidate pairs.

## Confidence And Uncertainty

Each node and relation should include confidence in `[0, 1]`.

Recommended uncertainty categories:

- `occluded`
- `low_resolution`
- `glare_or_reflection`
- `ambiguous_type`
- `screen_content`
- `viewpoint_inferred`
- `partial_object`

Visible people should not become nodes. If relevant, record a global observation such as:

```text
visible people ignored for privacy and stability
```

## Evidence Policy

Evidence should be short and grounded in visible image cues.

Good evidence:

- "gray door visible on the left portion of the wall"
- "monitor occludes the lower-right wall area"
- "bright glass region appears behind foreground monitor"

Weak evidence:

- "probably exists because most lobbies have one"
- "likely part of CityGML class X"

## Relation To Expected Sketches

Expected graph sketches are test cases.

They may:

- choose a subset of this scheme
- prioritize certain node families
- define image-specific success criteria
- include local observations about a specific input

They must not:

- narrow the general schema to one image
- force exact world graph classes
- include downstream retrieval or matching logic

## Current Benchmark Sketches

- `EXPECTED_GRAPH_SKETCH_SMARTCITYLAB_LOBBY_GT.md`
