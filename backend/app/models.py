from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import Papel, StatusAlerta


def agora() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(255))
    senha_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    papel: Mapped[str] = mapped_column(String(20), default=Papel.LEITOR.value)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    provedor_auth: Mapped[str] = mapped_column(String(50), default="local")
    sub_externo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)


class Ferramenta(Base):
    __tablename__ = "ferramentas_ia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    fornecedor: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(30))
    observacoes: Mapped[str] = mapped_column(Text, default="")

    eventos: Mapped[list["Evento"]] = relationship(back_populates="ferramenta")


class TipoInformacao(Base):
    __tablename__ = "tipos_informacao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    descricao: Mapped[str] = mapped_column(Text, default="")
    classificacao_padrao: Mapped[str] = mapped_column(String(20))


class Evento(Base):
    __tablename__ = "eventos_uso_ia"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    id_usuario: Mapped[str] = mapped_column(String(40), index=True)
    ferramenta_id: Mapped[int | None] = mapped_column(ForeignKey("ferramentas_ia.id"), nullable=True)
    ferramenta_nome: Mapped[str] = mapped_column(String(120), index=True)
    tipo_informacao: Mapped[str] = mapped_column(String(120), index=True)
    tipos_detectados: Mapped[list[str]] = mapped_column(JSON, default=list)
    sensibilidade: Mapped[str] = mapped_column(String(20), index=True)
    finalidade: Mapped[str] = mapped_column(String(255))
    risco: Mapped[str] = mapped_column(String(20), index=True)
    evidencias: Mapped[list[str]] = mapped_column(JSON, default=list)
    classificador: Mapped[str] = mapped_column(String(40))
    conteudo_hash: Mapped[str] = mapped_column(String(64))
    conteudo_tamanho: Mapped[int] = mapped_column(Integer, default=0)
    data_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, index=True)

    ferramenta: Mapped[Ferramenta | None] = relationship(back_populates="eventos")
    alerta: Mapped["Alerta | None"] = relationship(back_populates="evento", uselist=False)


class Alerta(Base):
    __tablename__ = "alertas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evento_id: Mapped[str] = mapped_column(ForeignKey("eventos_uso_ia.id"), unique=True)
    severidade: Mapped[str] = mapped_column(String(20), index=True)
    status: Mapped[str] = mapped_column(String(20), default=StatusAlerta.ABERTO.value, index=True)
    responsavel: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observacao: Mapped[str] = mapped_column(Text, default="")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, onupdate=agora)

    evento: Mapped[Evento] = relationship(back_populates="alerta")


class CasoValidacao(Base):
    __tablename__ = "casos_validacao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    descricao: Mapped[str] = mapped_column(String(255))
    ferramenta_nome: Mapped[str] = mapped_column(String(120))
    texto_entrada: Mapped[str] = mapped_column(Text)
    sensibilidade_esperada: Mapped[str] = mapped_column(String(20))
    risco_esperado: Mapped[str] = mapped_column(String(20))
