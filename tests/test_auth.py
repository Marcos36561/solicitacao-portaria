from werkzeug.security import generate_password_hash

from backend.extensions import db
from backend.models import Usuario


def criar_usuario(email="admin@email.com", senha="123456", nome="Admin"):
    usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=generate_password_hash(senha),
        is_admin=True,
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def test_login_sucesso(client):
    criar_usuario(email="admin@email.com", senha="123456", nome="Admin")

    response = client.post(
        "/usuarios/login",
        json={"email": "admin@email.com", "senha": "123456"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert "token" in payload
    assert "usuario" in payload
    assert payload["usuario"]["email"] == "admin@email.com"


def test_login_senha_invalida(client):
    criar_usuario(email="admin@email.com", senha="123456", nome="Admin")

    response = client.post(
        "/usuarios/login",
        json={"email": "admin@email.com", "senha": "senha_errada"},
    )

    assert response.status_code == 401
    payload = response.get_json()
    assert "Email ou senha inválidos" in payload["error"]


def test_rota_protegida_sem_token(client):
    response = client.get("/solicitacoes")

    assert response.status_code == 401
    payload = response.get_json()
    assert payload["error"] == "Token ausente"


def test_rota_protegida_com_token_valido(client):
    usuario = criar_usuario(email="teste@email.com", senha="abc123", nome="Teste")

    login_response = client.post(
        "/usuarios/login",
        json={"email": "teste@email.com", "senha": "abc123"},
    )

    token = login_response.get_json()["token"]

    response = client.get(
        "/solicitacoes",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in (200, 404)
    # 200 pode acontecer se houver solicitações no banco
    # 404 pode acontecer se não houver nenhuma, conforme a rota
    # então aqui o mais importante é validar a autenticação
    if response.status_code == 200:
        assert isinstance(response.get_json(), list)
    elif response.status_code == 404:
        payload = response.get_json()
        assert "Nenhuma solicitação encontrada" in payload["message"]


def test_rota_protegida_com_token_invalido(client):
    response = client.get(
        "/solicitacoes",
        headers={"Authorization": "Bearer token_invalido"},
    )

    assert response.status_code == 401
    payload = response.get_json()
    assert "Token inválido" in payload["error"]