from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import Risco, Sensibilidade, StatusAlerta, StatusFerramenta
from app.models import Alerta, Evento, Ferramenta
from app.schemas import Contagem, DashboardResumo, SerieDiaria
from app.security import get_usuario_atual

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"], dependencies=[Depends(get_usuario_atual)])


def _contar(db: Session, coluna, filtros, ordem: list[str] | None = None, limite: int | None = None) -> list[Contagem]:
    linhas = db.execute(select(coluna, func.count()).where(*filtros).group_by(coluna)).all()
    contagens = {str(r): int(t) for r, t in linhas}
    if ordem:
        return [Contagem(rotulo=r, total=contagens.get(r, 0)) for r in ordem]
    itens = sorted(contagens.items(), key=lambda x: x[1], reverse=True)
    return [Contagem(rotulo=r, total=t) for r, t in itens[:limite]]


@router.get("/resumo", response_model=DashboardResumo)
def resumo(db: Session = Depends(get_db), dias: int = Query(30, ge=1, le=365)) -> DashboardResumo:
    inicio_dia = datetime.now(timezone.utc).date() - timedelta(days=dias - 1)
    inicio = datetime.combine(inicio_dia, datetime.min.time(), tzinfo=timezone.utc)
    periodo = [Evento.data_hora >= inicio]
    alto_critico = Evento.risco.in_([Risco.ALTO.value, Risco.CRITICO.value])

    total = db.scalar(select(func.count()).select_from(Evento).where(*periodo)) or 0
    alto = db.scalar(select(func.count()).select_from(Evento).where(*periodo, alto_critico)) or 0
    usuarios = db.scalar(select(func.count(func.distinct(Evento.id_usuario))).where(*periodo)) or 0
    nao_aprovadas = (
        db.scalar(
            select(func.count())
            .select_from(Evento)
            .outerjoin(Ferramenta, Evento.ferramenta_id == Ferramenta.id)
            .where(
                *periodo,
                (Ferramenta.id.is_(None)) | (Ferramenta.status == StatusFerramenta.NAO_APROVADA.value),
            )
        )
        or 0
    )
    abertos = (
        db.scalar(select(func.count()).select_from(Alerta).where(Alerta.status != StatusAlerta.TRATADO.value)) or 0
    )

    dia = func.date(Evento.data_hora)
    linhas = db.execute(
        select(dia, func.count(), func.sum(case((alto_critico, 1), else_=0))).where(*periodo).group_by(dia)
    ).all()
    por_dia = {str(d): (int(t), int(a or 0)) for d, t, a in linhas}
    serie = []
    for i in range(dias):
        d = str(inicio_dia + timedelta(days=i))
        t, a = por_dia.get(d, (0, 0))
        serie.append(SerieDiaria(data=d, total=t, alto_critico=a))

    return DashboardResumo(
        total_eventos=total,
        alertas_abertos=abertos,
        eventos_alto_critico=alto,
        usuarios_distintos=usuarios,
        eventos_ferramentas_nao_aprovadas=nao_aprovadas,
        por_risco=_contar(db, Evento.risco, periodo, [r.value for r in Risco]),
        por_sensibilidade=_contar(db, Evento.sensibilidade, periodo, [s.value for s in Sensibilidade]),
        por_ferramenta=_contar(db, Evento.ferramenta_nome, periodo, limite=10),
        por_tipo_informacao=_contar(db, Evento.tipo_informacao, periodo, limite=10),
        alertas_por_status=_contar(db, Alerta.status, [], [s.value for s in StatusAlerta]),
        serie_diaria=serie,
    )
