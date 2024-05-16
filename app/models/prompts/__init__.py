from .steve_brule import SteveBrulePrompt
from .steve_brule_quiz import SteveBruleQuizPrompt
from .steve_brule_quiz_all import SteveBruleQuizAllPrompt

def prompt(mode, character, quiz_topic=None):
  if character == "steve_brule":
    if mode == "quiz" and quiz_topic != "all":
      return SteveBruleQuizPrompt().prompt
    elif mode == "quiz" and quiz_topic == "all":
      return SteveBruleQuizAllPrompt().prompt
    else:
      return SteveBrulePrompt().prompt



