import hashlib
import hmac
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.classification import ResultadoClassificacao, get_classificador
from app.classification.risk import AvaliacaoRisco, avaliar_risco
from app.config import get_settings
from app.enums import Sensibilidade, StatusFerramenta
from app.models import Alerta, Evento, Ferramenta, TipoInformacao, agora


def pseudonimizar_usuario(id_corporativo: str) -> str:
    if id_corporativo.startswith("USR-"):
        return id_corporativo
    chave = get_settings().pseudonymization_key.encode()
    digest = hmac.new(chave, id_corporativo.strip().lower().encode(), hashlib.sha256).hexdigest()
    return f"USR-{digest[:10]}"


def mapa_sensibilidade(db: Session) -> dict[str, Sensibilidade]:
    return {t.nome: Sensibilidade(t.classificacao_padrao) for t in db.scalars(select(TipoInformacao))}


def buscar_ferramenta(db: Session, nome: str) -> Ferramenta | None:
    return db.scalar(select(Ferramenta).where(Ferramenta.nome.ilike(nome.strip())))


def analisar(
    db: Session, texto: str, ferramenta_nome: str, finalidade: str | None
) -> tuple[ResultadoClassificacao, AvaliacaoRisco, Ferramenta | None]:
    resultado = get_classificador().classificar(texto, finalidade, mapa_sensibilidade(db))
    ferramenta = buscar_ferramenta(db, ferramenta_nome)
    status = StatusFerramenta(ferramenta.status) if ferramenta else None
    avaliacao = avaliar_risco(resultado.sensibilidade, status, resultado.total_ocorrencias)
    return resultado, avaliacao, ferramenta


def registrar_evento(
    db: Session,
    texto: str,
    ferramenta_nome: str,
    id_usuario: str,
    finalidade: str | None = None,
    data_hora: datetime | None = None,
) -> Evento:
    resultado, avaliacao, ferramenta = analisar(db, texto, ferramenta_nome, finalidade)
    evento = Evento(
        id=f"EVT-{uuid.uuid4().hex[:12].upper()}",
        id_usuario=pseudonimizar_usuario(id_usuario),
        ferramenta_id=ferramenta.id if ferramenta else None,
        ferramenta_nome=ferramenta.nome if ferramenta else ferramenta_nome.strip(),
        tipo_informacao=resultado.tipo_informacao,
        tipos_detectados=resultado.tipos_detectados,
        sensibilidade=resultado.sensibilidade.value,
        finalidade=resultado.finalidade,
        risco=avaliacao.risco.value,
        evidencias=resultado.evidencias + avaliacao.evidencias,
        classificador=resultado.classificador,
        conteudo_hash=hashlib.sha256(texto.encode()).hexdigest(),
        conteudo_tamanho=len(texto),
        data_hora=data_hora or agora(),
    )
    db.add(evento)
    if avaliacao.gera_alerta:
        db.add(Alerta(evento=evento, severidade=avaliacao.risco.value, criado_em=evento.data_hora))
    db.commit()
    db.refresh(evento)
    return evento
