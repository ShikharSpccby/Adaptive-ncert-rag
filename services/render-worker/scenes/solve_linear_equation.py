"""
Concept: solving a linear equation in one variable (2x + 3 = 7).
This scene is hand-written to prove the render pipeline works end to end.
In the real system, this file's content is what the Coding LLM agent produces --
this is here to validate the render/verify wiring before that agent exists.
"""

from manim import DOWN, UP, FadeIn, FadeOut, ReplacementTransform, Text, Write

from base_scene import ACCENT_COLOR, CORRECT_COLOR, TEXT_COLOR, BaseLessonScene


class SolveLinearEquation(BaseLessonScene):
    """
    Each step TRANSFORMS the equation in place rather than stacking a new line
    of text below the last one. This fixes a real layout bug found by actually
    watching the first render: stacking six elements vertically pushed the
    final answer below the visible frame -- a bug that survived until someone
    checked the output, which is exactly why render QA is a required pipeline
    step, not an optional one.
    """

    def construct(self):
        self.show_title("Solving a Linear Equation")

        equation = Text("2x + 3 = 7", color=TEXT_COLOR, font_size=56)
        self.play(Write(equation))
        self.wait(1)

        step1_label = Text("Subtract 3 from both sides", color=ACCENT_COLOR, font_size=28)
        step1_label.next_to(equation, UP, buff=0.6)
        self.play(FadeIn(step1_label))

        next_equation = Text("2x = 4", color=TEXT_COLOR, font_size=56)
        next_equation.move_to(equation)
        self.play(ReplacementTransform(equation, next_equation))
        equation = next_equation
        self.wait(1)
        self.play(FadeOut(step1_label))

        step2_label = Text("Divide both sides by 2", color=ACCENT_COLOR, font_size=28)
        step2_label.next_to(equation, UP, buff=0.6)
        self.play(FadeIn(step2_label))

        final_equation = Text("x = 2", color=CORRECT_COLOR, font_size=64)
        final_equation.move_to(equation)
        self.play(ReplacementTransform(equation, final_equation))
        self.wait(2)
