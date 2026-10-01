from app.classification.base import Classificador
from app.classification.rules import ClassificadorRegras
from app.config import get_settings


def get_classificador() -> Classificador:
    backend = get_settings().classifier_backend
    if backend == "rules":
        return ClassificadorRegras()
    raise ValueError(
        f"Classificador '{backend}' não disponível. Backends NLP/LLM devem implementar o protocolo Classificador."
    )
