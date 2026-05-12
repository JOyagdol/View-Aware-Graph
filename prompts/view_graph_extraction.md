# View-Aware Graph Extraction Prompt

You are given a street-view or urban-scene image. Extract a structured View-Aware Graph describing visible objects, their image-side spatial relationships, and any viewpoint assumptions that can be inferred from the image.

Return only JSON that conforms to `schemas/view_aware_graph.schema.json`.

Required focus:

- visible buildings, roads, sidewalks, signs, poles, vegetation, vehicles, and other stable urban landmarks
- image-relative positions and coarse depth/order relationships
- confidence for each object and relation
- short evidence text grounded in the image
- explicit uncertainty when an object or relation is ambiguous
