from .steve_brule import SteveBrulePrompt
from .steve_brule_quiz import SteveBruleQuizPrompt

def prompt(character):
  if character == "steve_brule":
    return SteveBrulePrompt().prompt
  elif character == "steve_brule_quiz":
    return SteveBruleQuizPrompt().prompt
    return None



