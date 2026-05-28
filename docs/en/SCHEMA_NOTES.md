# Schema Notes

Last updated: 2026-05-22

## Version 0.1.0

`schemas/view_aware_graph.schema.json` now implements the general View-Aware Graph scheme instead of the earlier outdoor/street placeholder taxonomy.

Key contract decisions:

- Node `type` is a coarse image-observed semantic family.
- Specific object names such as monitor, display stand, ceiling camera, light fixture, sign, shelf, or wood panel belong in `label` and optional `subtype`.
- The current coarse node types are `wall`, `door`, `window`, `opening`, `floor`, `ceiling`, `surface`, `panel`, `furniture`, `object`, and `unknown`.
- Final CityGML/3DCitySG classes are represented only as optional `world_candidate_types` hints.
- People are not valid graph nodes.
- Bounding boxes use normalized `x`, `y`, `width`, `height` values in `[0, 1]`.
- `bbox_format` is limited to `normalized_xywh`, `region_only`, or `unknown`; pixel-coordinate boxes are intentionally out of scope for schema version `0.1.0`.
- Nodes can carry `region`, `depth_hint`, `priority`, `occlusion`, `uncertainty`, evidence, and confidence.
- Relations include image-plane, view-depth, support, attachment, part-whole, adjacency, and alignment relationships.
- Exact downstream topology relations may appear only as optional `world_relation_hints`.

The minimal GT-derived synthetic example is:

```text
examples/outputs/smartcitylab_lobby_gt_minimal.json
```

Python schema validation still needs to be run by the project owner in the conda environment.
