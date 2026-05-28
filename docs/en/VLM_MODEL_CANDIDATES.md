# VLM Model Candidates

Last updated: 2026-05-22

## Purpose

This document records the first VLM candidate selection for the View-Aware Graph project.

The model must support:

- image input
- structured JSON generation, even if post-validation repair is needed
- object and spatial relation extraction
- confidence and evidence preservation
- provider-neutral configuration

Current project scope remains:

```text
Input Image
  -> VLM
  -> Structured View-Aware Graph JSON
```

## Selection Strategy

Use a free-first strategy.

Start with locally runnable or free-to-try VLMs to validate:

- whether the schema is usable
- whether the prompt is clear
- whether the GT lobby image can produce a meaningful graph
- what failure modes appear before paying for frontier models

Only upgrade to paid frontier models after the local/free baseline reveals what must be improved.

## Ollama Stage Is Not Training

The Ollama/local VLM stage is inference-only prompt engineering.

It is not:

- fine-tuning
- LoRA training
- distillation
- model adaptation
- dataset training

The goal is to run the frozen VLM with the current prompt, inspect the generated JSON, validate it against the schema, classify failures, and revise prompt/schema/parser behavior.

Training or fine-tuning should be considered only after enough curated image/output pairs and repeated failure patterns exist.

## Selection Criteria

The first baseline should be evaluated against the Smart City Lab lobby GT sketch, not generic benchmark scores alone.

Criteria:

- Vision quality for indoor architectural/furniture scenes
- JSON reliability under prompt-only structured output
- Spatial relation reasoning for `left_of`, `right_of`, `above`, `below`, `in_front_of`, `behind`, `attached_to`, `mounted_on`, `standing_on`, and `supports`
- Ability to preserve short visual evidence text
- Low hallucination rate for people, monitor screen contents, reflections, and tiny fixtures
- Setup speed in the project owner's local environment
- Cost: free local execution first, paid API later
- Privacy constraints for local images

## Free-First Candidate Shortlist

| Rank | Candidate | Role | Why It Is Considered | Main Risk |
| ---: | --- | --- | --- | --- |
| 1 | Qwen2.5-VL-3B-Instruct | Fast free smoke test | Smallest practical Qwen2.5-VL candidate; good for checking prompt/schema flow quickly. | Lower spatial reasoning quality; may need output repair. |
| 2 | Qwen2.5-VL-7B-Instruct | Primary free local baseline | Stronger open VLM while still easy to run locally. | Strict schema compliance is not guaranteed. |
| 3 | Qwen3-VL-8B-Instruct | Better small/medium local candidate | Newer Qwen3-VL family; good next step if setup supports it. | Runtime support may be less mature than Qwen2.5-VL in some tools. |
| 4 | Qwen2.5-VL-32B-Instruct quantized | Strong 32GB-class baseline | Mature Qwen2.5-VL 32B option; Ollama lists a 32B image model around 21GB. | Needs quantized runtime and careful image/context limits. |
| 5 | Qwen3-VL-32B-Instruct quantized | Best 32GB-class quality target | Newer Qwen3-VL 32B model; likely strongest local candidate under a 32GB VRAM target if it fits. | Heaviest local option; runtime/quant stability must be tested. |
| 6 | SmolVLM / SmolVLM2 class models | Lightweight fallback | Useful if hardware cannot run Qwen comfortably. | Likely weaker on cluttered indoor spatial relations. |
| 7 | InternVL3 8B class models | Local comparison | Strong open-source VLM family for multimodal reasoning. | More setup complexity; not the fastest first run. |

## Local VRAM Estimates

These are planning estimates, not hard guarantees. Actual VRAM depends on runtime, quantization, context length, image resolution, number of images, KV cache dtype, and whether the vision encoder/projector stays on GPU.

Use batch size 1 and downscale the GT image before comparing models.

| Candidate | Practical Local Form | Approx. Model Size / VRAM Planning Target | 32GB VRAM Fit | Project Use |
| --- | --- | ---: | --- | --- |
| Qwen2.5-VL-3B-Instruct | Ollama/LM Studio GGUF or Transformers quantized | 2-5GB | Easy | Fast smoke test |
| Qwen2.5-VL-7B-Instruct | Ollama/LM Studio GGUF or Transformers quantized | 5-9GB | Easy | Primary cheap baseline |
| Qwen3-VL-8B-Instruct | Transformers or supported local runtime | 8-14GB depending on precision/quant | Easy to moderate | Better small model comparison |
| InternVL3-8B | Transformers/vLLM | 12-18GB in BF16-style loading, less when quantized | Moderate | Comparison model |
| Qwen2.5-VL-32B-Instruct | Ollama `qwen2.5vl:32b` / AWQ / GGUF Q4-style | Ollama lists 21GB model size; plan 24-30GB effective VRAM | Good with 32GB if context/image tokens are controlled | Stable 32GB-class local target |
| Qwen3-VL-32B-Instruct | Quantized GGUF/AWQ-style runtime where available | Plan roughly 24-32GB effective VRAM for Q4-class use | Borderline but plausible with 32GB | Best 32GB-class quality target |
| Qwen2.5-VL-72B-Instruct | Quantized local runtime | Ollama lists 49GB model size | No | Out of 32GB scope |

Recommendation for a 32GB VRAM machine:

1. Start with Qwen2.5-VL-7B-Instruct to verify the prompt/schema pipeline.
2. Move to Qwen2.5-VL-32B-Instruct quantized for a stable high-quality local baseline.
3. Test Qwen3-VL-32B-Instruct quantized as the likely best local model under the 32GB target.
4. Keep paid models only as later reference runs.

If Qwen3-VL-32B is unstable or exceeds memory in the chosen runtime, use Qwen2.5-VL-32B-Instruct as the primary 32GB local baseline.

## Paid Upgrade Candidates

Use paid/frontier models only after the free-first loop produces a baseline output and known failure modes.

| Upgrade Rank | Candidate | Role |
| ---: | --- | --- |
| 1 | OpenAI latest account-available GPT vision-capable model, preferably `gpt-5.5` if available | High-quality schema-first reference run |
| 2 | OpenAI smaller GPT vision-capable model | Lower-cost paid iteration |
| 3 | Claude Sonnet 4.6 | Cross-provider reasoning validation |
| 4 | Gemini 3.5 Flash or current Gemini Flash-class model | Lower-cost hosted comparison |
| 5 | Gemini Pro-class current model | Higher-accuracy hosted comparison |

## Initial Baseline Decision

Use Qwen2.5-VL-3B-Instruct as the first smoke-test model, then Qwen2.5-VL-7B-Instruct as the first practical free local baseline.

For a 32GB VRAM workstation, the best local target to test after the smoke run is Qwen3-VL-32B-Instruct in a quantized runtime. The safer/stabler 32GB-class fallback is Qwen2.5-VL-32B-Instruct quantized.

Reason:

- The current bottleneck is not frontier accuracy yet; it is verifying schema, prompt, parsing, validation, and evaluation flow.
- Free local runs let us iterate without API cost or image-upload concerns.
- Qwen2.5-VL has official Hugging Face/Transformers support and is also available through local runtimes such as Ollama or LM Studio.
- The output may not be perfectly schema-valid, which is useful because it will reveal the parser/repair needs before paid model evaluation.
- This stage is prompt/schema/parser iteration with frozen models, not training.

Do not hard-code any model in core code. The selected baseline is an experiment default, not a permanent dependency.

## Recommended Run Order

1. Qwen2.5-VL-3B-Instruct: quick free smoke test.
2. Qwen2.5-VL-7B-Instruct: primary free local baseline.
3. Qwen2.5-VL-32B-Instruct quantized: stable 32GB-class local baseline.
4. Qwen3-VL-32B-Instruct quantized: best 32GB-class local quality candidate if the runtime is stable.
5. SmolVLM-class lightweight model if Qwen is too heavy.
6. Optional local comparison with InternVL3-8B or Gemma 3 vision-capable variants.
7. Paid upgrade to OpenAI latest GPT vision-capable model only after the local/free output is scored.

## First Evaluation Plan

Run each candidate on the same GT input and prompt, then compare outputs against:

- `schemas/view_aware_graph.schema.json`
- `docs/en/EXPECTED_GRAPH_SKETCH_SMARTCITYLAB_LOBBY_GT.md`
- `examples/outputs/smartcitylab_lobby_gt_minimal.json`

Minimum acceptance checks:

- Valid JSON or repairable JSON
- Passes schema validation after minimal repair
- Does not extract people as nodes
- Extracts main wall, door/opening, floor, foreground monitor/display objects as `object` nodes, and at least one furniture/surface/panel node
- Captures foreground monitor occlusion
- Preserves evidence and uncertainty

Failure categories:

- invalid JSON
- schema mismatch
- missing core object
- hallucinated object
- wrong relation
- over-focus on monitor screen content
- people extracted as nodes
- weak or generic evidence

## Configuration Policy

Keep provider/model selection outside core logic:

```toml
[vlm]
provider = ""
model = ""
```

Local credentials stay in `.env`, never in source control. Free local models should not require API keys.

## Sources Checked

- Qwen2.5-VL Transformers documentation: https://huggingface.co/docs/transformers/en/model_doc/qwen2_5_vl
- Qwen2.5-VL 3B model card: https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct
- Qwen2.5-VL 7B model card: https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct
- Qwen2.5-VL 32B AWQ model card: https://huggingface.co/Qwen/Qwen2.5-VL-32B-Instruct-AWQ
- Qwen3-VL 8B model card: https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct
- Qwen3-VL 32B model card: https://huggingface.co/Qwen/Qwen3-VL-32B-Instruct
- Ollama vision documentation: https://docs.ollama.com/capabilities/vision
- Ollama Qwen2.5VL library: https://ollama.com/library/qwen2.5vl
- LM Studio image input documentation: https://lmstudio.ai/docs/python/llm-prediction/image-input
- LM Studio Qwen2.5-VL 3B: https://lmstudio.ai/models/qwen/qwen2.5-vl-3b
- LM Studio Qwen2.5-VL 7B: https://lmstudio.ai/models/qwen/qwen2.5-vl-7b/
- SmolVLM Transformers documentation: https://huggingface.co/docs/transformers/model_doc/smolvlm
- Gemma 3 Transformers documentation: https://huggingface.co/docs/transformers/model_doc/gemma3
- InternVL3 8B model card: https://huggingface.co/OpenGVLab/InternVL3-8B
- OpenAI Models: https://platform.openai.com/docs/models
- OpenAI Images and Vision: https://platform.openai.com/docs/guides/vision
- OpenAI Structured Outputs: https://platform.openai.com/docs/guides/structured-outputs
- Claude Models Overview: https://docs.anthropic.com/en/docs/about-claude/models/overview
- Gemini Models: https://ai.google.dev/gemini-api/docs/models
