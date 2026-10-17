# Shorts Director ↔ AI Shorts Creator integration (draft)

This isolated module adds discovery-safe FilmCraft and EffectCraft CLI configuration **without modifying existing GUI, Qwen3-TTS, Gemini, or DrissionPage code**.

## What is included in this PR
- `src/automation/shorts_director_craft_bridge.py`: command discovery, MCP bridge configs, read-only import command planning
- Existing entrypoints and native editor projects are unchanged.

The complete experimental renderer, JSON schema, tests and demo media are distributed as a separate `shortsdirector_v1.zip` deliverable in the originating ChatGPT conversation. This PR **does not contain** the entire engine; importing an MP4 into Craft does not reconstruct editable mesh layers.

## Windows CLI setup

Install FilmCraft and EffectCraft separately and check their default install paths. Then:

```powershell
python src/automation/shorts_director_craft_bridge.py doctor
python src/automation/shorts_director_craft_bridge.py mcp-config --bridge
```

To control running editors, start their desktop executables with `--control 9876` and `--control 9877`; register the generated MCP server commands with a local MCP-compatible agent.

To prepare **but not execute** import commands against existing projects:

```powershell
python src/automation/shorts_director_craft_bridge.py draft-import --movie output/demo.mp4 --filmcraft-project my.fcproj --effectcraft-project my.ecproj
```

These generated command arrays are reviewable. The executing agent should use the actual Craft command introspection APIs and inspect the resulting project. The rendering package cannot be assumed to have a compatible native project format.

## ChatGPT specifics

ChatGPT's web UI cannot invoke a localhost stdio MCP server directly. Connecting from ChatGPT requires a separately authenticated, HTTPS-hosted MCP integration where supported and explicit user approval. Do not forward the unauthenticated FilmCraft/EffectCraft control ports to the Internet.

## Honest readiness status

- Command syntaxes were checked against the official upstream agent/CLI documentation.
- The application executables were not available on the build host; no successful live Craft import is claimed.
- Motion renderer/validation prototype was independently tested with generated art and FFmpeg. This branch contains only the GitHub integration bridge.
- Human review remains necessary for visual quality, pacing, factual accuracy, and suitability of any input style.
