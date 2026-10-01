from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import Papel
from app.models import CasoValidacao
from app.schemas import CasoValidacaoBase, CasoValidacaoOut, ExecucaoValidacao, ResultadoCaso
from app.security import exigir_papel, get_usuario_atual
from app.services import analisar

router = APIRouter(prefix="/api/casos-validacao", tags=["Casos de validação"])


@router.get("", response_model=list[CasoValidacaoOut], dependencies=[Depends(get_usuario_atual)])
def listar(db: Session = Depends(get_db)) -> list[CasoValidacao]:
    return list(db.scalars(select(CasoValidacao).order_by(CasoValidacao.id)))


@router.post("", response_model=CasoValidacaoOut, status_code=201, dependencies=[Depends(exigir_papel(Papel.ADMIN))])
def criar(dados: CasoValidacaoBase, db: Session = Depends(get_db)) -> CasoValidacao:
    caso = CasoValidacao(**dados.model_dump(mode="json"))
    db.add(caso)
    db.commit()
    return caso


@router.delete("/{caso_id}", status_code=204, dependencies=[Depends(exigir_papel(Papel.ADMIN))])
def remover(caso_id: int, db: Session = Depends(get_db)) -> None:
    caso = db.get(CasoValidacao, caso_id)
    if caso is None:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    db.delete(caso)
    db.commit()


@router.post("/executar", response_model=ExecucaoValidacao, dependencies=[Depends(get_usuario_atual)])
def executar(db: Session = Depends(get_db)) -> ExecucaoValidacao:
    resultados: list[ResultadoCaso] = []
    for caso in db.scalars(select(CasoValidacao).order_by(CasoValidacao.id)):
        resultado, avaliacao, _ = analisar(db, caso.texto_entrada, caso.ferramenta_nome, None)
        resultados.append(
            ResultadoCaso(
                caso=CasoValidacaoOut.model_validate(caso),
                sensibilidade_obtida=resultado.sensibilidade,
                risco_obtido=avaliacao.risco,
                aprovado=resultado.sensibilidade.value == caso.sensibilidade_esperada
                and avaliacao.risco.value == caso.risco_esperado,
                evidencias=resultado.evidencias + avaliacao.evidencias,
            )
        )
    aprovados = sum(r.aprovado for r in resultados)
    return ExecucaoValidacao(
        total=len(resultados),
        aprovados=aprovados,
        taxa_acerto=round(aprovados / len(resultados), 4) if resultados else 0.0,
        resultados=resultados,
    )
