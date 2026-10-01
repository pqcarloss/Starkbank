from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import Token, UsuarioOut
from app.security import criar_token_acesso, get_usuario_atual, verificar_senha

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    usuario = db.scalar(select(Usuario).where(Usuario.email == form.username.strip().lower()))
    if (
        usuario is None
        or not usuario.ativo
        or usuario.provedor_auth != "local"
        or not verificar_senha(form.password, usuario.senha_hash)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha incorretos")
    token, expira_em = criar_token_acesso(usuario)
    return Token(access_token=token, expires_in=expira_em)


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
    return usuario
