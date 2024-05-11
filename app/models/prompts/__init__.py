from .steve_brule import SteveBrulePrompt
def prompt(character):
  if character == "steve_brule":
    return SteveBrulePrompt().prompt
  else:
    return None


  
