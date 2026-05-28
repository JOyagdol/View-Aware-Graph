# Example Input Assessment

Last updated: 2026-05-14

## Purpose

This document records the initial assessment of local input images under `data/raw/` for View-Aware Graph extraction.

The goal is to decide whether each image is useful for the current project scope:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

These files are local raw inputs and are intentionally not committed to Git.

## Current Local Images

| File | Type | Resolution | Size | Assessment |
| --- | --- | ---: | ---: | --- |
| `data/raw/smartcitylab_lobby/SmartCityLab_Lobby_GT.jpg` | Real Smart City Lab lobby photo | 4000 x 3000 | 3,127,461 bytes | Good primary input for early VLM graph extraction |
| `data/raw/smartcitylab_lobby/SmartCityLab_Lobby_DT.png` | Digital twin lobby render | 1222 x 1120 | 84,585 bytes | Useful paired synthetic input, but weak as a standalone graph extraction benchmark |

## GT Photo

`SmartCityLab_Lobby_GT.jpg` is suitable as the first primary input because it contains many stable visual cues:

- corridor geometry
- walls, floor, ceiling, columns, and door
- monitors and display stands
- wood panels and shelving
- ceiling cameras, lights, tracks, and fixtures
- image-relative spatial relationships and depth ordering

Known issues:

- A monitor occupies a large foreground region and may distract the VLM from architectural structure.
- There is glare and reflection on the floor and foreground glass/screen surfaces.
- A person is partially visible, so privacy/shareability should be confirmed before public use.
- The scene is indoor; if the downstream world graph is primarily outdoor CityGML, this image is still useful for pipeline development but not representative of every final localization scenario.

Recommended use:

- Use as the first real-image sanity check for object extraction and view-aware spatial relations.
- Consider an additional cropped or anonymized version that reduces the foreground monitor/person distraction.
- Keep the original as a challenging real-world example once privacy/shareability is acceptable.

## DT Render

`SmartCityLab_Lobby_DT.png` is useful because it is paired with the same lobby concept and can support later GT-vs-DT domain-gap checks.

As a first standalone VLM input, it is weaker than the GT photo:

- The image is dark and low contrast.
- Materials and textures are sparse.
- Distinct semantic objects are limited.
- Several GT landmarks are absent or hard to recognize.
- It mainly exposes coarse geometry rather than rich object relationships.

Recommended use:

- Use as a paired synthetic comparison image after the GT prompt path works.
- Treat it as a coarse-geometry extraction test, not as the main benchmark.
- Improve future DT renders by matching the GT viewpoint, increasing lighting/contrast, and adding recognizable landmarks such as monitors, columns, doors, ceiling fixtures, and wall/floor material cues.

## Initial Decision

Use both images, but with different roles:

- GT photo: primary early input for VLM-to-graph development.
- DT render: secondary paired input for synthetic/real comparison and robustness checks.

The expected graph sketch for the GT image is documented in [`EXPECTED_GRAPH_SKETCH_SMARTCITYLAB_LOBBY_GT.md`](EXPECTED_GRAPH_SKETCH_SMARTCITYLAB_LOBBY_GT.md).
