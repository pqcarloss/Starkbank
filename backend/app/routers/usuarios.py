from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import Papel
from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.security import exigir_papel, gerar_hash_senha

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"], dependencies=[Depends(exigir_papel(Papel.ADMIN))])


@router.get("", response_model=list[UsuarioOut])
def listar(db: Session = Depends(get_db)) -> list[Usuario]:
    return list(db.scalars(select(Usuario).order_by(Usuario.nome)))


@router.post("", response_model=UsuarioOut, status_code=201)
def criar(dados: UsuarioCreate, db: Session = Depends(get_db)) -> Usuario:
    email = dados.email.lower()
    if db.scalar(select(Usuario).where(Usuario.email == email)):
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    usuario = Usuario(email=email, nome=dados.nome, papel=dados.papel.value, senha_hash=gerar_hash_senha(dados.senha))
    db.add(usuario)
    db.commit()
    return usuario


@router.patch("/{usuario_id}", response_model=UsuarioOut)
def atualizar(usuario_id: int, dados: UsuarioUpdate, db: Session = Depends(get_db)) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True, mode="json").items():
        setattr(usuario, campo, valor)
    db.commit()
    return usuario
