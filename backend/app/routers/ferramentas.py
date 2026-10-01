from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import Papel
from app.models import Ferramenta
from app.schemas import FerramentaBase, FerramentaOut, FerramentaUpdate
from app.security import exigir_papel, get_usuario_atual

router = APIRouter(prefix="/api/ferramentas", tags=["Ferramentas de IA"], dependencies=[Depends(get_usuario_atual)])


@router.get("", response_model=list[FerramentaOut])
def listar(db: Session = Depends(get_db)) -> list[Ferramenta]:
    return list(db.scalars(select(Ferramenta).order_by(Ferramenta.nome)))


@router.post("", response_model=FerramentaOut, status_code=201, dependencies=[Depends(exigir_papel(Papel.ADMIN))])
def criar(dados: FerramentaBase, db: Session = Depends(get_db)) -> Ferramenta:
    if db.scalar(select(Ferramenta).where(Ferramenta.nome.ilike(dados.nome))):
        raise HTTPException(status_code=409, detail="Ferramenta já cadastrada")
    ferramenta = Ferramenta(**dados.model_dump(mode="json"))
    db.add(ferramenta)
    db.commit()
    return ferramenta


@router.patch("/{ferramenta_id}", response_model=FerramentaOut, dependencies=[Depends(exigir_papel(Papel.ADMIN))])
def atualizar(ferramenta_id: int, dados: FerramentaUpdate, db: Session = Depends(get_db)) -> Ferramenta:
    ferramenta = db.get(Ferramenta, ferramenta_id)
    if ferramenta is None:
        raise HTTPException(status_code=404, detail="Ferramenta não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True, mode="json").items():
        setattr(ferramenta, campo, valor)
    db.commit()
    return ferramenta
