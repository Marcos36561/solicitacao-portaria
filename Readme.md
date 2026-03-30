# 🏢 Solicitações Portaria

Sistema web para gerenciamento de solicitações de portaria em condomínios. Permite cadastrar e acompanhar visitantes, prestadores de serviço, corretores e convidados de festa, com controle de status, anexos e filtro por condomínio.

![Screenshot do sistema](docs/screenshot.png)

---

## ✨ Funcionalidades

- Cadastro de solicitações com os tipos: **Visitante**, **Corretor**, **Prestador de Serviço** e **Convidado**
- Vinculação de solicitações a condomínios cadastrados
- Controle de status: `pendente`, `confirmado` e `cancelado`
- Anexo de imagens e documentos PDF
- Filtro de solicitações por condomínio
- Paginação de resultados
- Edição e exclusão de solicitações

---

## 🛠️ Tecnologias

**Backend**
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Migrate (Alembic)
- PostgreSQL

**Frontend**
- HTML, CSS e JavaScript

---

## 📁 Estrutura do Projeto

```
.
├── backend/
│   ├── models/         # Modelos do banco de dados
│   ├── routes/         # Endpoints da API REST
│   ├── utils/          # Funções auxiliares
│   ├── migrations/     # Migrações do banco (Alembic)
│   ├── uploads/        # Arquivos enviados pelos usuários
│   ├── app.py          # Aplicação Flask
│   ├── config.py       # Configurações da aplicação
│   ├── extensions.py   # Inicialização das extensões
│   └── wsgi.py         # Ponto de entrada para produção
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── .env.example
├── requirements.txt
└── run.py              # Ponto de entrada para desenvolvimento
```

---

## 🚀 Como rodar localmente

### Pré-requisitos

- Python 3.10+
- PostgreSQL instalado e rodando

### 1. Clone o repositório

```bash
git clone https://github.com/Marcos36561/solicitacoes-portaria.git
cd solicitacoes-portaria
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com as credenciais do seu banco de dados:

```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
```

### 5. Crie o banco de dados e rode as migrações

```bash
flask db upgrade
```

### 6. Inicie o servidor

```bash
python run.py
```

O backend estará disponível em `http://localhost:5000`.

---

## 🔌 Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/solicitacoes` | Lista todas as solicitações |
| POST | `/api/solicitacoes` | Cria uma nova solicitação |
| PUT | `/api/solicitacoes/<id>` | Atualiza uma solicitação |
| DELETE | `/api/solicitacoes/<id>` | Remove uma solicitação |
| GET | `/api/condominios` | Lista os condomínios |
| POST | `/api/condominios` | Cadastra um condomínio |
| POST | `/api/uploads` | Faz upload de arquivo |

---

## 📌 Melhorias futuras

- [ ] Autenticação de usuários
- [ ] Painel administrativo por condomínio
- [ ] Notificações por e-mail ao confirmar solicitação
- [ ] Deploy em nuvem

---

## 👨‍💻 Autor

Feito por **Marcos Ribeiro** — [LinkedIn](https://linkedin.com/in/marcos-ribeiro-84b566194) · [GitHub](https://github.com/Marcos36561)