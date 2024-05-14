from .steve_brule import SteveBrulePrompt
from .steve_brule_quiz import SteveBruleQuizPrompt

def prompt(mode, character):
  if character == "steve_brule":
    if mode == "tutor":
      return SteveBrulePrompt().prompt
    elif mode == "quiz":
      return SteveBruleQuizPrompt().prompt



