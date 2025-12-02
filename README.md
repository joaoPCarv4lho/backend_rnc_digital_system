# 🏭 RNC Digital System

O **RNC Digital System** é uma plataforma corporativa desenvolvida para digitalizar e otimizar o gerenciamento de **Registros de Não Conformidade (RNCs)** em indústrias do setor metalúrgico. A solução substitui processos manuais baseados em papel por uma arquitetura moderna e confiável, garantindo velocidade, integridade e rastreabilidade completa dos dados.

---

## 📌 Visão Geral

- **Objetivo:** Digitalizar o processo de controle e tratamento de RNCs.
- **Problema que resolve:**
  - Elimina descentralização dos dados.
  - Aumenta a confiabilidade das auditorias.
  - Reduz perdas de informações durante análises.
  - Melhora o tempo de reação e decisão da área de qualidade.
- **Público-alvo:** indústrias metalúrgicas com necessidade de rastreabilidade e padronização.

---

# 🏗️ Arquitetura do Sistema

O sistema utiliza uma arquitetura modular, com foco em escalabilidade, segurança e clareza na separação das responsabilidades.


## 🔙 Backend

**Tecnologias:**
- FastAPI  
- SQLAlchemy  
- python-jose (JWT)  
- bcrypt  
- Uvicorn  
- psycopg2  
- PostgreSQL  

**Camadas:**

| Camada        | Responsabilidade                                             |
|---------------|--------------------------------------------------------------|
| `model`       | Mapeamento ORM das tabelas                                   |
| `schema`      | Tipagem e validação com Pydantic                             |
| `router`      | Definição dos endpoints                                      |
| `service`     | Regras de negócio e fluxo principal                          |
| `repository`  | Acesso ao banco e queries                                    |
| `core`        | Configurações, autenticação, conexões e inicialização        |
| `utils`       | Funções auxiliares                                           |
| `websocket`   | Gerenciamento da comunicação em tempo real                   |

---

## ☁️ Infraestrutura

- **Containerização:** Docker  
- **Hospedagem:** AWS  
- **Comunicação:** REST + WebSocket  

---

# 📋 Funcionalidades Principais

- Cadastro, atualização e rastreamento completo de RNCs  
- Autenticação segura baseada em JWT  
- Criptografia de senha com bcrypt  
- Dashboard gerencial para administradores  
- Comunicação em tempo real para etapas do ciclo do RNC  
- Controle de permissões baseado em papéis (RBAC)  

---

# 🧩 Regras de Negócio

### 🔄 Fluxo do RNC

1. **Operador** cria o RNC  
2. **QA** realiza análise e apontamento  
3. **Técnico** executa o retrabalho  
4. **QA** valida o retrabalho  
5. Caso esteja conforme → **RNC aprovado**  
6. Caso contrário → retorna ao retrabalho ou é **refugado**  

---

### 🔐 Permissões por tipo de usuário

| Usuário       | Permissões |
|---------------|------------|
| **Operador**  | Criar RNCs |
| **Técnico**   | Realizar retrabalho |
| **QA / Eng.** | Analisar, aprovar, reprovar e fechar RNCs |
| **Admin**     | Dashboard, estatísticas e visão ampla do sistema |

---

# 🔐 Segurança dos Dados

O sistema foi projetado com políticas rígidas de segurança:

- Autenticação com **JWT**
- Senhas criptografadas com **bcrypt**
- RBAC — controle de acesso por papéis
- Logs e rastreabilidade para auditoria
- Separação clara entre camadas de negócio, persistência e API

---

# 🛠️ Stack Técnica Completa

### **Backend**
- Python
- FastAPI
- SQLAlchemy
- python-jose
- bcrypt
- psycopg2
- Uvicorn  

### **Banco**
- PostgreSQL  

---

# ▶️ Como Rodar o Projeto

```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>

# 2. Acessar o diretório
cd backend_rnc_digital_system


# 3. Instalar dependências
pip install -r requirements.txt

# 4. Ativar o ambiente virtual
source .venv/bin/activate

# 5. Executar o servidor
uvicorn server:app --reload
```

(O frontend pode ser executado conforme documentado no diretório correspondente.)

# 📈 Benefícios para o Negócio

A adoção do RNC Digital System gera impacto direto nos indicadores de qualidade e eficiência operacional:

## Antes do sistema

- Processos manuais demorados

- Formularização em papel sujeita a extravios

- Dificuldade para rastrear informações

- Erros frequentes por falta de integridade dos dados

- Tempo elevado entre criação e análise do RNC

## Após implementação

- Centralização total dos dados

- Rastreabilidade completa do ciclo de vida de cada RNC

- Redução de erros durante análises

- Agilidade na tomada de decisão

- Melhor visibilidade para auditorias internas e externas

- Economia significativa de tempo no setor de qualidade

- Redução na ocorrência de peças não conformes por falhas de processo

# 📘 Conclusão

O RNC Digital System é uma solução moderna, segura e escalável para transformar o processo de gestão de RNCs. Ele promove maior rastreabilidade, agiliza operações de qualidade e aumenta a confiabilidade das auditorias, contribuindo diretamente para a eficiência e competitividade da indústria metalúrgica.
