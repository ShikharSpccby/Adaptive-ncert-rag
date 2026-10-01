# Render Worker

Turns a verified lesson script into a rendered Manim video.

## What's here (Stage 3 scope)

- `scenes/base_scene.py` — `BaseLessonScene`, the shared house-style every lesson inherits
  (colors, title placement). Change the palette here once, not per scene.
- `scenes/solve_linear_equation.py` — one hand-written scene (solving `2x + 3 = 7`), standing
  in for what the Coding LLM agent will eventually generate. Proves the render pipeline works
  before that agent exists.
- `render_concept.py` — the actual enforcement point: calls the `verify` service (Stage 2) for
  every mathematical claim in the lesson, and **refuses to render if any check fails**. This is
  not a comment or a design doc, it's a real gate — run it with the verify service down and it
  errors out before touching Manim.

## Run it locally

Needs the `verify` service running first (separate terminal):

```bash
cd services/verify
uvicorn app.main:app --port 8001
```

Then, in this directory:

```bash
pip install -r requirements.txt
python render_concept.py
```

Output lands in `output/videos/solve_linear_equation/480p15/SolveLinearEquation.mp4`
(the `output/` directory is gitignored — renders are regenerable, never commit them).

## Note on LaTeX

This uses Manim's `Text` (Pango-based), not `MathTex`, so there's no LaTeX distribution
dependency yet. Fine for plain algebra written as characters (`2x + 3 = 7`). If/when you need
properly typeset math notation (stacked fractions, integrals, etc.), install `texlive` on the
render machine and switch the relevant Mobjects to `MathTex` — that's an environment change,
not a change to `BaseLessonScene`'s structure.

## What's deliberately NOT here yet (lean v1 scope)

- The Coding LLM agent that would generate `scenes/*.py` files like the one here — this stage
  only proves the render half of the pipeline works.
- TTS narration — not wired in yet (also: the TTS providers discussed, like Edge-TTS, need
  outbound network access that may be restricted in sandboxed dev environments; this runs fine
  on a normal machine/server).
- Sandboxed/Dockerized execution of generated scene code — needed once scenes are LLM-generated
  rather than hand-written, since at that point the code is untrusted input. Deliberately not
  added yet while the scene is still hand-authored and trusted.
