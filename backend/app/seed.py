import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.classification import rules
from app.config import get_settings
from app.enums import Papel, Risco, Sensibilidade, StatusAlerta, StatusFerramenta
from app.models import Alerta, CasoValidacao, Evento, Ferramenta, TipoInformacao, Usuario
from app.security import gerar_hash_senha
from app.services import registrar_evento

FERRAMENTAS = [
    ("ChatGPT Enterprise", "OpenAI", StatusFerramenta.APROVADA, "Tenant corporativo com retenção zero."),
    ("Microsoft Copilot", "Microsoft", StatusFerramenta.APROVADA, "Integrado ao M365 corporativo."),
    ("GitHub Copilot", "GitHub", StatusFerramenta.APROVADA, "Licença Business, sem retenção de código."),
    ("Google Gemini", "Google", StatusFerramenta.APROVADA_CONDICIONAL, "Somente dados públicos e internos."),
    ("Claude", "Anthropic", StatusFerramenta.APROVADA_CONDICIONAL, "Piloto restrito ao time de dados."),
    ("DeepSeek", "DeepSeek", StatusFerramenta.NAO_APROVADA, "Hospedagem fora do Brasil sem contrato."),
    ("ChatGPT (conta pessoal)", "OpenAI", StatusFerramenta.NAO_APROVADA, "Conta pessoal sem DPA."),
    ("Perplexity", "Perplexity AI", StatusFerramenta.NAO_APROVADA, "Em avaliação pela Governança de IA."),
]

TIPOS = [
    (rules.TIPO_PII, "CPF, RG, data de nascimento e demais dados pessoais (LGPD)."),
    (rules.TIPO_FINANCEIRO, "Cartões, contas, saldos, extratos e chaves PIX de clientes."),
    (rules.TIPO_CREDENCIAIS, "Senhas, tokens, chaves de API e chaves privadas."),
    (rules.TIPO_CODIGO, "Código-fonte proprietário e consultas a bancos de dados."),
    (rules.TIPO_ESTRATEGICO, "M&A, resultados não divulgados, planos estratégicos."),
    (rules.TIPO_CLIENTE_PJ, "CNPJ e dados cadastrais de clientes pessoa jurídica."),
    (rules.TIPO_CONTATO, "E-mails e telefones."),
    (rules.TIPO_INTERNO, "Políticas, procedimentos e atas de uso interno."),
    (rules.TIPO_PUBLICO, "Conteúdo sem dados sensíveis detectados."),
]


def gerar_cpf(rng: random.Random) -> str:
    d = [rng.randint(0, 9) for _ in range(9)]
    for n in (9, 10):
        d.append((sum(d[i] * (n + 1 - i) for i in range(n)) * 10) % 11 % 10)
    s = "".join(map(str, d))
    return f"{s[:3]}.{s[3:6]}.{s[6:9]}-{s[9:]}"


def gerar_cnpj(rng: random.Random) -> str:
    d = [rng.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]
    pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for n in (12, 13):
        resto = sum(d[i] * pesos[i + 13 - n] for i in range(n)) % 11
        d.append(0 if resto < 2 else 11 - resto)
    s = "".join(map(str, d))
    return f"{s[:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:]}"


def cpfs(rng: random.Random, n: int) -> str:
    return "\n".join(f"Cliente {i + 1}: {gerar_cpf(rng)}" for i in range(n))


CARTOES = ["4111 1111 1111 1111", "5555 5555 5555 4444", "4012 8888 8888 1881", "3782 822463 10005"]

MODELOS = [
    ("Resuma o comunicado público sobre o lançamento do novo app Starkbank.", None),
    ("Traduza para inglês o texto institucional do nosso site.", None),
    ("Escreva um e-mail convidando o time para o happy hour de sexta.", None),
    ("Crie um plano de estudos de Python para iniciantes.", None),
    ("Resuma esta ata de reunião de uso interno sobre o roadmap do trimestre.", None),
    ("Revise o procedimento interno de abertura de chamados (não compartilhar).", None),
    ("Analise a planilha de clientes:\n{cpfs}", "Análise de dados"),
    ("Valide o cadastro do cliente CPF {cpf}, data de nascimento 12/03/1985, nome da mãe Maria.", None),
    ("O cliente {cpf} reclamou da fatura do cliente com cartão {cartao}. Redija resposta.", None),
    ("Calcule o limite de crédito para agência 0001 conta 123456-7 com saldo do cliente de R$ 52 mil.", None),
    ("Corrija o erro:\nimport boto3\nclient = boto3.client('s3')\naws_key = {aws}\ndef up():\n    pass", None),
    ("Por que esta conexão falha?\npassword={senha}\nconst db = connect(url);\nlet x = db.query();", None),
    ("Refatore a função:\ndef calcular_tarifa(valor):\n    return valor * 0.02\nclass Tarifa:\n    pass", None),
    ("Otimize a query: SELECT id, nome FROM clientes WHERE ativo = true;\nconst r = run(q);", None),
    ("Resuma o memorando estritamente confidencial sobre a aquisição da fintech XPTO (due diligence).", None),
    ("Monte uma apresentação do fato relevante com o resultado não divulgado do trimestre.", None),
    ("Cadastre a empresa {cnpj} como fornecedora, contato {email}, telefone (11) 98765-4321.", None),
    ("Envie a lista de contatos: {email}, (21) 3456-7890.", "Redação/comunicação"),
]

USUARIOS_CORPORATIVOS = [
    f"{n}.{s}"
    for n in ("ana", "bruno", "carla", "diego", "elisa", "felipe", "gabriela", "henrique", "isabela", "joao")
    for s in ("silva", "souza", "oliveira", "costa")
]

PESOS_FERRAMENTA = [30, 22, 14, 10, 6, 7, 7, 4]


CASOS_VALIDACAO = [
    (
        "Texto público em ferramenta aprovada",
        "ChatGPT Enterprise",
        "Resuma o comunicado público sobre o novo app disponível no site.",
        Sensibilidade.PUBLICA,
        Risco.BAIXO,
    ),
    (
        "Documento interno em ferramenta aprovada",
        "Microsoft Copilot",
        "Revise este procedimento interno de onboarding (uso interno).",
        Sensibilidade.INTERNA,
        Risco.BAIXO,
    ),
    (
        "CPFs em ferramenta não aprovada",
        "DeepSeek",
        "Organize estes clientes: 529.982.247-25, 111.444.777-35",
        Sensibilidade.CONFIDENCIAL,
        Risco.CRITICO,
    ),
    (
        "Cartão de crédito em ferramenta aprovada",
        "ChatGPT Enterprise",
        "Cliente contestou compra no cartão 4111 1111 1111 1111.",
        Sensibilidade.CRITICA,
        Risco.ALTO,
    ),
    (
        "Segredo em código em ferramenta condicional",
        "Claude",
        "Debug:\napi_key = 'sk-live-123456789abc'\ndef main():\n    pass",
        Sensibilidade.CRITICA,
        Risco.CRITICO,
    ),
    (
        "Código sem segredos em ferramenta aprovada",
        "GitHub Copilot",
        "def soma(a, b):\n    return a + b\nclass Calculadora:\n    pass",
        Sensibilidade.CONFIDENCIAL,
        Risco.MEDIO,
    ),
    (
        "M&A em ferramenta condicional",
        "Google Gemini",
        "Prepare resumo da due diligence para a aquisição da empresa Alfa.",
        Sensibilidade.CRITICA,
        Risco.CRITICO,
    ),
    (
        "Contatos em ferramenta fora do inventário",
        "NovaIA Free",
        "Contato: fulano@empresa.com.br, (11) 91234-5678",
        Sensibilidade.INTERNA,
        Risco.ALTO,
    ),
    (
        "Volume elevado de CPFs em ferramenta aprovada",
        "ChatGPT Enterprise",
        "\n".join(["529.982.247-25"] * 6 + ["111.444.777-35"] * 6),
        Sensibilidade.CONFIDENCIAL,
        Risco.ALTO,
    ),
    (
        "Texto público em ferramenta não aprovada",
        "DeepSeek",
        "Sugira nomes criativos para um evento de tecnologia.",
        Sensibilidade.PUBLICA,
        Risco.MEDIO,
    ),
]


def _seed_usuarios(db: Session) -> None:
    settings = get_settings()
    contas = [
        (settings.admin_email, "Administrador", settings.admin_password, Papel.ADMIN),
        ("analista@starkbank.local", "Analista de Segurança", "analista123", Papel.ANALISTA),
        ("auditor@starkbank.local", "Auditor (somente leitura)", "auditor123", Papel.LEITOR),
    ]
    for email, nome, senha, papel in contas:
        if not db.scalar(select(Usuario).where(Usuario.email == email)):
            db.add(Usuario(email=email, nome=nome, senha_hash=gerar_hash_senha(senha), papel=papel.value))


def _seed_eventos(db: Session, rng: random.Random, quantidade: int) -> None:
    agora = datetime.now(timezone.utc)
    nomes = [f[0] for f in FERRAMENTAS]
    for _ in range(quantidade):
        modelo, finalidade = rng.choice(MODELOS)
        texto = modelo.format(
            cpfs=cpfs(rng, rng.choice([3, 5, 12, 25])),
            cpf=gerar_cpf(rng),
            cnpj=gerar_cnpj(rng),
            cartao=rng.choice(CARTOES),
            email=f"{rng.choice(USUARIOS_CORPORATIVOS)}@cliente.com.br",
            aws="'AKIA" + "".join(rng.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567", k=16)) + "'",
            senha="'" + "".join(rng.choices("abcdefXYZ123!@", k=12)) + "'",
        )
        ferramenta = rng.choices(nomes, weights=PESOS_FERRAMENTA)[0]
        if rng.random() < 0.04:
            ferramenta = rng.choice(["NovaIA Free", "Poe", "You.com"])
        data_hora = agora - timedelta(days=rng.randint(0, 29), hours=rng.randint(0, 10), minutes=rng.randint(0, 59))
        registrar_evento(db, texto, ferramenta, rng.choice(USUARIOS_CORPORATIVOS), finalidade, data_hora)

    for alerta in db.scalars(select(Alerta)):
        idade = (agora - alerta.criado_em.replace(tzinfo=alerta.criado_em.tzinfo or timezone.utc)).days
        sorteio = rng.random()
        if idade > 7 and sorteio < 0.7:
            alerta.status = StatusAlerta.TRATADO.value
            alerta.responsavel = "analista@starkbank.local"
            alerta.observacao = "Usuário orientado e conteúdo removido da ferramenta."
        elif idade > 2 and sorteio < 0.4:
            alerta.status = StatusAlerta.EM_ANALISE.value
            alerta.responsavel = "analista@starkbank.local"
    db.commit()


def seed(db: Session, quantidade_eventos: int = 400) -> None:
    _seed_usuarios(db)
    if not db.scalar(select(func.count()).select_from(Ferramenta)):
        for nome, fornecedor, status, obs in FERRAMENTAS:
            db.add(Ferramenta(nome=nome, fornecedor=fornecedor, status=status.value, observacoes=obs))
    if not db.scalar(select(func.count()).select_from(TipoInformacao)):
        for nome, descricao in TIPOS:
            db.add(
                TipoInformacao(
                    nome=nome, descricao=descricao, classificacao_padrao=rules.SENSIBILIDADE_PADRAO[nome].value
                )
            )
    if not db.scalar(select(func.count()).select_from(CasoValidacao)):
        for descricao, ferramenta, texto, sens, risco in CASOS_VALIDACAO:
            db.add(
                CasoValidacao(
                    descricao=descricao,
                    ferramenta_nome=ferramenta,
                    texto_entrada=texto,
                    sensibilidade_esperada=sens.value,
                    risco_esperado=risco.value,
                )
            )
    db.commit()
    if quantidade_eventos and not db.scalar(select(func.count()).select_from(Evento)):
        _seed_eventos(db, random.Random(42), quantidade_eventos)
