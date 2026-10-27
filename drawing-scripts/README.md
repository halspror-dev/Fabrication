# Drawing scripts (3D views, PASS/FAIL checks, DXFs and STLs)

These scripts need Python 3 plus `pip install shapely numpy scipy ezdxf manifold3d matplotlib`. Shapely must be 2.x.
There are no 2D drawing pages or 1:1 cut templates any more: the sleeves are 3D printed and the plates are ordered cut from the DXFs.

1. Run `python3 templates.py` to print every PASS/FAIL clearance check (keeper, trigger, tabs, pivot, sleeves, grip span, can positions). It ends with `ok` or `FAIL`.
2. Run `python3 check3d.py templates.py` (needs scipy) for the real-shape 3D clearances: every pair of parts in the 3D model, in 5 states. It prints a short PASS/FAIL line per state; the full table goes to `check3d-table.txt` (`--full` prints it instead). Pairs that touch on purpose are listed in JOINT_PARTS/TOUCH at its top. It exits 1 on any FAIL, and a Claude Code hook runs it before every `git push` and blocks the push on a FAIL.
3. Run `python3 render3d.py templates.py iso.pdf` to make the 3D views, the tab and keeper close-ups and the exploded views. It loads the part geometry from templates.py.
4. DXFs (the 4 laser-cut plates): `python3 make_dxf.py templates.py OUTDIR`.
5. STLs for printing (the 2 sleeves, plus the 4 plates at real thickness for a plastic test build, in mm): `python3 make_stl.py templates.py OUTDIR`.

v0.95: the printed sleeves are built as real solids in sleeves.py from the sections in templates.py (TRIG_SLV, GRIP_SLV). render3d.py and check3d.py use the same solids. The grip span is set by BAR_BACK, BOW and SLV_T; the checks print the span per finger.

Edit part shapes near the top of templates.py: the collar, keeper, frame points, trigger, finger plate, the pivot P = (-1.50, 1.215) and the up-stop S = (-2.50, 0.87). The trigger checks assume a button travel BT at the top of the checks block.

Coordinates are in inches. The origin is the can's center at the collar's top surface. x points forward (the spray direction), y points to the can's left, and z points up.

render3d.py is a custom z-buffer renderer. It replaced matplotlib's 3D plotting, which drew colors bleeding through parts. Checking the renders without loading every image:

6. `python3 pagediff.py OUTDIR` lists the render preview PNGs that changed against `OUTDIR/../last-review/`. `last-review/` is not in git: in a fresh checkout, build the previous version's commit into OUTDIR first and run `python3 pagediff.py OUTDIR --accept`, then build the new version.
7. Send only the CHANGED/NEW pages, with a one-line note on what changed, to the `render-reviewer` subagent (`.claude/agents/render-reviewer.md`). It checks for wrong overlaps, labels, balloons, and both open/closed states, and replies PASS/FAIL per page. Once it passes, run `python3 pagediff.py OUTDIR --accept`.
8. Before a version goes to carlie or out for an order, have the subagent check all pages once.
