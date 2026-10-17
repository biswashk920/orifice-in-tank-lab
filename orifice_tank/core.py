"""Flow through an orifice in the wall of a cylindrical tank.

Conventions (all SI units, metres):
  L  = water level above the BOTTOM edge of the orifice
  head = L - yc = water height above the orifice CENTRE
  a, b = orifice sizes: circle (a=diameter), square (a=side),
         rectangle (a=width, b=height), triangle (a=base, b=height; base at the bottom)
"""
import math

G = 9.81   # gravity, m/s2
CV = 0.98  # velocity coefficient used for the jet

__all__ = ["G", "CV", "geometry", "flow", "discharge", "jet_velocity",
           "jet_range", "drain", "analyze"]


def geometry(shape, a, b=None):
    """Return (height, width(s), area, centroid_height). s is measured up from the bottom edge."""
    if min(a, b if b is not None else a) <= 0:
        raise ValueError("orifice sizes must be positive")
    if shape == "circle":
        r = a / 2
        return a, (lambda s: 2 * math.sqrt(max(r * r - (s - r) ** 2, 0))), math.pi * r * r, r
    if shape == "square":
        return a, (lambda s: a), a * a, a / 2
    if shape == "rectangle":
        return b, (lambda s: a), a * b, b / 2
    if shape == "triangle":
        return b, (lambda s: a * (1 - s / b)), a * b / 2, b / 3
    raise ValueError(f"unknown shape: {shape}")


def flow(L, shape, a, b=None, cd=0.61, n=400):
    """Discharge Q (m3/s) and wetted opening area (m2) at water level L.

    Q = Cd * integral of  w(s) * sqrt(2 g (L - s)) ds  over the part of the opening under water.
    Slicing the opening handles large orifices, where the head is not the same top and bottom.
    """
    H, w, _, _ = geometry(shape, a, b)
    top = min(L, H)
    if top <= 0:
        return 0.0, 0.0
    ds = top / n
    q = area = 0.0
    for i in range(n):
        s = (i + 0.5) * ds
        q += w(s) * math.sqrt(2 * G * (L - s)) * ds
        area += w(s) * ds
    return cd * q, area


def discharge(L, shape, a, b=None, cd=0.61, n=400):
    return flow(L, shape, a, b, cd, n)[0]


def jet_velocity(L, shape, a, b=None, cd=0.61):
    """Average jet speed (m/s): CV * Q / (Cd * wetted area). Small orifice -> CV * sqrt(2 g h)."""
    q, area = flow(L, shape, a, b, cd)
    return CV * q / (cd * area) if area > 0 else 0.0


def jet_range(v, y0):
    """Horizontal landing distance of a jet leaving horizontally at speed v from height y0."""
    return v * math.sqrt(2 * y0 / G)


def drain(L0, tank_d, shape, a, b=None, cd=0.61, L_stop=None):
    """Drain a cylindrical tank of diameter tank_d. Returns (times, levels) in s and m.

    dL/dt = -Q(L) / At. Flow slows down as the level falls and never quite reaches zero,
    so the run stops at L_stop (default: 2 % of the orifice height, at least 1 mm).
    """
    H = geometry(shape, a, b)[0]
    at = math.pi * tank_d ** 2 / 4
    L_stop = L_stop if L_stop is not None else max(0.02 * H, 0.001)
    t, L = 0.0, L0
    ts, Ls = [0.0], [L0]
    while L > L_stop and len(ts) < 20000:
        q = discharge(L, shape, a, b, cd, 100)
        dt = 0.01 * L * at / q                      # about 1 % level drop per step
        q_mid = discharge(max(L - 0.5 * dt * q / at, 1e-9), shape, a, b, cd, 100)
        L -= dt * q_mid / at                        # midpoint (RK2) step
        t += dt
        ts.append(t)
        Ls.append(max(L, 0.0))
    return ts, Ls


def analyze(head, shape, a, b=None, cd=0.61, tank_d=1.0, bottom_height=0.5, mode="drain"):
    """One-call summary used for quick checks: Q, jet speed, range and time to empty."""
    _, _, area, yc = geometry(shape, a, b)
    H = geometry(shape, a, b)[0]
    L = head + yc
    q = discharge(L, shape, a, b, cd)
    v = jet_velocity(L, shape, a, b, cd)
    y0 = bottom_height + min(yc, L / 2)
    out = {"level_above_bottom_m": L, "Q_m3s": q, "jet_velocity_ms": v,
           "range_m": jet_range(v, y0), "orifice_area_m2": area, "orifice_height_m": H}
    if mode == "drain":
        out["time_to_empty_s"] = drain(L, tank_d, shape, a, b, cd)[0][-1]
    return out
