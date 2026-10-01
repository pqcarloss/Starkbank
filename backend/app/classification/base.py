from dataclasses import dataclass, field
from typing import Protocol

from app.enums import Sensibilidade


@dataclass(frozen=True)
class Deteccao:
    regra: str
    tipo_informacao: str
    ocorrencias: int
    amostras: list[str] = field(default_factory=list)

    @property
    def evidencia(self) -> str:
        amostras = f": {', '.join(self.amostras)}" if self.amostras else ""
        return f"{self.regra} ({self.ocorrencias}x){amostras}"


@dataclass(frozen=True)
class ResultadoClassificacao:
    tipo_informacao: str
    tipos_detectados: list[str]
    sensibilidade: Sensibilidade
    finalidade: str
    deteccoes: list[Deteccao]
    classificador: str

    @property
    def total_ocorrencias(self) -> int:
        return sum(d.ocorrencias for d in self.deteccoes)

    @property
    def evidencias(self) -> list[str]:
        return [d.evidencia for d in self.deteccoes]


class Classificador(Protocol):
    nome: str

    def classificar(
        self,
        texto: str,
        finalidade_declarada: str | None = None,
        sensibilidade_por_tipo: dict[str, Sensibilidade] | None = None,
    ) -> ResultadoClassificacao: ...
