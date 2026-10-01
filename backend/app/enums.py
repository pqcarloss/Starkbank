from enum import Enum


class Sensibilidade(str, Enum):
    PUBLICA = "Pública"
    INTERNA = "Interna"
    CONFIDENCIAL = "Confidencial"
    CRITICA = "Crítica"

    @property
    def nivel(self) -> int:
        return list(Sensibilidade).index(self)


class Risco(str, Enum):
    BAIXO = "Baixo"
    MEDIO = "Médio"
    ALTO = "Alto"
    CRITICO = "Crítico"

    @property
    def nivel(self) -> int:
        return list(Risco).index(self)

    @classmethod
    def from_nivel(cls, nivel: int) -> "Risco":
        membros = list(cls)
        return membros[max(0, min(nivel, len(membros) - 1))]


class StatusAlerta(str, Enum):
    ABERTO = "Aberto"
    EM_ANALISE = "Em análise"
    TRATADO = "Tratado"


class StatusFerramenta(str, Enum):
    APROVADA = "Aprovada"
    APROVADA_CONDICIONAL = "Aprovada condicional"
    NAO_APROVADA = "Não aprovada"


class Papel(str, Enum):
    ADMIN = "admin"
    ANALISTA = "analista"
    LEITOR = "leitor"
