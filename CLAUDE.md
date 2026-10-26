# Fabrication

- Finding your way around: if graphify-out/graph.json exists, run graphify query "<question>" to see how the code connects before you grep. Refresh it with graphify update . after big changes.
- Cross-project notes: `.claude/skills/project-notes`. Read your inbox in `halspror-dev/project-notes` when a thread starts and update your status file before it ends.
- Web research: `.claude/skills/research`. Fetch with its tool, read grep matches not whole pages, and only report what a saved page shows.
- Design changes: every moving part gets an OPEN and CLOSED (or rest and full-travel) state, drawn and checked for clearances (`python3 drawing-scripts/templates.py` prints the checks), so the mechanism is proven before anything is cut. No 2D drawing pages or 1:1 templates (carlie, 2026-10-26): parts are printed and cuts ordered from the DXFs.
- Checking a build: run `check3d.py` (short summary) and `pagediff.py`; send only the changed pages to the `render-reviewer` subagent (`.claude/agents/render-reviewer.md`); don't open render PNGs or the PDF in the main thread. Full visual pass on all render pages (by the subagent) once before a version goes to carlie or out for an order.
- One design version per thread: read `drawing-scripts/STATE.md` first; update it and commit before ending. Start a fresh thread after two failed fixes of the same problem.
