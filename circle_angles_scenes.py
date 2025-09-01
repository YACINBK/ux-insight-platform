from manim import *
import numpy as np
import math

# Helpers

def filled_minor_angle(point: np.ndarray, u: np.ndarray, v: np.ndarray, radius: float, color) -> VGroup:
    a1 = math.atan2(u[1], u[0]); a2 = math.atan2(v[1], v[0])
    delta = (a2 - a1) % (2*math.pi)
    if delta <= math.pi:
        start, sweep = a1, delta
    else:
        start, sweep = a2, 2*math.pi - delta
    sector = Sector(arc_center=point, radius=radius, start_angle=start, angle=sweep,
                    color=color, fill_opacity=0.35, stroke_opacity=0)
    outline = Arc(arc_center=point, radius=radius, start_angle=start, angle=sweep,
                  color=color, stroke_width=6)
    return VGroup(sector, outline)

class InscribedAngleScene(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        # Circle
        R = 2.8
        circle = Circle(radius=R, color=GRAY_E, stroke_width=6).shift(UP*0.6)
        O = circle.get_center()
        # Points M and N on lower arc
        angM = math.radians(210)
        angN = math.radians(330)
        M = O + R*np.array([math.cos(angM), math.sin(angM), 0])
        N = O + R*np.array([math.cos(angN), math.sin(angN), 0])
        # Lines OM and ON start at O and extend outward (do not cross behind O)
        vM = (M - O); vM = vM / np.linalg.norm(vM)
        vN = (N - O); vN = vN / np.linalg.norm(vN)
        Lx = Line(O, O + (R+1.2)*vM, color=GRAY_E, stroke_width=5)
        Ly = Line(O, O + (R+1.2)*vN, color=GRAY_E, stroke_width=5)
        # Minor arc MN in red
        arcMN = Arc(arc_center=O, radius=R, start_angle=angM, angle=(angN-angM)%(2*math.pi), color=RED_D, stroke_width=6)
        # Angle at O between OM and ON (thin gray fill)
        angleO = filled_minor_angle(O, vM, vN, radius=0.7, color=GRAY_B)
        # Assemble
        self.add(circle, Lx, Ly, arcMN, angleO)
        self.add(Dot(O, color=GRAY_E), Dot(M, color=BLUE_D), Dot(N, color=BLUE_D))
        self.add(Text("O", font_size=30, color=BLACK).next_to(O, UP*0.6))
        # Apply spacing like for B/C: more outward (normal) and along/against radial for horizontal breathing room; no rotation
        nM = np.array([-vM[1], vM[0], 0.0])
        nN = np.array([-vN[1], vN[0], 0.0])
        self.add(Text("M", font_size=30, color=BLACK).move_to(M + 0.6*nM - 0.3*vM))
        self.add(Text("N", font_size=30, color=BLACK).move_to(N + 0.6*nN + 0.3*vN))
        # Labels x,y at outer ends
        self.add(Text("x", font_size=28, color=BLACK).move_to(Lx.get_end() + 0.25*vM))
        self.add(Text("y", font_size=28, color=BLACK).move_to(Ly.get_end() + 0.25*vN))
        # Circle name (ζ) reverted to lower-left for visibility
        zeta = MathTex(r"(\zeta)", color=BLACK).next_to(circle, DOWN+LEFT, buff=0.4)
        self.add(zeta)
        self.wait(0.1)

class CentralAngleWithTangentScene(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        R = 2.8
        circle = Circle(radius=R, color=GRAY_E, stroke_width=6).shift(RIGHT*0.4)
        Ccenter = circle.get_center()
        # Choose points A (top-left-ish), B (bottom-left-ish), C (right-lower on circle)
        angA = math.radians(110)
        angB = math.radians(250)
        angC = math.radians(340)
        A = Ccenter + R*np.array([math.cos(angA), math.sin(angA), 0])
        B = Ccenter + R*np.array([math.cos(angB), math.sin(angB), 0])
        C = Ccenter + R*np.array([math.cos(angC), math.sin(angC), 0])
        # Line x: starts at A, goes through B and beyond (balanced length)
        dir_x = (B - A); dir_x = dir_x/np.linalg.norm(dir_x)
        line_x = Line(A, A + 5.5*dir_x, color=GRAY_E, stroke_width=5)
        # Line y: starts at A, goes through C and beyond (match x length feel)
        dir_y = (C - A); dir_y = dir_y/np.linalg.norm(dir_y)
        line_y = Line(A, A + 5.5*dir_y, color=GRAY_E, stroke_width=5)
        # Angle at A between AB and AC
        angleA = filled_minor_angle(A, dir_x, dir_y, radius=0.55, color=GRAY_B)
        # Assemble
        self.add(circle, line_x, line_y)
        self.add(Dot(A, color=BLUE_D), Dot(B, color=BLUE_D), Dot(C, color=BLUE_D))
        # Labels without rotation, with spacing
        self.add(Text("A", font_size=30, color=BLACK).next_to(A, UL, buff=0.3))
        n_x = np.array([-dir_x[1], dir_x[0], 0.0])
        n_y = np.array([-dir_y[1], dir_y[0], 0.0])
        self.add(Text("B", font_size=30, color=BLACK).move_to(B + 0.5*n_x - 0.25*dir_x))
        self.add(Text("C", font_size=30, color=BLACK).move_to(C + 0.5*n_y + 0.25*dir_y))
        # Endpoint labels x, y
        self.add(Text("x", font_size=28, color=BLACK).move_to(line_x.get_end() + 0.25*dir_x))
        self.add(Text("y", font_size=28, color=BLACK).move_to(line_y.get_end() + 0.25*dir_y))
        self.add(angleA)
        zeta = MathTex(r"(\zeta)", color=BLACK).next_to(circle, UP+LEFT, buff=0.2)
        self.add(zeta)
        self.wait(0.1)
