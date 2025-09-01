from manim import *
import numpy as np

config.background_color = WHITE

def calculate_intersection(p1, p2, p3, p4):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    x3, y3 = p3[0], p3[1]
    x4, y4 = p4[0], p4[1]
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denominator) < 1e-10:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)
    return np.array([x, y, 0])

def normalize_angle(a):
    while a <= -np.pi:
        a += 2*np.pi
    while a > np.pi:
        a -= 2*np.pi
    return a

def make_internal_angle_with_ticks(line_a: Line, line_b: Line, radius: float, color) -> VGroup:
    """Draw the smaller internal angle (< pi) between two lines with fill and ticks,
    regardless of the order of lines provided.
    """
    # First create a candidate angle with default orientation
    candidate = Angle(line_a, line_b, radius=radius, color=color, stroke_width=4)
    # If candidate is reflex (> pi), switch to the other angle
    try:
        val = candidate.get_value()
    except Exception:
        # Fallback: approximate using directions from the vertex
        v = calculate_intersection(line_a.get_start(), line_a.get_end(), line_b.get_start(), line_b.get_end())
        if v is None:
            val = np.pi/2
        else:
            def dir_from_vertex(line: Line):
                p1 = line.get_start(); p2 = line.get_end()
                v1 = p1 - v; v2 = p2 - v
                vec = v2 if np.linalg.norm(v2) > np.linalg.norm(v1) else v1
                return np.arctan2(vec[1], vec[0])
            th1 = dir_from_vertex(line_a)
            th2 = dir_from_vertex(line_b)
            val = abs(normalize_angle(th2 - th1))
            if val > np.pi:
                val = 2*np.pi - val
    if val > np.pi - 1e-6:
        angle = Angle(line_a, line_b, radius=radius, color=color, stroke_width=4, other_angle=True)
    else:
        angle = candidate
    if hasattr(angle, 'set_fill'):
        angle.set_fill(color, opacity=0.25)
    # Build tick arcs centered at the vertex along the minor arc
    v = calculate_intersection(line_a.get_start(), line_a.get_end(), line_b.get_start(), line_b.get_end())
    if v is None:
        return VGroup(angle)
    def dir_from_vertex(line: Line):
        p1 = line.get_start(); p2 = line.get_end()
        v1 = p1 - v; v2 = p2 - v
        vec = v2 if np.linalg.norm(v2) > np.linalg.norm(v1) else v1
        return np.arctan2(vec[1], vec[0])
    th1 = dir_from_vertex(line_a)
    th2 = dir_from_vertex(line_b)
    signed_delta = normalize_angle(th2 - th1)
    if abs(signed_delta) > np.pi:
        signed_delta = -np.sign(signed_delta) * (2*np.pi - abs(signed_delta))
    mid = th1 + signed_delta/2
    arc_len = min(abs(signed_delta)*0.35, 0.5)
    r1 = radius*0.72
    r2 = radius*0.85
    tick1 = Arc(radius=r1, start_angle=mid-arc_len/2, angle=arc_len, arc_center=v, color=color, stroke_width=3)
    tick2 = Arc(radius=r2, start_angle=mid-arc_len/2, angle=arc_len, arc_center=v, color=color, stroke_width=3)
    return VGroup(angle, tick1, tick2)

class Image1Scene(Scene):
    def construct(self):
        circle = Circle(radius=2, color=BLACK, stroke_width=2)
        center = Dot(ORIGIN, color=BLACK, radius=0.05)
        center_label = Text("O", color=BLACK).next_to(center, UP+LEFT, buff=0.2)
        radius_x = Line(ORIGIN, 3*DOWN+LEFT, color=BLACK, stroke_width=2)
        radius_y = Line(ORIGIN, 3*DOWN+RIGHT, color=BLACK, stroke_width=2)
        point_M = Dot(2*DOWN+LEFT, color=BLUE, radius=0.08)
        point_N = Dot(2*DOWN+RIGHT, color=BLUE, radius=0.08)
        M_label = Text("M", color=BLACK).next_to(point_M, DOWN+LEFT, buff=0.3)
        N_label = Text("N", color=BLACK).next_to(point_N, DOWN+RIGHT, buff=0.3)
        x_label = Text("x", color=BLACK).next_to(radius_x.get_end(), DOWN+LEFT, buff=0.4)
        y_label = Text("y", color=BLACK).next_to(radius_y.get_end(), DOWN+RIGHT, buff=0.4)
        arc = ArcBetweenPoints(point_M.get_center(), point_N.get_center(), color=RED, stroke_width=4)
        zeta_label = Text("(ζ)", color=BLACK).to_corner(UP+LEFT)
        self.add(circle, center, center_label, radius_x, radius_y, point_M, point_N, 
                M_label, N_label, x_label, y_label, arc, zeta_label)

class Image2Scene(Scene):
    def construct(self):
        line_x = Line(3*LEFT+UP, 3*RIGHT+UP, color=BLACK, stroke_width=2)
        line_y = Line(3*LEFT+DOWN, 3*RIGHT+DOWN, color=BLACK, stroke_width=2)
        transversal = Line(2*LEFT+1.5*UP, 2*RIGHT+1.5*DOWN, color=BLACK, stroke_width=2)
        pA = calculate_intersection(line_x.get_start(), line_x.get_end(), transversal.get_start(), transversal.get_end())
        pB = calculate_intersection(line_y.get_start(), line_y.get_end(), transversal.get_start(), transversal.get_end())
        point_A = Dot(pA, color=BLACK, radius=0.05)
        point_B = Dot(pB, color=BLACK, radius=0.05)
        x_label = Text("x", color=BLACK).next_to(line_x.get_end(), RIGHT, buff=0.3)
        y_label = Text("y", color=BLACK).next_to(line_y.get_start(), LEFT, buff=0.3)
        A_label = Text("A", color=BLACK).next_to(point_A, UP, buff=0.3)
        B_label = Text("B", color=BLACK).next_to(point_B, DOWN, buff=0.3)
        angle_A = make_internal_angle_with_ticks(line_x, transversal, radius=0.4, color=PINK)
        angle_B = make_internal_angle_with_ticks(transversal, line_y, radius=0.4, color=PINK)
        parallel_text = MathTex(r"(Ax)//(By)", color=RED).to_corner(UP+LEFT)
        angle_text = MathTex(r"\widehat{BAx} = \widehat{ABy}", color=RED).move_to(2*RIGHT+0.5*UP)
        self.add(line_x, line_y, transversal, point_A, point_B, x_label, y_label, A_label, B_label,
                 angle_A, angle_B, parallel_text, angle_text)

class Image3Scene(Scene):
    def construct(self):
        line_x = Line(3*LEFT+UP, 3*RIGHT+UP, color=BLACK, stroke_width=2)
        line_y = Line(3*LEFT+DOWN, 3*RIGHT+DOWN, color=BLACK, stroke_width=2)
        transversal = Line(2*LEFT+1.5*UP, 2*RIGHT+1.5*DOWN, color=BLACK, stroke_width=2)
        pA = calculate_intersection(line_x.get_start(), line_x.get_end(), transversal.get_start(), transversal.get_end())
        pB = calculate_intersection(line_y.get_start(), line_y.get_end(), transversal.get_start(), transversal.get_end())
        point_A = Dot(pA, color=BLACK, radius=0.05)
        point_B = Dot(pB, color=BLACK, radius=0.05)
        x_label = Text("x", color=BLACK).next_to(line_x.get_start(), LEFT, buff=0.3)
        y_label = Text("y", color=BLACK).next_to(line_y.get_start(), LEFT, buff=0.3)
        z_label = Text("z", color=BLACK).next_to(transversal.get_start(), UP+LEFT, buff=0.3)
        A_label = Text("A", color=BLACK).next_to(point_A, UP+LEFT, buff=0.3)
        B_label = Text("B", color=BLACK).next_to(point_B, DOWN+LEFT, buff=0.3)
        angle_A = make_internal_angle_with_ticks(transversal, line_x, radius=0.5, color=BLUE)
        angle_B = make_internal_angle_with_ticks(transversal, line_y, radius=0.5, color=BLUE)
        parallel_text = MathTex(r"(Ax)//(By)", color=RED).to_corner(UP+LEFT)
        angle_text = MathTex(r"\widehat{zAx} = \widehat{zBy}", color=RED).move_to(2*RIGHT+0.5*UP)
        self.add(line_x, line_y, transversal, point_A, point_B, x_label, y_label, z_label, A_label, B_label,
                 angle_A, angle_B, parallel_text, angle_text)

class Image4Scene(Scene):
    def construct(self):
        line_x = Line(3*LEFT+UP, 3*RIGHT+UP, color=BLACK, stroke_width=2)
        line_y = Line(3*LEFT+DOWN, 3*RIGHT+DOWN, color=BLACK, stroke_width=2)
        transversal = Line(2*LEFT+1.5*UP, 2*RIGHT+1.5*DOWN, color=BLACK, stroke_width=2)
        pA = calculate_intersection(line_x.get_start(), line_x.get_end(), transversal.get_start(), transversal.get_end())
        pB = calculate_intersection(line_y.get_start(), line_y.get_end(), transversal.get_start(), transversal.get_end())
        point_A = Dot(pA, color=BLACK, radius=0.05)
        point_B = Dot(pB, color=BLACK, radius=0.05)
        x_label = Text("x", color=BLACK).next_to(line_x.get_start(), LEFT, buff=0.3)
        y_label = Text("y", color=BLACK).next_to(line_y.get_start(), LEFT, buff=0.3)
        A_label = Text("A", color=BLACK).next_to(point_A, UP+LEFT, buff=0.3)
        B_label = Text("B", color=BLACK).next_to(point_B, DOWN+LEFT, buff=0.3)
        angle_A = make_internal_angle_with_ticks(line_x, transversal, radius=0.4, color=GREEN)
        angle_B = make_internal_angle_with_ticks(transversal, line_y, radius=0.4, color=GREEN)
        parallel_text = MathTex(r"(Ax)//(By)", color=RED).to_corner(UP+LEFT)
        angle_text = MathTex(r"\widehat{BAx} + \widehat{ABy} = 180°", color=RED).move_to(2*RIGHT+0.5*UP)
        self.add(line_x, line_y, transversal, point_A, point_B, x_label, y_label, A_label, B_label,
                 angle_A, angle_B, parallel_text, angle_text)

class Image5Scene(Scene):
    def construct(self):
        line_x = Line(3*LEFT+UP, 3*RIGHT+UP, color=BLACK, stroke_width=2)
        line_y = Line(3*LEFT+DOWN, 3*RIGHT+DOWN, color=BLACK, stroke_width=2)
        transversal = Line(2*LEFT+1.5*UP, 2*RIGHT+1.5*DOWN, color=BLACK, stroke_width=2)
        pA = calculate_intersection(line_x.get_start(), line_x.get_end(), transversal.get_start(), transversal.get_end())
        pB = calculate_intersection(line_y.get_start(), line_y.get_end(), transversal.get_start(), transversal.get_end())
        point_A = Dot(pA, color=BLACK, radius=0.05)
        point_B = Dot(pB, color=BLACK, radius=0.05)
        x_label = Text("x", color=BLACK).next_to(line_x.get_end(), RIGHT, buff=0.3)
        y_label = Text("y", color=BLACK).next_to(line_y.get_start(), LEFT, buff=0.3)
        A_label = Text("A", color=BLACK).next_to(point_A, UP+RIGHT, buff=0.3)
        B_label = Text("B", color=BLACK).next_to(point_B, DOWN+LEFT, buff=0.3)
        angle_A = make_internal_angle_with_ticks(transversal, line_x, radius=0.4, color=PINK)
        angle_B = make_internal_angle_with_ticks(line_y, transversal, radius=0.4, color=PINK)
        french_text = MathTex(r"\text{Si } \widehat{BAx} = \widehat{ABy} \text{ alors } (Ax)//(By)", color=RED).to_edge(UP)
        self.add(line_x, line_y, transversal, point_A, point_B, x_label, y_label, A_label, B_label,
                 angle_A, angle_B, french_text)

class Image6Scene(Scene):
    def construct(self):
        line_x = Line(3*LEFT+UP, 3*RIGHT+UP, color=BLACK, stroke_width=2)
        line_y = Line(3*LEFT+DOWN, 3*RIGHT+DOWN, color=BLACK, stroke_width=2)
        transversal = Line(2*LEFT+1.5*UP, 2*RIGHT+1.5*DOWN, color=BLACK, stroke_width=2)
        pA = calculate_intersection(line_x.get_start(), line_x.get_end(), transversal.get_start(), transversal.get_end())
        pB = calculate_intersection(line_y.get_start(), line_y.get_end(), transversal.get_start(), transversal.get_end())
        point_A = Dot(pA, color=BLACK, radius=0.05)
        point_B = Dot(pB, color=BLACK, radius=0.05)
        x_label = Text("x", color=BLACK).next_to(line_x.get_start(), LEFT, buff=0.3)
        y_label = Text("y", color=BLACK).next_to(line_y.get_start(), LEFT, buff=0.3)
        z_label = Text("z", color=BLACK).next_to(transversal.get_start(), UP+LEFT, buff=0.3)
        A_label = Text("A", color=BLACK).next_to(point_A, UP+LEFT, buff=0.3)
        B_label = Text("B", color=BLACK).next_to(point_B, DOWN+LEFT, buff=0.3)
        angle_A = make_internal_angle_with_ticks(transversal, line_x, radius=0.5, color=BLUE)
        angle_B = make_internal_angle_with_ticks(transversal, line_y, radius=0.5, color=BLUE)
        parallel_text = MathTex(r"(Ax)//(By)", color=RED).to_corner(UP+LEFT)
        angle_text = MathTex(r"\widehat{zAx} = \widehat{zBy}", color=RED).move_to(2*RIGHT+0.5*UP)
        self.add(line_x, line_y, transversal, point_A, point_B, x_label, y_label, z_label, A_label, B_label,
                 angle_A, angle_B, parallel_text, angle_text)

class Image7Scene(Scene):
    def construct(self):
        line_x = Line(3*LEFT+UP, 3*RIGHT+UP, color=BLACK, stroke_width=2)
        line_y = Line(3*LEFT+DOWN, 3*RIGHT+DOWN, color=BLACK, stroke_width=2)
        transversal = Line(2*LEFT+1.5*UP, 2*RIGHT+1.5*DOWN, color=BLACK, stroke_width=2)
        pA = calculate_intersection(line_x.get_start(), line_x.get_end(), transversal.get_start(), transversal.get_end())
        pB = calculate_intersection(line_y.get_start(), line_y.get_end(), transversal.get_start(), transversal.get_end())
        point_A = Dot(pA, color=BLACK, radius=0.05)
        point_B = Dot(pB, color=BLACK, radius=0.05)
        x_label = Text("x", color=BLACK).next_to(line_x.get_start(), LEFT, buff=0.3)
        y_label = Text("y", color=BLACK).next_to(line_y.get_start(), LEFT, buff=0.3)
        A_label = Text("A", color=BLACK).next_to(point_A, UP+LEFT, buff=0.3)
        B_label = Text("B", color=BLACK).next_to(point_B, DOWN+LEFT, buff=0.3)
        angle_A = make_internal_angle_with_ticks(line_x, transversal, radius=0.4, color=GREEN)
        angle_B = make_internal_angle_with_ticks(transversal, line_y, radius=0.4, color=GREEN)
        parallel_text = MathTex(r"(Ax)//(By)", color=RED).to_corner(UP+LEFT)
        angle_text = MathTex(r"\widehat{BAx} + \widehat{ABy} = 180°", color=RED).move_to(2*RIGHT+0.5*UP)
        self.add(line_x, line_y, transversal, point_A, point_B, x_label, y_label, A_label, B_label,
                 angle_A, angle_B, parallel_text, angle_text)

class Image8Scene(Scene):
    def construct(self):
        circle = Circle(radius=2, color=BLACK, stroke_width=2)
        zeta_label = Text("(ζ)", color=BLACK).next_to(circle, UP+RIGHT, buff=0.3)
        line_x = Line(2*UP, 2*DOWN, color=BLACK, stroke_width=2).shift(1.5*LEFT)
        x_label = Text("x", color=BLACK).next_to(line_x.get_end(), DOWN, buff=0.3)
        line_y = Line(2*UP, 2*DOWN+RIGHT, color=BLACK, stroke_width=2).shift(0.5*RIGHT)
        y_label = Text("y", color=BLACK).next_to(line_y.get_end(), DOWN+RIGHT, buff=0.3)
        point_A = Dot(2*UP, color=BLUE, radius=0.08).shift(1.5*LEFT)
        point_B = Dot(2*DOWN, color=BLUE, radius=0.08).shift(1.5*LEFT)
        point_C = Dot(1.5*RIGHT+0.5*DOWN, color=BLUE, radius=0.08)
        A_label = Text("A", color=BLACK).next_to(point_A, UP+LEFT, buff=0.3)
        B_label = Text("B", color=BLACK).next_to(point_B, DOWN+LEFT, buff=0.3)
        C_label = Text("C", color=BLACK).next_to(point_C, RIGHT, buff=0.3)
        center_x = Text("x", color=BLACK).move_to(ORIGIN)
        angle_A = make_internal_angle_with_ticks(line_x, line_y, radius=0.6, color=GRAY)
        self.add(circle, zeta_label, line_x, line_y, x_label, y_label, 
                 point_A, point_B, point_C, A_label, B_label, C_label, center_x, angle_A)
