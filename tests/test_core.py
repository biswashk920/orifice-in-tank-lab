"""Checks against textbook formulas. Run: python -m pytest   (or)   python -m tests.test_core"""
import math
from orifice_tank import G, CV, discharge, jet_velocity, jet_range, drain


def close(a, b, tol):
    assert abs(a - b) <= tol * abs(b), (a, b)


def test_small_circle_matches_torricelli():
    d, h = 0.01, 1.0
    close(discharge(h + d / 2, "circle", d), 0.61 * math.pi * d * d / 4 * math.sqrt(2 * G * h), 0.01)


def test_rectangle_matches_exact_integral():
    w, H, L = 0.2, 0.1, 0.8
    exact = 0.61 * (2 / 3) * w * math.sqrt(2 * G) * (L ** 1.5 - (L - H) ** 1.5)
    close(discharge(L, "rectangle", w, H), exact, 1e-3)


def test_square_equals_rectangle():
    close(discharge(0.7, "square", 0.1), discharge(0.7, "rectangle", 0.1, 0.1), 1e-9)


def test_jet_range_is_two_sqrt_h_y():
    d, h, y0 = 0.01, 1.0, 2.0
    v = jet_velocity(h + d / 2, "circle", d)
    close(jet_range(v, y0), 2 * CV * math.sqrt(h * y0), 0.01)


def test_drain_time_matches_theory():
    d, D, h0, r = 0.01, 1.0, 1.0, 0.005
    ts, _ = drain(r + h0, D, "circle", d, L_stop=r + 0.2)
    theory = 2 * (math.pi * D * D / 4) / (0.61 * math.pi * r * r * math.sqrt(2 * G)) * (math.sqrt(h0) - math.sqrt(0.2))
    close(ts[-1], theory, 0.02)


def test_bigger_orifice_drains_faster():
    t_small = drain(1.0, 1.0, "circle", 0.02)[0][-1]
    t_big = drain(1.0, 1.0, "circle", 0.08)[0][-1]
    assert t_big < t_small


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok ", name)
