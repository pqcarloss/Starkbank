from dataclasses import dataclass

from app.enums import Risco, Sensibilidade, StatusFerramenta

MATRIZ_RISCO: dict[StatusFerramenta, dict[Sensibilidade, Risco]] = {
    StatusFerramenta.APROVADA: {
        Sensibilidade.PUBLICA: Risco.BAIXO,
        Sensibilidade.INTERNA: Risco.BAIXO,
        Sensibilidade.CONFIDENCIAL: Risco.MEDIO,
        Sensibilidade.CRITICA: Risco.ALTO,
    },
    StatusFerramenta.APROVADA_CONDICIONAL: {
        Sensibilidade.PUBLICA: Risco.BAIXO,
        Sensibilidade.INTERNA: Risco.MEDIO,
        Sensibilidade.CONFIDENCIAL: Risco.ALTO,
        Sensibilidade.CRITICA: Risco.CRITICO,
    },
    StatusFerramenta.NAO_APROVADA: {
        Sensibilidade.PUBLICA: Risco.MEDIO,
        Sensibilidade.INTERNA: Risco.ALTO,
        Sensibilidade.CONFIDENCIAL: Risco.CRITICO,
        Sensibilidade.CRITICA: Risco.CRITICO,
    },
}

LIMIAR_VOLUME = 10
RISCOS_QUE_GERAM_ALERTA = {Risco.ALTO, Risco.CRITICO}


@dataclass(frozen=True)
class AvaliacaoRisco:
    risco: Risco
    evidencias: list[str]

    @property
    def gera_alerta(self) -> bool:
        return self.risco in RISCOS_QUE_GERAM_ALERTA


def avaliar_risco(
    sensibilidade: Sensibilidade,
    status_ferramenta: StatusFerramenta | None,
    total_ocorrencias: int,
) -> AvaliacaoRisco:
    evidencias: list[str] = []
    if status_ferramenta is None:
        status_ferramenta = StatusFerramenta.NAO_APROVADA
        evidencias.append("Ferramenta fora do inventário (shadow AI)")
    else:
        evidencias.append(f"Ferramenta com status '{status_ferramenta.value}'")

    risco = MATRIZ_RISCO[status_ferramenta][sensibilidade]
    evidencias.append(f"Sensibilidade '{sensibilidade.value}' x ferramenta => risco base '{risco.value}'")

    if total_ocorrencias >= LIMIAR_VOLUME and sensibilidade.nivel >= Sensibilidade.CONFIDENCIAL.nivel:
        elevado = Risco.from_nivel(risco.nivel + 1)
        if elevado != risco:
            evidencias.append(f"Volume elevado ({total_ocorrencias} ocorrências) eleva risco para '{elevado.value}'")
            risco = elevado

    return AvaliacaoRisco(risco, evidencias)
