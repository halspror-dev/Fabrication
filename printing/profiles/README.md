# Slicer profiles

One exported file per profile (printer, filament, process), committed after every change so git is the version
history. Name files `<kind>-<name>-v<N>.<ext>` (for example `filament-petg-<brand>-v1.json`) and bump `N` on any
change. Each commit message says what changed and why, and names the test record in `../tests/` that justifies it.
Export from the slicer on BigGuy; never sync these through a slicer cloud.
