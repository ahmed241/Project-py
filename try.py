from manim import *
from MF_Tools import TransformByGlyphMap
from manim_narration import NarrationScene
from manim_narration.speech import KokoroService

class HungarianShowcase(NarrationScene):
	def construct(self):
		self.set_speech_services(
	en=KokoroService(voice="af_heart", lang_code="en-us")
)
		expA = MathTex("\\left( \\cos(x) + i\\sin(x) \\right)^3")
		expB = MathTex("\\cos(3x) + i\\sin(3x)")
		self.add(expA)
		with self.narration(speech_service_id="en", text = "tada!") as narration:
			self.play(TransformByGlyphMap(expA,expB,
				([16], [4]),
				([16], [13]),
				([0,15], [])
			))