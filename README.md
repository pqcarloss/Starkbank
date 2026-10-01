# Starkbank DLP — Governança de Uso de IA

Plataforma para monitorar o uso corporativo de ferramentas de IA: classifica o conteúdo enviado (DLP), calcula risco, gera alertas e apresenta um dashboard operacional. Modelo de dados derivado de `docs/dicionario_dados.csv`.

| Camada | Tecnologia |
|---|---|
| Frontend | Next.js 15 / React 19 / TypeScript / Tailwind / Chart.js |
| Backend | FastAPI / SQLAlchemy 2 / PyJWT / bcrypt |
| Banco | PostgreSQL 16 |
| Autenticação | JWT (OAuth2 password flow) — preparado para SSO/OAuth2 |
| Classificação | Regras determinísticas — preparado para NLP/LLM |

## Execução rápida (Docker Compose)

```bash
cp .env.example .env   # ajuste JWT_SECRET, PSEUDONYMIZATION_KEY e ADMIN_PASSWORD
docker compose up -d --build
```

- Frontend: http://localhost:3000
- API / Swagger: http://localhost:8000/docs

Usuários de desenvolvimento (criados pelo seed, junto com 400 eventos fictícios):

| Papel | E-mail | Senha |
|---|---|---|
| admin | admin@starkbank.local | admin123 |
| analista | analista@starkbank.local | analista123 |
| leitor | auditor@starkbank.local | auditor123 |

Defina `SEED_ON_STARTUP=false` e troque todos os segredos em produção.

## Desenvolvimento local

```bash
# Banco
docker compose up -d db

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload            # http://localhost:8000
pytest && ruff check . && ruff format --check .

# Frontend
cd frontend
npm ci
npm run dev                              # http://localhost:3000 (proxy /api -> BACKEND_URL)
npm run lint && npx tsc --noEmit && npm run build
```

## Funcionalidades

- **Dashboard** (Chart.js): KPIs, eventos por risco/sensibilidade/ferramenta/tipo, série temporal, alertas por status.
- **Eventos de uso de IA**: filtros, paginação e evidências mascaradas. Usuário pseudonimizado via HMAC-SHA256 (`USR-xxxxxxxxxx`); o conteúdo original não é persistido (apenas hash SHA-256 e tamanho).
- **Alertas**: gerados automaticamente para risco Alto/Crítico; workflow Aberto → Em análise → Tratado com responsável e comentário.
- **Classificar**: análise DLP sem persistência ou registro do evento.
- **Ferramentas de IA**: inventário com status Aprovada / Aprovada condicional / Não aprovada.
- **Tipos de informação**: classificação padrão (sensibilidade) configurável.
- **Casos de validação**: resultado esperado x obtido para regressão das regras.
- **Perfis**: `admin` (tudo), `analista` (eventos e alertas), `leitor` (somente leitura).

## Motor DLP (regras determinísticas)

`backend/app/classification/rules.py` detecta CPF/CNPJ (com dígito verificador), cartões (Luhn), agência/conta, chaves AWS, chaves privadas, senhas/tokens/API keys, JWT/Bearer, e-mails, telefones, código-fonte e termos financeiros, estratégicos, pessoais e internos. Prevalece o tipo de maior sensibilidade detectado.

`backend/app/classification/risk.py` combina sensibilidade × status da ferramenta × volume de ocorrências. Ferramenta fora do inventário é tratada como não aprovada (shadow AI).

## Endpoints principais

```
POST /api/auth/login              GET  /api/auth/me
POST /api/classificar             GET|POST /api/eventos
GET|PATCH /api/alertas            GET|POST|PATCH /api/ferramentas
GET|POST|PATCH /api/tipos-informacao
GET|POST|DELETE /api/casos-validacao   POST /api/casos-validacao/executar
GET  /api/dashboard/resumo        GET  /api/health
```

## Evolução

### SSO / OAuth2
`app/security.py` centraliza emissão e validação do token (`get_usuario_atual`). Para SSO, adicionar uma rota de callback OIDC (Entra ID, Okta, Google) que valide o `id_token` do provedor, localize/provisione o `Usuario` e emita o mesmo JWT interno — as rotas e o frontend não mudam. O botão "Entrar com SSO" na tela de login já está reservado.

### NLP / LLM
Classificadores implementam o protocolo `Classificador` (`app/classification/base.py`) e são selecionados por `CLASSIFIER_BACKEND` em `app/classification/factory.py`. Um backend `llm` ou `hibrido` pode reaproveitar as regras como primeira camada (alta precisão para padrões estruturados) e usar NLP/LLM para contexto semântico; os casos de validação servem como conjunto de regressão para comparar backends.
