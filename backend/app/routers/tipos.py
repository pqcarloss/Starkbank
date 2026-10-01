from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import Papel
from app.models import TipoInformacao
from app.schemas import TipoInformacaoBase, TipoInformacaoOut, TipoInformacaoUpdate
from app.security import exigir_papel, get_usuario_atual

router = APIRouter(
    prefix="/api/tipos-informacao", tags=["Tipos de informação"], dependencies=[Depends(get_usuario_atual)]
)


@router.get("", response_model=list[TipoInformacaoOut])
def listar(db: Session = Depends(get_db)) -> list[TipoInformacao]:
    return list(db.scalars(select(TipoInformacao).order_by(TipoInformacao.nome)))


@router.post("", response_model=TipoInformacaoOut, status_code=201, dependencies=[Depends(exigir_papel(Papel.ADMIN))])
def criar(dados: TipoInformacaoBase, db: Session = Depends(get_db)) -> TipoInformacao:
    if db.scalar(select(TipoInformacao).where(TipoInformacao.nome.ilike(dados.nome))):
        raise HTTPException(status_code=409, detail="Tipo de informação já cadastrado")
    tipo = TipoInformacao(**dados.model_dump(mode="json"))
    db.add(tipo)
    db.commit()
    return tipo


@router.patch("/{tipo_id}", response_model=TipoInformacaoOut, dependencies=[Depends(exigir_papel(Papel.ADMIN))])
def atualizar(tipo_id: int, dados: TipoInformacaoUpdate, db: Session = Depends(get_db)) -> TipoInformacao:
    tipo = db.get(TipoInformacao, tipo_id)
    if tipo is None:
        raise HTTPException(status_code=404, detail="Tipo de informação não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True, mode="json").items():
        setattr(tipo, campo, valor)
    db.commit()
    return tipo
