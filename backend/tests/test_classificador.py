import pytest

from app.classification.risk import avaliar_risco
from app.classification.rules import (
    TIPO_CODIGO,
    TIPO_CONTATO,
    TIPO_CREDENCIAIS,
    TIPO_ESTRATEGICO,
    TIPO_FINANCEIRO,
    TIPO_PII,
    TIPO_PUBLICO,
    ClassificadorRegras,
    cnpj_valido,
    cpf_valido,
    luhn_valido,
    mascarar,
)
from app.enums import Risco, Sensibilidade, StatusFerramenta

classificador = ClassificadorRegras()


@pytest.mark.parametrize(
    "valor,esperado",
    [("529.982.247-25", True), ("52998224725", True), ("111.111.111-11", False), ("529.982.247-26", False)],
)
def test_cpf(valor: str, esperado: bool) -> None:
    assert cpf_valido(valor) is esperado


def test_cnpj_e_luhn() -> None:
    assert cnpj_valido("11.222.333/0001-81")
    assert not cnpj_valido("11.222.333/0001-80")
    assert luhn_valido("4111 1111 1111 1111")
    assert not luhn_valido("4111 1111 1111 1112")


def test_mascarar_nao_expoe_valor() -> None:
    assert mascarar("529.982.247-25") == "529********-25"


@pytest.mark.parametrize(
    "texto,tipo,sensibilidade",
    [
        ("Sugira nomes para um evento.", TIPO_PUBLICO, Sensibilidade.PUBLICA),
        ("Cliente 529.982.247-25 pediu revisão.", TIPO_PII, Sensibilidade.CONFIDENCIAL),
        ("Cartão 5555 5555 5555 4444 recusado.", TIPO_FINANCEIRO, Sensibilidade.CRITICA),
        ("aws = AKIAABCDEFGHIJKLMNOP", TIPO_CREDENCIAIS, Sensibilidade.CRITICA),
        ("-----BEGIN RSA PRIVATE KEY-----\nabc", TIPO_CREDENCIAIS, Sensibilidade.CRITICA),
        ("def f():\n    return 1\nclass A:\n    pass", TIPO_CODIGO, Sensibilidade.CONFIDENCIAL),
        ("Resumo da Aquisição da empresa X", TIPO_ESTRATEGICO, Sensibilidade.CRITICA),
        ("Fale com joao@x.com.br", TIPO_CONTATO, Sensibilidade.INTERNA),
    ],
)
def test_classificacao(texto: str, tipo: str, sensibilidade: Sensibilidade) -> None:
    resultado = classificador.classificar(texto)
    assert resultado.tipo_informacao == tipo
    assert resultado.sensibilidade == sensibilidade


def test_tipo_principal_e_o_mais_sensivel() -> None:
    r = classificador.classificar("CPF 529.982.247-25, e-mail a@b.com, senha: SuperSecreta1")
    assert r.tipo_informacao == TIPO_CREDENCIAIS
    assert set(r.tipos_detectados) == {TIPO_CREDENCIAIS, TIPO_PII, TIPO_CONTATO}


def test_evidencias_nao_contem_dado_em_claro() -> None:
    r = classificador.classificar("CPF 529.982.247-25")
    assert all("529.982.247-25" not in e for e in r.evidencias)


def test_sensibilidade_configuravel() -> None:
    r = classificador.classificar(
        "Fale com joao@x.com.br", sensibilidade_por_tipo={TIPO_CONTATO: Sensibilidade.CRITICA}
    )
    assert r.sensibilidade == Sensibilidade.CRITICA


def test_finalidade() -> None:
    assert classificador.classificar("Traduza este texto").finalidade == "Tradução (inferida)"
    assert classificador.classificar("x", finalidade_declarada="Pesquisa").finalidade == "Pesquisa"


@pytest.mark.parametrize(
    "sens,status,ocorrencias,esperado",
    [
        (Sensibilidade.PUBLICA, StatusFerramenta.APROVADA, 0, Risco.BAIXO),
        (Sensibilidade.CRITICA, StatusFerramenta.APROVADA, 1, Risco.ALTO),
        (Sensibilidade.CONFIDENCIAL, StatusFerramenta.NAO_APROVADA, 1, Risco.CRITICO),
        (Sensibilidade.INTERNA, None, 1, Risco.ALTO),
        (Sensibilidade.CONFIDENCIAL, StatusFerramenta.APROVADA, 10, Risco.ALTO),
        (Sensibilidade.INTERNA, StatusFerramenta.APROVADA, 50, Risco.BAIXO),
    ],
)
def test_matriz_risco(sens: Sensibilidade, status: StatusFerramenta | None, ocorrencias: int, esperado: Risco) -> None:
    assert avaliar_risco(sens, status, ocorrencias).risco == esperado
