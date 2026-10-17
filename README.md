# Orifice in a Tank

**[Open the Live App](https://biswashk920.github.io/orifice-in-tank-lab/)**

Flow through an orifice in a cylindrical tank: a Python package for the hydraulics, and a browser app that animates the jet and the falling water level.

## What it does
- Orifice shapes: circle, square, rectangle, triangle
- Two modes: **constant head** and **draining tank**
- Outputs: jet velocity, discharge, jet landing distance, time to empty, head vs. time graph
- Large orifices are handled by slicing the opening, because the water is deeper (and faster) at the bottom than at the top

## Method
- Small orifice (Torricelli): `v = sqrt(2 g h)`, `Q = Cd * A * sqrt(2 g h)`
- Any orifice: `Q = Cd * integral of w(s) * sqrt(2 g (L - s)) ds` over the part under water
- Jet: leaves horizontally at `v = Cv * Q / (Cd * A_wet)` with `Cv = 0.98`, lands at `x = v * sqrt(2 y / g)`
- Draining: `dL/dt = -Q(L) / A_tank`, solved with a midpoint step

## Use it
Browser app: open `docs/index.html` (or enable GitHub Pages on the `/docs` folder).

Python:
```python
from orifice_tank import analyze
print(analyze(head=1.5, shape="circle", a=0.05, cd=0.61, tank_d=1.0, bottom_height=1.0))
```

Tests (checked against textbook formulas):
```
python -m pytest
```

## Assumptions
Cd is constant, the tank is cylindrical, the jet leaves horizontally, and there is no air or viscous drag on the jet.

## 3D version
Open `docs/3d.html` (also on GitHub Pages as `/3d.html`). Drag to rotate, scroll to zoom. It uses three.js from a CDN, so it needs an internet connection.
- Glass tank with a real hole in the shape of the orifice, water level that drops, and a jet drawn along the exact parabola
- Jet narrows after the orifice (vena contracta), is coloured by speed, and breaks into spray and a splash with a growing puddle
- Overlays: pressure arrows on the wall, streamlines inside the tank, dimension labels, ground tape for the range, cut-away view
- Camera presets, slow motion, and a screenshot button
The numbers come from `docs/physics.js`, which uses the same equations as the Python package.
