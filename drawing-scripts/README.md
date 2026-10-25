# Drawing scripts (generate templates-vX.Y.pdf)

These scripts need Python 3 plus `pip install matplotlib shapely pypdf numpy scipy ezdxf manifold3d`. Shapely must be 2.x.

1. Run `python3 templates.py t.pdf prev.png` to make pages 1–7 (the 1:1 templates, the assembly side and top views, the keeper section, the trigger motion and sections, and the open/closed checks). It also writes preview PNGs.
2. Run `python3 check3d.py templates.py chk.pdf` (needs scipy) for the real-shape 3D clearance page: every pair of parts in the 3D model, in 5 states. Pairs that touch on purpose are listed in JOINT_PARTS/TOUCH at its top.
3. Run `python3 render3d.py templates.py iso.pdf` to make the 3D views, the tab and keeper close-ups and the exploded views. It loads the part geometry from templates.py.
4. Merge them into one PDF:
   `python3 -c "from pypdf import PdfWriter; w=PdfWriter(); [w.append(f) for f in ['t.pdf','chk.pdf','iso.pdf']]; w.write('templates-vX.Y.pdf')"`
5. DXFs (the 4 laser-cut plates): `python3 make_dxf.py templates.py OUTDIR`.
6. STLs for printing (the 2 sleeves, plus the 4 plates at real thickness for a plastic test build, in mm): `python3 make_stl.py templates.py OUTDIR`.

v0.95: the printed sleeves are built as real solids in sleeves.py from the sections in templates.py (TRIG_SLV, GRIP_SLV). render3d.py and check3d.py use the same solids. The grip span is set by BAR_BACK, BOW and SLV_T; the checks page prints the span per finger.

Edit part shapes near the top of templates.py: the collar, keeper, frame points, trigger, finger plate, the pivot P = (-1.50, 1.215) and the up-stop S = (-2.50, 0.87). Page 6 (trigger motion) assumes a button travel BT near its top. Update the version number in the page-1 footer text.

Coordinates are in inches. The origin is the can's center at the collar's top surface. x points forward (the spray direction), y points to the can's left, and z points up.

render3d.py is a custom z-buffer renderer. It replaced matplotlib's 3D plotting, which drew colors bleeding through parts. Before sending, check every rendered view for wrong overlaps and labels.
