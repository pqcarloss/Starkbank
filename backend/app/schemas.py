from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums import Papel, Risco, Sensibilidade, StatusAlerta, StatusFerramenta


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UsuarioOut(ORMModel):
    id: int
    email: str
    nome: str
    papel: Papel
    ativo: bool
    provedor_auth: str


class UsuarioCreate(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=255)
    nome: str = Field(min_length=1, max_length=255)
    senha: str = Field(min_length=8)
    papel: Papel = Papel.LEITOR


class UsuarioUpdate(BaseModel):
    nome: str | None = None
    papel: Papel | None = None
    ativo: bool | None = None


class FerramentaBase(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    fornecedor: str = ""
    status: StatusFerramenta
    observacoes: str = ""


class FerramentaOut(FerramentaBase, ORMModel):
    id: int


class FerramentaUpdate(BaseModel):
    fornecedor: str | None = None
    status: StatusFerramenta | None = None
    observacoes: str | None = None


class TipoInformacaoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    descricao: str = ""
    classificacao_padrao: Sensibilidade


class TipoInformacaoOut(TipoInformacaoBase, ORMModel):
    id: int


class TipoInformacaoUpdate(BaseModel):
    descricao: str | None = None
    classificacao_padrao: Sensibilidade | None = None


class DeteccaoOut(BaseModel):
    regra: str
    tipo_informacao: str
    ocorrencias: int
    amostras: list[str]


class ClassificacaoRequest(BaseModel):
    texto: str = Field(min_length=1, max_length=200_000)
    ferramenta: str = Field(min_length=1, max_length=120)
    finalidade: str | None = None


class ClassificacaoOut(BaseModel):
    tipo_informacao: str
    tipos_detectados: list[str]
    sensibilidade: Sensibilidade
    finalidade: str
    risco: Risco
    gera_alerta: bool
    evidencias: list[str]
    deteccoes: list[DeteccaoOut]
    classificador: str


class EventoCreate(ClassificacaoRequest):
    id_usuario: str = Field(min_length=1, max_length=255, description="ID corporativo (será pseudonimizado)")
    data_hora: datetime | None = None


class AlertaResumo(ORMModel):
    id: int
    status: StatusAlerta
    severidade: Risco


class EventoOut(ORMModel):
    id: str
    id_usuario: str
    ferramenta_nome: str
    tipo_informacao: str
    tipos_detectados: list[str]
    sensibilidade: Sensibilidade
    finalidade: str
    risco: Risco
    evidencias: list[str]
    classificador: str
    conteudo_tamanho: int
    data_hora: datetime
    alerta: AlertaResumo | None = None


class Pagina(BaseModel):
    total: int
    pagina: int
    tamanho: int


class EventosPagina(Pagina):
    itens: list[EventoOut]


class AlertaOut(ORMModel):
    id: int
    evento_id: str
    severidade: Risco
    status: StatusAlerta
    responsavel: str | None
    observacao: str
    criado_em: datetime
    atualizado_em: datetime
    evento: EventoOut


class AlertasPagina(Pagina):
    itens: list[AlertaOut]


class AlertaUpdate(BaseModel):
    status: StatusAlerta | None = None
    responsavel: str | None = None
    observacao: str | None = None


class CasoValidacaoBase(BaseModel):
    descricao: str = Field(min_length=1, max_length=255)
    ferramenta_nome: str
    texto_entrada: str
    sensibilidade_esperada: Sensibilidade
    risco_esperado: Risco


class CasoValidacaoOut(CasoValidacaoBase, ORMModel):
    id: int


class ResultadoCaso(BaseModel):
    caso: CasoValidacaoOut
    sensibilidade_obtida: Sensibilidade
    risco_obtido: Risco
    aprovado: bool
    evidencias: list[str]


class ExecucaoValidacao(BaseModel):
    total: int
    aprovados: int
    taxa_acerto: float
    resultados: list[ResultadoCaso]


class Contagem(BaseModel):
    rotulo: str
    total: int


class SerieDiaria(BaseModel):
    data: str
    total: int
    alto_critico: int


class DashboardResumo(BaseModel):
    total_eventos: int
    alertas_abertos: int
    eventos_alto_critico: int
    usuarios_distintos: int
    eventos_ferramentas_nao_aprovadas: int
    por_risco: list[Contagem]
    por_sensibilidade: list[Contagem]
    por_ferramenta: list[Contagem]
    por_tipo_informacao: list[Contagem]
    alertas_por_status: list[Contagem]
    serie_diaria: list[SerieDiaria]
