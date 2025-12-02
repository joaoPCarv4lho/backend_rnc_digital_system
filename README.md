RNC Digital System

O RNC Digital System é uma solução corporativa desenvolvida para digitalizar e otimizar o gerenciamento de Registros de Não Conformidade (RNCs) em indústrias do setor metalúrgico. O sistema moderniza processos antes realizados em papel, garantindo mais rapidez, rastreabilidade, integridade dos dados e apoio ao setor de qualidade.

📌 Visão Geral

Objetivo: substituir o fluxo manual de RNCs por uma plataforma digital robusta e confiável.

Problema que resolve:

Reduz a descentralização e perda de informações.

Aumenta a confiabilidade das auditorias.

Melhora o tempo de análise e tomada de decisão.

Público-alvo: indústrias metalúrgicas que buscam digitalização e eficiência no controle de qualidade.

🏗️ Arquitetura do Sistema

O sistema foi projetado com uma arquitetura modular, segura e escalável, suportando tanto operações síncronas (API REST) quanto comunicação em tempo real (WebSocket).

Backend

Framework: FastAPI

ORM: SQLAlchemy

Autenticação: JWT (python-jose)

Criptografia de senha: bcrypt

Servidor: Uvicorn

Banco de Dados: PostgreSQL

Driver: psycopg2


Camadas da aplicação

O backend segue uma estrutura clara e separada em responsabilidades:

Camada	Responsabilidade
model	Mapeamento das tabelas (ORM).
schema	Validação e tipagem dos dados (Pydantic).
router	Definição das rotas e endpoints da API.
service	Regras de negócio e fluxo de operações.
repository	Acesso ao banco de dados e queries.
core	Configurações, autenticação e dependências.
utils	Funções auxiliares.
websocket	Gerenciamento de eventos em tempo real.


🚀 Infraestrutura

Containerização: Docker

Hospedagem planejada: AWS

Implementação preparada para serviços como ECS/EKS, RDS, EC2 ou Lightsail.

Comunicação:

REST para operações tradicionais.

WebSocket para eventos em tempo real (criação, atualização e fechamento de RNCs).

📋 Funcionalidades Principais

Cadastro e atualização de RNCs

Gestão completa do ciclo de vida do RNC

Autenticação segura baseada em JWT

Hash seguro de senha com bcrypt

Atualizações em tempo real via WebSocket

Diferentes perfis e permissões por usuário

Dashboard para administradores


🧩 Regras de Negócio

O ciclo do RNC segue fielmente a prática das indústrias metalúrgicas:

Fluxo do ciclo de vida

Operador cria o RNC

QA analisa e realiza apontamento

Técnico executa o retrabalho

QA valida se o retrabalho resolveu a não conformidade

Se conforme → RNC é aprovado

Se não conforme → retorna ao retrabalho ou é classificado como refugo

Permissões
Usuário	Permissões
Operador	Criar RNCs
Técnico	Executar retrabalho e registrar ações
QA / Engenharia	Aprovar, reprovar, validar e fechar RNCs
Administrador	Acesso a dashboard, estatísticas e visão geral
🔐 Segurança dos Dados

A arquitetura prioriza confidencialidade, integridade e rastreabilidade.

Medidas implementadas:

Autenticação com JWT Tokens

Criptografia de senha com bcrypt

Política de acesso baseada em papéis (RBAC)

Comunicação estruturada entre cliente e servidor

Separação clara entre regras de negócio e repositórios

Logs detalhados e eventos via WebSocket para auditoria

🛠️ Stack Técnica Completa
Backend

Python

FastAPI

SQLAlchemy

python-jose

bcrypt

psycopg2

Uvicorn

Frontend

TypeScript

React

Vite

Axios

Tailwind CSS

Lucide-react

Framer-motion

Immer

Banco

PostgreSQL

▶️ Como Rodar o Projeto
# 1. Clonar o repositório
git clone <url-do-repositorio>

# 2. Acessar o diretório
cd rnc-digital-system

Backend
# 3. Instalar dependências
pip install -r requirements.txt

# 4. Ativar o ambiente virtual
source .venv/bin/activate

# 5. Executar o servidor
uvicorn server:app --reload


(O frontend pode ser executado conforme documentado no diretório correspondente, caso exista.)

📈 Benefícios para o Negócio

A adoção do RNC Digital System gera impacto direto nos indicadores de qualidade e eficiência operacional:

Antes do sistema

Processos manuais demorados

Formularização em papel sujeita a extravios

Dificuldade para rastrear informações

Erros frequentes por falta de integridade dos dados

Tempo elevado entre criação e análise do RNC

Após implementação

Centralização total dos dados

Rastreabilidade completa do ciclo de vida de cada RNC

Redução de erros durante análises

Agilidade na tomada de decisão

Melhor visibilidade para auditorias internas e externas

Economia significativa de tempo no setor de qualidade

Redução na ocorrência de peças não conformes por falhas de processo

📘 Conclusão

O RNC Digital System é uma solução moderna, segura e escalável para transformar o processo de gestão de RNCs. Ele promove maior rastreabilidade, agiliza operações de qualidade e aumenta a confiabilidade das auditorias, contribuindo diretamente para a eficiência e competitividade da indústria metalúrgica.
