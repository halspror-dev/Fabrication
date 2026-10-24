# Drawing scripts (generate templates-vX.Y.pdf)

These scripts need Python 3 plus `pip install matplotlib shapely pypdf numpy`. Shapely must be 2.x.

1. Run `python3 templates.py t.pdf prev.png` to make pages 1–6 (the 1:1 templates, the assembly side and top views, the keeper section, and the trigger motion and sections). It also writes preview PNGs.
2. Run `python3 render3d.py templates.py iso.pdf` to make pages 7–8 (the 3D views and the angle clip close-up). It loads the part geometry from templates.py.
3. Merge the two into one PDF:
   `python3 -c "from pypdf import PdfWriter; w=PdfWriter(); [w.append(f) for f in ['t.pdf','iso.pdf']]; w.write('templates-vX.Y.pdf')"`

Edit part shapes near the top of templates.py: the collar, keeper, frame points, trigger, finger plate, the pivot P = (-1.50, 1.215) and the up-stop S = (-2.50, 0.87). Page 6 (trigger motion) assumes a button travel BT near its top. Update the version number in the page-1 footer text.

Coordinates are in inches. The origin is the can's center at the collar's top surface. x points forward (the spray direction), y points to the can's left, and z points up.

render3d.py is a custom z-buffer renderer. It replaced matplotlib's 3D plotting, which drew colors bleeding through parts. Before sending, check every rendered view for wrong overlaps and labels.
