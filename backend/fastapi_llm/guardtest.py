import guardrails
print("Guardrails version:", getattr(guardrails, "__version__", "NO __version__"))
print("Guardrails file:", guardrails.__file__)
from guardrails.guard import Guard
print("Guard class docstring:", Guard.__doc__)