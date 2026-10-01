"""
BaseLessonScene: every generated Manim scene should subclass this, not manim.Scene
directly. This is what keeps hundreds of LLM-generated scenes visually consistent
(same palette, same title placement) instead of each looking like a different app.

NOTE on LaTeX: this uses manim's `Text` (Pango-based) rather than `MathTex`/`Tex`,
because MathTex requires a full LaTeX distribution installed on the render machine.
Text is enough for algebra-level expressions written in plain characters (as in this
demo). If/when you need proper typeset math notation (stacked fractions, integral
signs, etc.), install a LaTeX distribution (e.g. `texlive`) on the render worker and
switch the relevant Mobjects to MathTex -- that's a render-environment change, not a
change to this base class.
"""

from manim import BLACK, UP, WHITE, Scene, Text, Write

# House palette -- change these once, and every scene that inherits
# BaseLessonScene picks up the new look.
BACKGROUND_COLOR = WHITE
TEXT_COLOR = BLACK
ACCENT_COLOR = "#3B82F6"   # step highlights
CORRECT_COLOR = "#22C55E"  # verified-correct confirmations


class BaseLessonScene(Scene):
    def setup(self):
        self.camera.background_color = BACKGROUND_COLOR

    def show_title(self, title_text: str):
        title = Text(title_text, color=TEXT_COLOR, font_size=40)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        return title
