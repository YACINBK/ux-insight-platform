from manim import *
import numpy as np
import math

# Utilities to build the configuration once and reuse across scenes

def build_base(m: float = 0.0, y1: float = 1.5, y2: float = -1.5, theta: float = 65*DEGREES):
    x_left, x_right = -7, 7
    def line_points(m, b):
        return np.array([x_left, m*x_left + b, 0]), np.array([x_right, m*x_right + b, 0])
    L1 = Line(*line_points(m, y1), color=GRAY_E, stroke_width=6)
    L2 = Line(*line_points(m, y2), color=GRAY_E, stroke_width=6)
    t_len = 10
    dir_vec = np.array([np.cos(theta), np.sin(theta), 0.0])
    T = Line(-dir_vec*t_len/2, dir_vec*t_len/2, color=GRAY_E, stroke_width=6)
    p0 = T.get_start(); v = T.get_end() - T.get_start()
    def intersect_with_line(b):
        denom = (v[1] - m*v[0])
        s = (m*p0[0] + b - p0[1]) / denom
        p = p0 + s*v
        return p
    A = intersect_with_line(y1)
    B = intersect_with_line(y2)
    tL = np.array([1.0, m, 0.0]); tL = tL/np.linalg.norm(tL)
    tT = dir_vec/np.linalg.norm(dir_vec)
    return L1, L2, T, A, B, (tL, tT)


def add_line_labels(scene: Scene, L1: Line, L2: Line, T: Line):
    fs = 28
    x_p = L1.point_from_proportion(0.08)
    y_p = L2.point_from_proportion(0.08)
    z_p = T.point_from_proportion(0.85)
    x_lbl = Text("x", font_size=fs, color=BLACK).move_to(x_p + UP*0.35)
    y_lbl = Text("y", font_size=fs, color=BLACK).move_to(y_p + DOWN*0.35)
    t_vec = T.get_end() - T.get_start()
    t_unit = t_vec / np.linalg.norm(t_vec)
    n_unit = np.array([-t_unit[1], t_unit[0], 0.0])
    z_lbl = Text("z", font_size=fs, color=BLACK).move_to(z_p + n_unit*0.35)
    scene.add(x_lbl, y_lbl, z_lbl)


def _minor_ccw_from_angles(a1: float, a2: float):
    delta = (a2 - a1) % (2 * math.pi)
    if delta <= math.pi:
        return a1, delta
    else:
        return a2, (2 * math.pi - delta)


def filled_minor_angle(point: np.ndarray, u: np.ndarray, v: np.ndarray, radius: float, color) -> VGroup:
    a1 = math.atan2(u[1], u[0]); a2 = math.atan2(v[1], v[0])
    start, sweep = _minor_ccw_from_angles(a1, a2)
    sector = Sector(arc_center=point, radius=radius, start_angle=start, angle=sweep,
                    color=color, fill_opacity=0.35, stroke_opacity=0)
    outline = Arc(arc_center=point, radius=radius, start_angle=start, angle=sweep,
                  color=color, stroke_width=6)
    return VGroup(sector, outline)


def mid_tick(point: np.ndarray, u: np.ndarray, v: np.ndarray, radius: float, color, count: int = 2) -> VGroup:
    a1 = math.atan2(u[1], u[0]); a2 = math.atan2(v[1], v[0])
    start, sweep = _minor_ccw_from_angles(a1, a2)
    mid = start + sweep/2
    ticks = VGroup()
    for i in range(count):
        shift = (i- (count-1)/2)*0.08
        r1 = radius - 0.06 + shift
        r2 = radius + 0.06 + shift
        p1 = point + np.array([math.cos(mid)*r1, math.sin(mid)*r1, 0])
        p2 = point + np.array([math.cos(mid)*r2, math.sin(mid)*r2, 0])
        ticks.add(Line(p1, p2, color=color, stroke_width=4))
    return ticks


def label_points(A, B):
    dotA = Dot(A, color=GRAY_E); dotB = Dot(B, color=GRAY_E)
    labA = Text("A", font_size=32, color=BLACK).next_to(dotA, RIGHT, buff=0.12)
    labB = Text("B", font_size=32, color=BLACK).next_to(dotB, RIGHT, buff=0.12)
    return VGroup(dotA, dotB, labA, labB)


class CorrespondingAnglesEqual(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        m = 0.0
        L1, L2, T, A, B, (tL, tT) = build_base(m=m, y1=1.6, y2=-1.6, theta=65*DEGREES)
        self.add(L1, L2, T)
        # Custom A/B labels with increased spacing like other scenes
        dotA = Dot(A, color=GRAY_E); dotB = Dot(B, color=GRAY_E)
        labA = Text("A", font_size=32, color=BLACK).next_to(dotA, UP, buff=0.5)
        labB = Text("B", font_size=32, color=BLACK).next_to(dotB, DOWN, buff=0.7)
        self.add(dotA, dotB, labA, labB)
        # x on right of upper, y on left of lower, z perpendicular
        fs = 28
        x_p = L1.point_from_proportion(0.92)
        y_p = L2.point_from_proportion(0.08)
        z_p = T.point_from_proportion(0.85)
        x_lbl = Text("x", font_size=fs, color=BLACK).move_to(x_p + UP*0.35)
        y_lbl = Text("y", font_size=fs, color=BLACK).move_to(y_p + DOWN*0.35)
        t_vec = T.get_end() - T.get_start(); t_unit = t_vec/np.linalg.norm(t_vec)
        n_unit = np.array([-t_unit[1], t_unit[0], 0.0])
        z_lbl = Text("z", font_size=fs, color=BLACK).move_to(z_p + n_unit*0.35)
        self.add(x_lbl, y_lbl, z_lbl)
        # Corresponding angles
        leftL = -tL; upT = tT
        a_arc = filled_minor_angle(A, leftL, upT, radius=0.55, color=BLUE_B)
        b_arc = filled_minor_angle(B, leftL, upT, radius=0.55, color=BLUE_B)
        self.add(a_arc, b_arc)
        stmt = MathTex(r"\hat{zAx} = \hat{zBy}", color=RED_D).scale(0.9).to_corner(RIGHT+UP)
        par = MathTex(r"(Ax)//(By)", color=RED_D).scale(0.9).to_corner(LEFT+UP)
        self.add(stmt, par)
        self.wait(0.1)


class AlternateInteriorAnglesEqual(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        L1, L2, T, A, B, (tL, tT) = build_base(m=0.0, y1=1.6, y2=-1.6, theta=65*DEGREES)
        self.add(L1, L2, T)
        # Custom A/B labels with increased spacing
        dotA = Dot(A, color=GRAY_E); dotB = Dot(B, color=GRAY_E)
        labA = Text("A", font_size=32, color=BLACK).next_to(dotA, UP, buff=0.5)
        labB = Text("B", font_size=32, color=BLACK).next_to(dotB, DOWN, buff=0.7)
        self.add(dotA, dotB, labA, labB)
        # Custom line labels: x right on upper, y left on lower, z perpendicular
        fs = 28
        x_p = L1.point_from_proportion(0.92)
        y_p = L2.point_from_proportion(0.08)
        z_p = T.point_from_proportion(0.85)
        x_lbl = Text("x", font_size=fs, color=BLACK).move_to(x_p + UP*0.35)
        y_lbl = Text("y", font_size=fs, color=BLACK).move_to(y_p + DOWN*0.35)
        t_vec = T.get_end() - T.get_start(); t_unit = t_vec/np.linalg.norm(t_vec)
        n_unit = np.array([-t_unit[1], t_unit[0], 0.0])
        z_lbl = Text("z", font_size=fs, color=BLACK).move_to(z_p + n_unit*0.35)
        self.add(x_lbl, y_lbl, z_lbl)
        rightL = tL; leftL = -tL; upT = tT; downT = -tT
        a_arc = filled_minor_angle(A, downT, rightL, radius=0.55, color=PURE_RED)
        b_arc = filled_minor_angle(B, upT, leftL, radius=0.55, color=PURE_RED)
        self.add(a_arc, b_arc)
        # Equality ticks like implication scene
        self.add(mid_tick(A, downT, rightL, radius=0.55, color=PURE_RED, count=2))
        self.add(mid_tick(B, upT, leftL, radius=0.55, color=PURE_RED, count=2))
        # Hats: small hat accents
        stmt = MathTex(r"B\hat{A}x = A\hat{B}y", color=RED_D).scale(0.9).to_corner(RIGHT+UP)
        par = MathTex(r"(Ax)//(By)", color=RED_D).scale(0.9).to_corner(LEFT+UP)
        self.add(stmt, par)
        self.wait(0.1)


class CointeriorAnglesSupplementary(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        L1, L2, T, A, B, (tL, tT) = build_base(m=0.0, y1=1.6, y2=-1.6, theta=65*DEGREES)
        self.add(L1, L2, T)
        # Custom labels to push B lower
        dotA = Dot(A, color=GRAY_E); dotB = Dot(B, color=GRAY_E)
        labA = Text("A", font_size=32, color=BLACK).next_to(dotA, UR, buff=0.18)
        labB = Text("B", font_size=32, color=BLACK).next_to(dotB, DOWN, buff=0.6)
        self.add(dotA, dotB, labA, labB)
        # Place x and y on right side for both lines; z perpendicular
        fs = 28
        x_p = L1.point_from_proportion(0.92)
        y_p = L2.point_from_proportion(0.92)
        z_p = T.point_from_proportion(0.85)
        x_lbl = Text("x", font_size=fs, color=BLACK).move_to(x_p + UP*0.35)
        y_lbl = Text("y", font_size=fs, color=BLACK).move_to(y_p + DOWN*0.35)
        t_vec = T.get_end() - T.get_start(); t_unit = t_vec/np.linalg.norm(t_vec)
        n_unit = np.array([-t_unit[1], t_unit[0], 0.0])
        z_lbl = Text("z", font_size=fs, color=BLACK).move_to(z_p + n_unit*0.35)
        self.add(x_lbl, y_lbl, z_lbl)
        rightL = tL; leftL = -tL; upT = tT; downT = -tT
        a_arc = filled_minor_angle(A, downT, rightL, radius=0.55, color=TEAL_D)
        b_arc = filled_minor_angle(B, upT, rightL, radius=0.55, color=TEAL_D)
        self.add(a_arc, b_arc)
        stmt = MathTex(r"\hat{BAx} + A\hat{B}y = 180^\circ", color=RED_D).scale(0.9).to_corner(RIGHT+UP)
        par = MathTex(r"(Ax)//(By)", color=RED_D).scale(0.9).to_corner(LEFT+UP)
        self.add(stmt, par)
        self.wait(0.1)


class AlternateInteriorAnglesImplication(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        L1, L2, T, A, B, (tL, tT) = build_base(m=0.0, y1=1.6, y2=-1.6, theta=65*DEGREES)
        self.add(L1, L2, T)
        # Custom A/B labels with increased spacing
        dotA = Dot(A, color=GRAY_E); dotB = Dot(B, color=GRAY_E)
        labA = Text("A", font_size=32, color=BLACK).next_to(dotA, UP, buff=0.5)
        labB = Text("B", font_size=32, color=BLACK).next_to(dotB, DOWN, buff=0.7)
        self.add(dotA, dotB, labA, labB)
        # Custom line labels: x on right of upper line, y on left of lower line, z perpendicular
        fs = 28
        x_p = L1.point_from_proportion(0.92)
        y_p = L2.point_from_proportion(0.08)
        z_p = T.point_from_proportion(0.85)
        x_lbl = Text("x", font_size=fs, color=BLACK).move_to(x_p + UP*0.35)
        y_lbl = Text("y", font_size=fs, color=BLACK).move_to(y_p + DOWN*0.35)
        t_vec = T.get_end() - T.get_start(); t_unit = t_vec/np.linalg.norm(t_vec)
        n_unit = np.array([-t_unit[1], t_unit[0], 0.0])
        z_lbl = Text("z", font_size=fs, color=BLACK).move_to(z_p + n_unit*0.35)
        self.add(x_lbl, y_lbl, z_lbl)
        rightL = tL; leftL = -tL; upT = tT; downT = -tT
        a_arc = filled_minor_angle(A, downT, rightL, radius=0.55, color=PURE_RED)
        b_arc = filled_minor_angle(B, upT, leftL, radius=0.55, color=PURE_RED)
        self.add(a_arc, b_arc)
        self.add(mid_tick(A, downT, rightL, radius=0.55, color=PURE_RED, count=2))
        self.add(mid_tick(B, upT, leftL, radius=0.55, color=PURE_RED, count=2))
        stmt = MathTex(r"Si\ B\hat{A}x\ =\ A\hat{B}y\ alors\ (Ax)//(By).", color=RED_D)
        stmt.to_edge(UP, buff=0.45)
        stmt.shift(LEFT*2.8)
        self.add(stmt)
        self.wait(0.1)
