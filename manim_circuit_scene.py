from manim import *
import numpy as np

class EnhancedCircuitScene(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = "#cbe2fa"

        # --- Centering offset ---
        x_offset = 1.5  # shift right to center the circuit

        # --- Positions (centered grid layout for strict 90° angles) ---
        battery_pos = LEFT * 3.5 + DOWN * 2
        copper_rod_x = 0
        copper_rod_y = 2
        lamp_x = 4
        lamp_y = 2
        magnet_x = 6.5
        magnet_y = 2
        motor_x = 9
        motor_y = 2
        led_x = 9
        led_y = -2
        electrolyser_x = 4
        electrolyser_y = -2

        # Apply centering offset
        def cx(x): return x + x_offset

        # --- Battery ---
        battery = Rectangle(width=0.6, height=1, color=BLUE, fill_opacity=0.7).move_to([cx(battery_pos[0]), battery_pos[1], 0])
        battery_label = Text("Batterie", font_size=24, color=BLUE).next_to(battery, DOWN)
        battery_plus = Text("+", font_size=24, color=RED).next_to(battery, UP, buff=0.1).shift(LEFT*0.15)
        battery_minus = Text("-", font_size=24, color=BLACK).next_to(battery, UP, buff=0.1).shift(RIGHT*0.15)

        # --- Lamp (bulb, yellow glass) ---
        bulb_base = Rectangle(width=0.4, height=0.25, color=BLACK, fill_opacity=1).move_to([cx(lamp_x), lamp_y-0.4, 0])
        bulb_glass = Circle(radius=0.6, color=YELLOW, fill_opacity=0.7).move_to([cx(lamp_x), lamp_y+0.45, 0])
        filament = VGroup(
            Line([cx(lamp_x-0.1), lamp_y+0.05, 0], [cx(lamp_x), lamp_y+0.25, 0], color=BLACK, stroke_width=2),
            Line([cx(lamp_x+0.1), lamp_y+0.05, 0], [cx(lamp_x), lamp_y+0.25, 0], color=BLACK, stroke_width=2),
            Line([cx(lamp_x), lamp_y+0.25, 0], [cx(lamp_x), lamp_y+0.45, 0], color=BLACK, stroke_width=2)
        )
        bulb_label = Text("Lampe", font_size=24, color=BLACK).next_to(bulb_glass, UP)
        bulb_glow = Circle(radius=0.7, color=YELLOW, fill_opacity=0.4).move_to(bulb_glass.get_center())

        # --- Copper rod (Tige de cuivre) as a segment in the cable ---
        copper_rod_start = [battery.get_right()[0] + 0.5, battery.get_right()[1], 0]
        copper_rod_end = [cx(copper_rod_x-0.3), copper_rod_y, 0]
        copper_rod = Line(copper_rod_start, copper_rod_end, color=YELLOW, stroke_width=12)
        copper_rod_label = Text("Tige en cuivre", font_size=18, color=YELLOW).next_to(copper_rod, UP)

        # --- Magnet (Aiguille aimantée) ---
        magnet_pos = [cx(magnet_x), magnet_y, 0]
        compass_base = Circle(radius=0.25, color=BLUE, fill_opacity=0.2).move_to(magnet_pos)
        magnet = Arrow(start=[cx(magnet_x), magnet_y-0.15, 0], end=[cx(magnet_x), magnet_y+0.35, 0], color=RED, buff=0, stroke_width=10)
        magnet_label = Text("Aiguille aimantée", font_size=20, color=RED).next_to(compass_base, UP)

        # --- Motor (gear) ---
        box = RoundedRectangle(width=1.5, height=1, corner_radius=0.2, color=BLUE, fill_opacity=0.3).move_to([cx(motor_x), motor_y, 0])
        gear = Annulus(inner_radius=0.18, outer_radius=0.28, color=YELLOW, fill_opacity=1).move_to(box.get_center())
        gear_teeth = VGroup(
            *[Line(gear.get_center(), gear.get_center() + 0.32*RIGHT, color=YELLOW, stroke_width=5).rotate(angle, about_point=gear.get_center())
              for angle in np.linspace(0, 2*PI, 8, endpoint=False)]
        )
        gear_group = VGroup(gear, gear_teeth)
        motor_label = Text("Moteur", font_size=24, color=BLUE).next_to(box, UP)

        # --- LED (green) ---
        led_body = Triangle().scale(0.25).set_fill(GREEN, opacity=1).set_stroke(BLACK, width=2).move_to([cx(led_x), led_y, 0])
        led_line = Line(led_body.get_bottom(), led_body.get_bottom() + DOWN*0.3, color=BLACK, stroke_width=3)
        led_glow = Triangle().scale(0.32).set_fill(GREEN, opacity=0.4).move_to(led_body)
        led_label = Text("LED", font_size=24, color=GREEN).next_to(led_body, DOWN)

        # --- Electrolyser (realistic) ---
        beaker = RoundedRectangle(width=1.2, height=1.2, corner_radius=0.3, color=BLUE, fill_opacity=0.1).move_to([cx(electrolyser_x), electrolyser_y, 0])
        solution = Rectangle(width=1.1, height=0.5, color=BLUE, fill_opacity=0.3).move_to(beaker.get_center() + DOWN*0.2)
        electrode_left = Line(beaker.get_top() + LEFT*0.3, beaker.get_bottom() + LEFT*0.3, color=GRAY, stroke_width=8)
        electrode_right = Line(beaker.get_top() + RIGHT*0.3, beaker.get_bottom() + RIGHT*0.3, color=GRAY, stroke_width=8)
        bubbles = VGroup(*[Dot(beaker.get_bottom() + LEFT*0.3 + UP*0.2*i, radius=0.04, color=BLUE) for i in range(1, 5)])
        beaker_label = Text("Électrolyseur", font_size=24, color=BLUE).next_to(beaker, DOWN)

        # --- Cables (all 90° angles, only horizontal/vertical segments) ---
        # Battery to copper rod (horizontal)
        cable_batt_to_rod = Line(battery.get_right(), copper_rod_start, color=RED, stroke_width=8)
        # Copper rod segment (yellow, already defined)
        # Copper rod to lamp (horizontal, then vertical)
        rod_to_lamp_h = Line([cx(copper_rod_x-0.3), copper_rod_y, 0], [cx(lamp_x-1.2), copper_rod_y, 0], color=RED, stroke_width=8)
        rod_to_lamp_v = Line([cx(lamp_x-1.2), copper_rod_y, 0], [cx(lamp_x-1.2), lamp_y-0.7, 0], color=RED, stroke_width=8)
        rod_to_lamp_h2 = Line([cx(lamp_x-1.2), lamp_y-0.7, 0], bulb_base.get_left(), color=RED, stroke_width=8)
        # Lamp to magnet (horizontal)
        cable_lamp_to_magnet = Line(bulb_base.get_right(), [cx(magnet_x-0.25), magnet_y, 0], color=RED, stroke_width=8)
        # Magnet to motor (horizontal)
        cable_magnet_to_motor = Line([cx(magnet_x+0.25), magnet_y, 0], box.get_left(), color=RED, stroke_width=8)
        # Motor to LED (vertical down)
        cable_motor_to_led_v = Line(box.get_bottom(), [cx(motor_x), led_y+0.5, 0], color=RED, stroke_width=8)
        cable_motor_to_led_h = Line([cx(motor_x), led_y+0.5, 0], [cx(led_x), led_y+0.5, 0], color=RED, stroke_width=8)
        cable_motor_to_led_v2 = Line([cx(led_x), led_y+0.5, 0], led_body.get_top(), color=RED, stroke_width=8)
        # LED to electrolyser (horizontal)
        cable_led_to_electrolyser = Line(led_body.get_left(), [cx(electrolyser_x+0.6), led_y, 0], color=RED, stroke_width=8)
        cable_led_to_electrolyser_v = Line([cx(electrolyser_x+0.6), led_y, 0], [cx(electrolyser_x+0.6), electrolyser_y-0.6, 0], color=RED, stroke_width=8)
        cable_led_to_electrolyser_h2 = Line([cx(electrolyser_x+0.6), electrolyser_y-0.6, 0], beaker.get_right(), color=RED, stroke_width=8)
        # Electrolyser to battery (horizontal)
        cable_electrolyser_to_batt = Line(beaker.get_left(), [battery.get_left()[0], electrolyser_y, 0], color=RED, stroke_width=8)
        cable_electrolyser_to_batt_v = Line([battery.get_left()[0], electrolyser_y, 0], battery.get_left(), color=RED, stroke_width=8)

        # --- Current flow (moving dot) ---
        current_path = VMobject()
        current_path.set_points_as_corners([
            battery.get_right(),
            copper_rod_start,
            copper_rod_end,
            [cx(lamp_x-1.2), copper_rod_y, 0],
            [cx(lamp_x-1.2), lamp_y-0.7, 0],
            bulb_base.get_left(),
            bulb_base.get_right(),
            [cx(magnet_x-0.25), magnet_y, 0],
            [cx(magnet_x+0.25), magnet_y, 0],
            box.get_left(),
            box.get_bottom(),
            [cx(motor_x), led_y+0.5, 0],
            [cx(led_x), led_y+0.5, 0],
            led_body.get_top(),
            led_body.get_left(),
            [cx(electrolyser_x+0.6), led_y, 0],
            [cx(electrolyser_x+0.6), electrolyser_y-0.6, 0],
            beaker.get_right(),
            beaker.get_left(),
            [battery.get_left()[0], electrolyser_y, 0],
            battery.get_left()
        ])
        dot = Dot(color=RED).move_to(current_path.get_start())

        # --- Add all elements ---
        self.add(battery, battery_label, battery_plus, battery_minus)
        self.add(beaker, solution, electrode_left, electrode_right, bubbles, beaker_label)
        self.add(copper_rod, copper_rod_label)
        self.add(compass_base, magnet, magnet_label)
        self.add(led_body, led_line, led_label)
        self.add(bulb_base, bulb_glass, filament, bulb_label)
        self.add(box, gear_group, motor_label)
        self.add(
            cable_batt_to_rod,
            copper_rod,
            rod_to_lamp_h, rod_to_lamp_v, rod_to_lamp_h2,
            cable_lamp_to_magnet, cable_magnet_to_motor,
            cable_motor_to_led_v, cable_motor_to_led_h, cable_motor_to_led_v2,
            cable_led_to_electrolyser, cable_led_to_electrolyser_v, cable_led_to_electrolyser_h2,
            cable_electrolyser_to_batt, cable_electrolyser_to_batt_v
        )
        self.add(dot)

        # --- Animations ---
        self.play(FadeIn(bulb_glow), FadeIn(led_glow), run_time=0.5)
        bubble_anims = [bubble.animate.shift(UP*0.3).set_opacity(0) for bubble in bubbles]
        current_anim = MoveAlongPath(dot, current_path, rate_func=linear, run_time=4)
        gear_rotation = Rotate(gear_group, angle=2*PI, about_point=gear.get_center(), run_time=4)
        self.play(AnimationGroup(
            *bubble_anims,
            current_anim,
            gear_rotation,
            lag_ratio=0.1
        ))
        self.wait(1)
