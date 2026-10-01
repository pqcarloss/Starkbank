from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.enums import Papel, Risco, StatusAlerta
from app.models import Alerta, Usuario
from app.schemas import AlertaOut, AlertasPagina, AlertaUpdate
from app.security import exigir_papel, get_usuario_atual

router = APIRouter(prefix="/api/alertas", tags=["Alertas"])


@router.get("", response_model=AlertasPagina, dependencies=[Depends(get_usuario_atual)])
def listar(
    db: Session = Depends(get_db),
    pagina: int = Query(1, ge=1),
    tamanho: int = Query(20, ge=1, le=200),
    status: StatusAlerta | None = None,
    severidade: Risco | None = None,
) -> AlertasPagina:
    filtros = []
    if status:
        filtros.append(Alerta.status == status.value)
    if severidade:
        filtros.append(Alerta.severidade == severidade.value)
    total = db.scalar(select(func.count()).select_from(Alerta).where(*filtros)) or 0
    itens = db.scalars(
        select(Alerta)
        .where(*filtros)
        .options(joinedload(Alerta.evento))
        .order_by(Alerta.criado_em.desc())
        .offset((pagina - 1) * tamanho)
        .limit(tamanho)
    ).all()
    return AlertasPagina(
        total=total, pagina=pagina, tamanho=tamanho, itens=[AlertaOut.model_validate(a) for a in itens]
    )


@router.patch("/{alerta_id}", response_model=AlertaOut)
def atualizar(
    alerta_id: int,
    dados: AlertaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_papel(Papel.ADMIN, Papel.ANALISTA)),
) -> Alerta:
    alerta = db.get(Alerta, alerta_id)
    if alerta is None:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    valores = dados.model_dump(exclude_unset=True, mode="json")
    if "status" in valores and "responsavel" not in valores and not alerta.responsavel:
        valores["responsavel"] = usuario.email
    for campo, valor in valores.items():
        setattr(alerta, campo, valor)
    db.commit()
    db.refresh(alerta)
    return alerta
