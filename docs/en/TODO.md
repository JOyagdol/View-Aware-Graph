# View-Aware Graph TODO

Last updated: 2026-05-12

## Immediate Setup Tasks

0. Convention document creation and rules
   - [x] Create project convention rules.
   - [x] Add root `AGENTS.md` so Codex can automatically reference local project rules.
   - [x] Add the convention document `AGENTS.md` to `.gitignore`.
   - [x] Keep `AGENTS.md` detailed enough for Codex automatic reference while keeping `docs/en/CONVENTIONS.md` as the tracked convention source.
   - [x] Define the documentation rule: keep docs in both English and Korean.
   - [x] Define the documentation rule: keep Korean docs local-only under `docs/ko/`.
   - [x] Document project purpose, overview, and structure.

1. Project structure
   - [x] Create baseline source package under `src/view_aware_graph/`.
   - [x] Create config, schema, prompt, script, test, data, and example directories.
   - [x] Add placeholder files so intended empty directories are preserved.
   - [x] Add initial View-Aware Graph JSON schema placeholder.
   - [x] Keep repository structure scoped to image-to-graph extraction only.

2. Git
   - [x] Initialize Git repository.
   - [x] Set initial branch to `main`.
   - [x] Add baseline `.gitignore`, `.gitattributes`, and `.editorconfig`.
   - [x] Ignore local-only docs and artifacts.
   - [ ] Create the first commit after reviewing the initialized files.

3. Conda environment setup
   - [x] Replace previous local setup instructions with conda setup instructions.
   - [x] Add `environment.yml`.
   - [ ] Project owner creates and verifies the conda environment locally.

## Next Work Queue

- [ ] Define the first production prompt for image-to-graph extraction.
- [ ] Choose the initial VLM provider adapter interface.
- [ ] Implement image input normalization.
- [ ] Implement VLM response parsing into structured graph JSON.
- [ ] Add schema validation for generated graph JSON.
