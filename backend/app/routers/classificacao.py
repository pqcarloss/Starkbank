from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ClassificacaoOut, ClassificacaoRequest, DeteccaoOut
from app.security import get_usuario_atual
from app.services import analisar

router = APIRouter(prefix="/api/classificar", tags=["Classificação DLP"], dependencies=[Depends(get_usuario_atual)])


@router.post("", response_model=ClassificacaoOut)
def classificar(dados: ClassificacaoRequest, db: Session = Depends(get_db)) -> ClassificacaoOut:
    resultado, avaliacao, _ = analisar(db, dados.texto, dados.ferramenta, dados.finalidade)
    return ClassificacaoOut(
        tipo_informacao=resultado.tipo_informacao,
        tipos_detectados=resultado.tipos_detectados,
        sensibilidade=resultado.sensibilidade,
        finalidade=resultado.finalidade,
        risco=avaliacao.risco,
        gera_alerta=avaliacao.gera_alerta,
        evidencias=resultado.evidencias + avaliacao.evidencias,
        deteccoes=[DeteccaoOut(**asdict(d)) for d in resultado.deteccoes],
        classificador=resultado.classificador,
    )
