import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass

from app.classification.base import Deteccao, ResultadoClassificacao
from app.enums import Sensibilidade

TIPO_PII = "Dados pessoais"
TIPO_FINANCEIRO = "Dados financeiros de clientes"
TIPO_CREDENCIAIS = "Credenciais e segredos"
TIPO_CODIGO = "Código-fonte"
TIPO_ESTRATEGICO = "Informação estratégica"
TIPO_CLIENTE_PJ = "Dados cadastrais de empresas"
TIPO_CONTATO = "Dados de contato"
TIPO_INTERNO = "Documento interno"
TIPO_PUBLICO = "Informação pública"

SENSIBILIDADE_PADRAO: dict[str, Sensibilidade] = {
    TIPO_PII: Sensibilidade.CONFIDENCIAL,
    TIPO_FINANCEIRO: Sensibilidade.CRITICA,
    TIPO_CREDENCIAIS: Sensibilidade.CRITICA,
    TIPO_CODIGO: Sensibilidade.CONFIDENCIAL,
    TIPO_ESTRATEGICO: Sensibilidade.CRITICA,
    TIPO_CLIENTE_PJ: Sensibilidade.CONFIDENCIAL,
    TIPO_CONTATO: Sensibilidade.INTERNA,
    TIPO_INTERNO: Sensibilidade.INTERNA,
    TIPO_PUBLICO: Sensibilidade.PUBLICA,
}


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sem_acento.lower()


def somente_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor)


def cpf_valido(valor: str) -> bool:
    d = somente_digitos(valor)
    if len(d) != 11 or d == d[0] * 11:
        return False
    for n in (9, 10):
        soma = sum(int(d[i]) * (n + 1 - i) for i in range(n))
        dv = (soma * 10) % 11 % 10
        if dv != int(d[n]):
            return False
    return True


def cnpj_valido(valor: str) -> bool:
    d = somente_digitos(valor)
    if len(d) != 14 or d == d[0] * 14:
        return False
    pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for n in (12, 13):
        soma = sum(int(d[i]) * pesos[i + 13 - n] for i in range(n))
        resto = soma % 11
        dv = 0 if resto < 2 else 11 - resto
        if dv != int(d[n]):
            return False
    return True


def luhn_valido(valor: str) -> bool:
    d = somente_digitos(valor)
    if not 13 <= len(d) <= 19:
        return False
    total = 0
    for i, c in enumerate(reversed(d)):
        n = int(c)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def mascarar(valor: str) -> str:
    valor = valor.strip()
    if len(valor) <= 4:
        return "*" * len(valor)
    visiveis = 2 if len(valor) < 10 else 3
    return valor[:visiveis] + "*" * (len(valor) - 2 * visiveis) + valor[-visiveis:]


@dataclass(frozen=True)
class RegraRegex:
    nome: str
    tipo_informacao: str
    padrao: re.Pattern[str]
    validador: Callable[[str], bool] | None = None
    minimo: int = 1
    mascarar_amostras: bool = True


@dataclass(frozen=True)
class RegraPalavrasChave:
    nome: str
    tipo_informacao: str
    termos: tuple[str, ...]
    minimo: int = 1


REGRAS_REGEX: tuple[RegraRegex, ...] = (
    RegraRegex("CPF válido", TIPO_PII, re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)"), cpf_valido),
    RegraRegex(
        "CNPJ válido", TIPO_CLIENTE_PJ, re.compile(r"(?<!\d)\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}(?!\d)"), cnpj_valido
    ),
    RegraRegex(
        "Cartão de pagamento (Luhn)", TIPO_FINANCEIRO, re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)"), luhn_valido
    ),
    RegraRegex(
        "Agência/conta bancária",
        TIPO_FINANCEIRO,
        re.compile(r"(?i)\b(?:ag(?:[eê]ncia)?\.?|conta(?:\s+corrente)?|c/c)\s*:?\s*\d{3,6}-?[\dxX]?\b"),
    ),
    RegraRegex("Chave de acesso AWS", TIPO_CREDENCIAIS, re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    RegraRegex(
        "Chave privada",
        TIPO_CREDENCIAIS,
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----"),
        mascarar_amostras=False,
    ),
    RegraRegex(
        "Token/segredo em atribuição",
        TIPO_CREDENCIAIS,
        re.compile(r"(?i)\b(?:senha|password|passwd|pwd|secret|api[_-]?key|token|client[_-]?secret)\s*[:=]\s*\S{4,}"),
    ),
    RegraRegex("Token JWT/Bearer", TIPO_CREDENCIAIS, re.compile(r"\beyJ[\w-]{10,}\.[\w-]{10,}\.[\w-]{10,}\b")),
    RegraRegex("E-mail", TIPO_CONTATO, re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    RegraRegex(
        "Telefone",
        TIPO_CONTATO,
        re.compile(r"(?<!\d)(?:\+?55\s?)?\(?\d{2}\)?\s?9?\d{4}-?\d{4}(?!\d)"),
    ),
    RegraRegex(
        "Sintaxe de código",
        TIPO_CODIGO,
        re.compile(
            r"(?m)^\s*(?:def |class |import |from \S+ import |function |const |let |public |private |#include)"
            r"|\bSELECT\b.+\bFROM\b|=>|\);\s*$"
        ),
        minimo=2,
        mascarar_amostras=False,
    ),
)

REGRAS_PALAVRAS_CHAVE: tuple[RegraPalavrasChave, ...] = (
    RegraPalavrasChave(
        "Termos de dados pessoais",
        TIPO_PII,
        ("data de nascimento", "nome da mae", "rg:", "prontuario", "endereco residencial"),
    ),
    RegraPalavrasChave(
        "Termos financeiros de clientes",
        TIPO_FINANCEIRO,
        ("saldo do cliente", "extrato", "limite de credito", "chave pix", "cvv", "fatura do cliente"),
    ),
    RegraPalavrasChave(
        "Termos estratégicos",
        TIPO_ESTRATEGICO,
        (
            "fusao",
            "aquisicao",
            "m&a",
            "fato relevante",
            "resultado nao divulgado",
            "estritamente confidencial",
            "plano estrategico",
            "due diligence",
        ),
    ),
    RegraPalavrasChave(
        "Marcação de uso interno",
        TIPO_INTERNO,
        ("uso interno", "politica interna", "procedimento interno", "nao compartilhar", "ata de reuniao"),
    ),
)

FINALIDADES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Desenvolvimento de software", ("codigo", "debug", "erro", "stack trace", "refator", "funcao", "query")),
    ("Análise de dados", ("analis", "planilha", "relatorio", "indicador", "dashboard")),
    ("Tradução", ("traduz", "traducao", "translate")),
    ("Resumo de documento", ("resum", "sintetiz")),
    ("Redação/comunicação", ("redig", "escrev", "e-mail", "email", "comunicado", "carta")),
    ("Atendimento ao cliente", ("cliente", "atendimento", "reclamacao")),
)


class ClassificadorRegras:
    nome = "regras-v1"

    def classificar(
        self,
        texto: str,
        finalidade_declarada: str | None = None,
        sensibilidade_por_tipo: dict[str, Sensibilidade] | None = None,
    ) -> ResultadoClassificacao:
        mapa = {**SENSIBILIDADE_PADRAO, **(sensibilidade_por_tipo or {})}
        deteccoes = self._detectar_regex(texto) + self._detectar_palavras_chave(texto)

        if not deteccoes:
            tipo = TIPO_PUBLICO
            tipos: list[str] = []
            sensibilidade = mapa.get(TIPO_PUBLICO, Sensibilidade.PUBLICA)
        else:
            contagem: dict[str, int] = {}
            for d in deteccoes:
                contagem[d.tipo_informacao] = contagem.get(d.tipo_informacao, 0) + d.ocorrencias
            tipos = sorted(
                contagem,
                key=lambda t: (mapa.get(t, Sensibilidade.INTERNA).nivel, contagem[t]),
                reverse=True,
            )
            tipo = tipos[0]
            sensibilidade = mapa.get(tipo, Sensibilidade.INTERNA)

        return ResultadoClassificacao(
            tipo_informacao=tipo,
            tipos_detectados=tipos,
            sensibilidade=sensibilidade,
            finalidade=finalidade_declarada.strip() if finalidade_declarada else self._inferir_finalidade(texto),
            deteccoes=deteccoes,
            classificador=self.nome,
        )

    @staticmethod
    def _detectar_regex(texto: str) -> list[Deteccao]:
        deteccoes: list[Deteccao] = []
        for regra in REGRAS_REGEX:
            achados = [m.group(0) for m in regra.padrao.finditer(texto)]
            if regra.validador:
                achados = [a for a in achados if regra.validador(a)]
            if len(achados) < regra.minimo:
                continue
            amostras = [mascarar(a) for a in achados[:3]] if regra.mascarar_amostras else []
            deteccoes.append(Deteccao(regra.nome, regra.tipo_informacao, len(achados), amostras))
        return deteccoes

    @staticmethod
    def _detectar_palavras_chave(texto: str) -> list[Deteccao]:
        normalizado = normalizar(texto)
        deteccoes: list[Deteccao] = []
        for regra in REGRAS_PALAVRAS_CHAVE:
            encontrados = [t for t in regra.termos if t in normalizado]
            ocorrencias = sum(normalizado.count(t) for t in encontrados)
            if ocorrencias >= regra.minimo:
                deteccoes.append(Deteccao(regra.nome, regra.tipo_informacao, ocorrencias, encontrados[:3]))
        return deteccoes

    @staticmethod
    def _inferir_finalidade(texto: str) -> str:
        normalizado = normalizar(texto)
        for finalidade, termos in FINALIDADES:
            if any(t in normalizado for t in termos):
                return f"{finalidade} (inferida)"
        return "Não informada"
