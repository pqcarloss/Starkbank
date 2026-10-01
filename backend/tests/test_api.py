from fastapi.testclient import TestClient


def test_login_invalido(client: TestClient) -> None:
    r = client.post("/api/auth/login", data={"username": "admin@starkbank.local", "password": "errada"})
    assert r.status_code == 401


def test_rotas_exigem_token(client: TestClient) -> None:
    assert client.get("/api/eventos").status_code == 401
    assert client.get("/api/dashboard/resumo", headers={"Authorization": "Bearer invalido"}).status_code == 401


def test_me(client: TestClient, admin: dict[str, str]) -> None:
    r = client.get("/api/auth/me", headers=admin)
    assert r.json()["papel"] == "admin"


def test_registrar_evento_gera_alerta_e_pseudonimiza(client: TestClient, admin: dict[str, str]) -> None:
    r = client.post(
        "/api/eventos",
        headers=admin,
        json={"texto": "Clientes: 529.982.247-25", "ferramenta": "DeepSeek", "id_usuario": "maria.lima"},
    )
    assert r.status_code == 201, r.text
    evento = r.json()
    assert evento["risco"] == "Crítico"
    assert evento["id_usuario"].startswith("USR-") and "maria" not in evento["id_usuario"]
    assert evento["alerta"]["status"] == "Aberto"

    alertas = client.get("/api/alertas", headers=admin, params={"status": "Aberto"}).json()
    alerta = next(a for a in alertas["itens"] if a["evento_id"] == evento["id"])
    r = client.patch(f"/api/alertas/{alerta['id']}", headers=admin, json={"status": "Em análise"})
    assert r.json()["status"] == "Em análise"
    assert r.json()["responsavel"] == "admin@starkbank.local"


def test_leitor_nao_altera(client: TestClient, leitor: dict[str, str]) -> None:
    r = client.post("/api/eventos", headers=leitor, json={"texto": "x", "ferramenta": "Claude", "id_usuario": "a"})
    assert r.status_code == 403
    r = client.post("/api/ferramentas", headers=leitor, json={"nome": "X", "status": "Aprovada"})
    assert r.status_code == 403


def test_classificar_nao_persiste(client: TestClient, admin: dict[str, str]) -> None:
    antes = client.get("/api/eventos", headers=admin).json()["total"]
    r = client.post("/api/classificar", headers=admin, json={"texto": "senha: abc12345", "ferramenta": "Claude"})
    assert r.json()["risco"] == "Crítico"
    assert client.get("/api/eventos", headers=admin).json()["total"] == antes


def test_casos_validacao_todos_aprovados(client: TestClient, admin: dict[str, str]) -> None:
    r = client.post("/api/casos-validacao/executar", headers=admin).json()
    reprovados = [x["caso"]["descricao"] for x in r["resultados"] if not x["aprovado"]]
    assert r["total"] == 10
    assert reprovados == []


def test_dashboard(client: TestClient, admin: dict[str, str]) -> None:
    r = client.get("/api/dashboard/resumo", headers=admin)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["total_eventos"] == 40
    assert sum(c["total"] for c in d["por_risco"]) == 40
    assert len(d["serie_diaria"]) == 30


def test_alterar_classificacao_padrao_afeta_risco(client: TestClient, admin: dict[str, str]) -> None:
    tipos = client.get("/api/tipos-informacao", headers=admin).json()
    contato = next(t for t in tipos if t["nome"] == "Dados de contato")
    client.patch(f"/api/tipos-informacao/{contato['id']}", headers=admin, json={"classificacao_padrao": "Crítica"})
    r = client.post("/api/classificar", headers=admin, json={"texto": "a@b.com", "ferramenta": "ChatGPT Enterprise"})
    assert r.json()["sensibilidade"] == "Crítica"
