"""
Concept: solving a linear equation in one variable (2x + 3 = 7).
This scene is hand-written to prove the render pipeline works end to end.
In the real system, this file's content is what the Coding LLM agent produces --
this is here to validate the render/verify wiring before that agent exists.
"""

from manim import DOWN, FadeIn, Text, Write

from base_scene import ACCENT_COLOR, CORRECT_COLOR, TEXT_COLOR, BaseLessonScene


class SolveLinearEquation(BaseLessonScene):
    def construct(self):
        self.show_title("Solving a Linear Equation")

        eq0 = Text("2x + 3 = 7", color=TEXT_COLOR, font_size=48)
        self.play(Write(eq0))
        self.wait(1)

        step1_label = Text("Subtract 3 from both sides", color=ACCENT_COLOR, font_size=28)
        step1_label.next_to(eq0, DOWN, buff=1.0)
        eq1 = Text("2x = 4", color=TEXT_COLOR, font_size=48)
        eq1.next_to(step1_label, DOWN, buff=0.5)

        self.play(FadeIn(step1_label))
        self.play(Write(eq1))
        self.wait(1)

        step2_label = Text("Divide both sides by 2", color=ACCENT_COLOR, font_size=28)
        step2_label.next_to(eq1, DOWN, buff=1.0)
        eq2 = Text("x = 2", color=CORRECT_COLOR, font_size=56)
        eq2.next_to(step2_label, DOWN, buff=0.5)

        self.play(FadeIn(step2_label))
        self.play(Write(eq2))
        self.wait(2)
