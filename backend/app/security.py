from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.enums import Papel
from app.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def gerar_hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verificar_senha(senha: str, senha_hash: str | None) -> bool:
    if not senha_hash:
        return False
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())


def criar_token_acesso(usuario: Usuario) -> tuple[str, int]:
    settings = get_settings()
    expira_em = settings.jwt_expire_minutes * 60
    payload = {
        "sub": str(usuario.id),
        "email": usuario.email,
        "papel": usuario.papel,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expira_em),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm), expira_em


def get_usuario_atual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise credenciais_invalidas from exc

    usuario = db.get(Usuario, usuario_id)
    if usuario is None or not usuario.ativo:
        raise credenciais_invalidas
    return usuario


def exigir_papel(*papeis: Papel):
    permitidos = {p.value for p in papeis}

    def dependencia(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
        if usuario.papel not in permitidos:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")
        return usuario

    return dependencia
