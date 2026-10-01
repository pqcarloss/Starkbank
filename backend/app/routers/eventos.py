from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.enums import Papel, Risco, Sensibilidade
from app.models import Evento
from app.schemas import EventoCreate, EventoOut, EventosPagina
from app.security import exigir_papel, get_usuario_atual
from app.services import registrar_evento

router = APIRouter(prefix="/api/eventos", tags=["Eventos de uso de IA"])


@router.get("", response_model=EventosPagina, dependencies=[Depends(get_usuario_atual)])
def listar(
    db: Session = Depends(get_db),
    pagina: int = Query(1, ge=1),
    tamanho: int = Query(20, ge=1, le=200),
    risco: Risco | None = None,
    sensibilidade: Sensibilidade | None = None,
    ferramenta: str | None = None,
    tipo_informacao: str | None = None,
    id_usuario: str | None = None,
    inicio: datetime | None = None,
    fim: datetime | None = None,
) -> EventosPagina:
    filtros = []
    if risco:
        filtros.append(Evento.risco == risco.value)
    if sensibilidade:
        filtros.append(Evento.sensibilidade == sensibilidade.value)
    if ferramenta:
        filtros.append(Evento.ferramenta_nome == ferramenta)
    if tipo_informacao:
        filtros.append(Evento.tipo_informacao == tipo_informacao)
    if id_usuario:
        filtros.append(Evento.id_usuario == id_usuario)
    if inicio:
        filtros.append(Evento.data_hora >= inicio)
    if fim:
        filtros.append(Evento.data_hora <= fim)

    total = db.scalar(select(func.count()).select_from(Evento).where(*filtros)) or 0
    itens = db.scalars(
        select(Evento)
        .where(*filtros)
        .options(selectinload(Evento.alerta))
        .order_by(Evento.data_hora.desc())
        .offset((pagina - 1) * tamanho)
        .limit(tamanho)
    ).all()
    return EventosPagina(
        total=total, pagina=pagina, tamanho=tamanho, itens=[EventoOut.model_validate(e) for e in itens]
    )


@router.get("/{evento_id}", response_model=EventoOut, dependencies=[Depends(get_usuario_atual)])
def obter(evento_id: str, db: Session = Depends(get_db)) -> Evento:
    evento = db.get(Evento, evento_id)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return evento


@router.post(
    "",
    response_model=EventoOut,
    status_code=201,
    dependencies=[Depends(exigir_papel(Papel.ADMIN, Papel.ANALISTA))],
)
def registrar(dados: EventoCreate, db: Session = Depends(get_db)) -> Evento:
    return registrar_evento(db, dados.texto, dados.ferramenta, dados.id_usuario, dados.finalidade, dados.data_hora)
