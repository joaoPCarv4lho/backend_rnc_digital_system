# Mensagens de Commit Semânticas - RNC Digital System

> **Padrão:** Conventional Commits + Semantic Versioning
> **Data:** 2 de Dezembro de 2025

---

## 📋 Resumo das Alterações

Total de **9 commits semânticos** organizados por arquitetura (core → model → schema → repository → service → router → websocket → utils → server).

---

## 1. **INFRA: Configuração e Autenticação**

### Commit: `feat(core): add refresh token mechanism and logging setup`

**Escopo:** Core infrastructure - Configuration, Security, Logging
**Tipo:** `feat` (feature)

**Arquivos modificados:**
- `app/core/config.py`
- `app/core/security.py`
- `app/core/dependencies.py`
- `app/core/logging_config.py` (NEW)

**Descrição:**

Implementa mecanismo de refresh token com validade de 7 dias e centraliza configuração de logging em toda a aplicação.

**Detalhes:**
- ✨ Adiciona `REFRESH_TOKEN_EXPIRE_DAYS` (7 dias) e `REFRESH_SECRET_KEY` em Settings
- ✨ Implementa `create_refresh_token()` com suporte a expiração customizável
- ✨ Consolida papéis técnicos: `TECNICO_USINAGEM` + `TECNICO_FUNDICAO` → `TECNICO`
- ✨ Cria `app/core/logging_config.py` com `setup_logging()` centralizada
- 🔧 Melhora tratamento de exceções em `verify_token()` com logging explícito
- 🔧 Define níveis de logging por módulo (uvicorn=INFO, fastapi=DEBUG, websocket=DEBUG)

**Motivação:**
- Segurança: Tokens de acesso com vida curta, refresh com vida longa
- Manutenibilidade: Logging centralizado facilita debugging e monitoramento
- Simplificação: Um único role TECNICO reduz complexidade de permissões

---

## 2. **MODEL: Expansão do Workflow RNC**

### Commit: `refactor(model): expand RNC workflow with multi-stage process and analysis/rework tracking`

**Escopo:** Data models - RNC, User
**Tipo:** `refactor` (refactor)

**Arquivos modificados:**
- `app/model/rnc_model.py`
- `app/model/user_model.py`
- `app/model/__init__.py`

**Descrição:**

Transforma RNC de modelo simples (aberto/fechado) para processo multi-etapa com análise da qualidade e retrabalho técnico.

**Detalhes:**

**RNC Model Changes:**
- ✨ Novo enum `RNCCriticalLevel`: BAIXA, MEDIA, ALTA, CRITICA
- ✨ Expande `RNCCondition`: EM_ANALISE → AGUARDANDO_RETRABALHO → AGUARDANDO_VERIFICACAO → APROVADO/REFUGO
- 📝 Adiciona 15+ campos para análise de qualidade:
  - `root_cause`, `corrective_action`, `preventive_action`, `analysis_observations`
  - `estimated_rework_time`, `requires_external_support`, `quality_verified`
  - `analysis_date`, `analysis_user_id`
- 📝 Adiciona 5+ campos para retrabalho técnico:
  - `rework_description`, `actions_taken`, `materials_used`, `time_spent`
  - `rework_date`, `rework_user_id`, `rework_observations`
- 📝 Adiciona campos de closure:
  - `closing_notes`, `close_rnc`, `refused`, `closing_date`
- 🔗 Novos relacionamentos com User: `analysis_by`, `rework_by`
- 🎯 Métodos de instância:
  - `is_open()`, `is_closed()`, `is_critical()`
  - `has_analysis()`, `has_rework()`, `get_total_time_spent()`, `get_resolution_time_days()`
  - `__repr__()` para debug
- 🔧 Otimiza `generate_next_num_rnc()` com `func.max()` ao invés de ordenação completa
- 🔧 Usa `sa_column=Column(Text)` para campos de texto ilimitado

**User Model Changes:**
- ✨ Consolida roles: Remove TECNICO_USINAGEM e TECNICO_FUNDICAO → TECNICO
- 🔗 Atualiza relacionamentos: `rncs_responsible` → `analysis_rncs` + `rework_rncs`
- 📝 Agora rastreia RNCs por papel: `open_rncs`, `analysis_rncs`, `rework_rncs`, `rncs_closed`

**Motivação:**
- Suporta workflow completo: Abertura → Análise → Retrabalho → Fechamento
- Rastreabilidade: Registra quem fez cada etapa e quando
- Métricas: Permite calcular tempo de resolução e estatísticas por etapa

---

## 3. **SCHEMA: Separação de Responsabilidades**

### Commit: `refactor(schema): separate analysis, rework, and closure concerns with dedicated schemas`

**Escopo:** Pydantic validation schemas
**Tipo:** `refactor` (refactor)

**Arquivos modificados:**
- `app/schema/rnc_schema.py`
- `app/schema/__init__.py`

**Descrição:**

Divide RNCUpdate genérico em schemas específicos para cada etapa do workflow, habilitando validação e documentação precisas.

**Detalhes:**

**Novos Schemas:**
- ✨ `QualityAnalysis`: Para análise por qualidade
  - Campos obrigatórios: `root_cause` (min 20 chars)
  - Suporta fechamento imediato: `close_rnc`, `refused`
  - Documentação e exemplos JSON
- ✨ `TechnicianRework`: Para retrabalho técnico
  - Campos obrigatórios: `rework_description` (min 10), `actions_taken` (min 20)
  - Tempo gasto em minutos: `time_spent` (gt=0)
  - Exemplos com dados realistas
- ✨ `RNCClose`: Para fechamento manual
  - `closing_notes` obrigatório (min 20 chars)
  - Tipo de resolução documentado

**Schemas de Resposta:**
- ✨ `RNCListResponse`: Resposta paginada
  - `items`, `total`, `page`, `page_size`, `total_pages`
- ✨ `RNCReadSimple`: Para listagens
  - Informações essenciais: num_rnc, título, status, criticidade
- ✨ `RNCReadWithPart`: Com dados aninhados da peça
- ✨ `RNCStatistics`: Agregações
  - Totais por status/condição, tempo médio de resolução
  - Breakdown mensal, por status, por condição
  - Exemplo JSON com dados representativos

**Melhorias Gerais:**
- 🔧 Adiciona `Field()` com descrições detalhadas
- 🔧 Adiciona `json_schema_extra` com exemplos para OpenAPI
- 🔧 Valida níveis de criticidade com `@field_validator`
- 🔧 Todos com `Config.from_attributes = True` para SQLModel

**Motivação:**
- Validação forte: Cada etapa tem regras específicas
- API clara: Cliente sabe exatamente o que enviar
- Documentação: OpenAPI auto-gerado com exemplos

---

## 4. **REPOSITORY: Otimização de Queries**

### Commit: `refactor(repository): add pagination, eager loading, and new operation methods`

**Escopo:** Data access layer
**Tipo:** `refactor` (refactor)

**Arquivos modificados:**
- `app/repository/rnc_repository.py`

**Descrição:**

Transforma repository de métodos básicos para queries otimizadas com paginação, eager loading e operações específicas de workflow.

**Detalhes:**

**Utilitários:**
- ✨ `_get_current_utc_datetime()`: Retorna datetime UTC para consistency
- ✨ `_apply_eager_loading()`: Aplica selectinload em relacionamentos

**Métodos de Consulta (Novos):**
- ✨ `get_by_num(num_rnc, lock=False)`: Busca por número com bloqueio pessimista (FOR UPDATE)
- ✨ `search_rnc_opened_by_user()`: RNCs criados por usuário (limit/offset)
- ✨ `search_rnc_rework_by_user()`: RNCs retrabalhados (limit/offset)
- ✨ `search_rnc_by_analysis_user()`: RNCs analisados (limit/offset)
- ✨ `list_by_rework_status()`: Pendentes ou completados
- ✨ `list_by_analysis_status()`: Pendentes ou completados
- ✨ `list_all()`: Com filtros opcionais e paginação

**Métodos de Mutação (Refatorados):**
- ✨ `create_rnc()`: Validação de RNC ativo, UTC timezone
- ✨ `register_quality_analysis()`: Registra análise com transição de estado
  - Suporta fechamento como APROVADO ou REFUGO
  - Ou transição para AGUARDANDO_RETRABALHO
- ✨ `register_technician_rework()`: Registra retrabalho
  - Transição para AGUARDANDO_VERIFICACAO
- ✨ `close_rnc()`: Fechamento manual com notas

**Otimizações:**
- 🔧 Eager loading com selectinload() previne N+1 queries
- 🔧 Paginação (limit/offset) em todas as listas (padrão 100-1000)
- 🔧 Bloqueio pessimista em operações críticas
- 🔧 UTC timezone enforcement em todas as timestamps
- 🔧 Transações explícitas (commit/refresh)

**Motivação:**
- Performance: Eager loading reduz queries para DB
- Escalabilidade: Paginação permite grandes datasets
- Concorrência: FOR UPDATE previne race conditions em análise/retrabalho

---

## 5. **SERVICE: Camada de Lógica Assíncrona**

### Commit: `refactor(service): transform to async architecture with comprehensive validation and WebSocket broadcasts`

**Escopo:** Business logic layer
**Tipo:** `refactor` (refactor)

**Arquivos modificados:**
- `app/service/rnc_service.py`

**Descrição:**

Transforma serviço de síncrono para assíncrono com broadcasts WebSocket para atualizações real-time e validação role-based.

**Detalhes:**

**Métodos de Criação (Async):**
- ✨ `async create()`: Cria RNC com validação e broadcast `rnc_created`

**Métodos de Consulta (19+):**
- ✨ `get_rnc_by_num()`: Single RNC lookup
- ✨ `get_rncs_opened_by_user()`: RNCListResponse (paginado)
- ✨ `get_rncs_reworked_by_user()`: RNCListResponse (paginado)
- ✨ `get_rncs_analyzed_by_user()`: RNCListResponse (paginado)
- ✨ `get_filtered_rncs()`: Com validação de filtros
- ✨ `get_rncs_pending_rework()`: AGUARDANDO_RETRABALHO
- ✨ `get_rncs_with_completed_rework()`: AGUARDANDO_VERIFICACAO
- ✨ `get_rncs_pending_analysis()`: EM_ANALISE + AGUARDANDO_VERIFICACAO
- ✨ `get_rncs_with_completed_analysis()`: Analisados

**Métodos de Workflow (Async):**
- ✨ `async register_quality_analysis()`: Registra análise
  - Validações: RNC existe, não fechado, usuário tem permissão
  - Broadcasts: `rnc_closed` ou `rnc_analysis_completed`
- ✨ `async register_technician_rework()`: Registra retrabalho
  - Validações: RNC existe, tem análise prévia
  - Broadcast: `rnc_rework_completed`
- ✨ `async close_rnc()`: Fechamento manual
  - Broadcast: `rnc_closed`

**Estatísticas:**
- ✨ `get_statistics()`: Retorna RNCStatistics
  - Contadores: total, aberto, fechado, aprovado, refugo
  - Tempo médio de resolução em dias
  - Breakdown mensal, por status, por condição
  - Usa `Counter` da stdlib para agregação

**Validação (5 métodos auxiliares):**
- ✨ `_validate_filters()`: Valida status/condition
- ✨ `_validate_critical_level()`: Valida BAIXA/MEDIA/ALTA/CRITICA
- ✨ `_user_can_analyze()`: QUALIDADE ou ENGENHARIA
- ✨ `_user_can_rework()`: TECNICO
- ✨ `_user_can_close()`: QUALIDADE ou ENGENHARIA

**Logging:**
- 🔧 Remove logs de debug antigos (REGISTROS DE NAO CONFORMIDADES!!!)
- 🔧 Adiciona logging estruturado em cada etapa
- 🔧 Logging de erros com contexto (usuário, RNC, operação)

**Motivação:**
- Async: Não bloqueia durante I/O (WebSocket, DB)
- Real-time: Broadcasts atualizam UI clientes instantaneamente
- Segurança: Validação role-based em cada operação
- Observabilidade: Logging detalhado para troubleshooting

---

## 6. **ROUTER: Endpoints Reestruturados**

### Commit: `refactor(router): restructure RNC endpoints with analysis/rework workflow and add refresh token`

**Escopo:** HTTP API layer
**Tipo:** `refactor` (refactor)

**Arquivos modificados:**
- `app/router/auth_router.py`
- `app/router/rnc_router.py`
- `app/router/part_router.py`

**Descrição:**

Reestrutura endpoints RNC para suportar novo workflow, adiciona refresh token, e consolida referencias a roles.

**Detalhes:**

**Auth Router Mudanças:**
- ✨ Adiciona `POST /api/auth/refresh`:
  - Extrai refresh_token do HttpOnly cookie
  - Decodifica com REFRESH_SECRET_KEY
  - Retorna novo access_token
- 🔧 Login agora retorna refresh_token em HttpOnly cookie
  - `httponly=True, secure=True, samesite="none"`
  - Validade: 7 dias
- 🧹 Remove logs de debug antigos

**RNC Router Refatorações:**
- ✨ `POST /api/rnc/create_rnc`: Retorna RNCReadSimple (não full RNCRead)
- ✨ `GET /api/rnc/list_rncs`: Retorna RNCListResponse (paginado)
- ✨ `GET /api/rnc/list/to_be_reworked` (NEW): AGUARDANDO_RETRABALHO
- ✨ `GET /api/rnc/list/open/user` (RENAMED): Antes era /list_user_rncs
- ✨ `GET /api/rnc/list/analysis/user` (NEW): RNCs analisados por usuário
- ✨ `GET /api/rnc/list/rework/user` (NEW): RNCs retrabalhados por usuário
- ✨ `GET /api/rnc/statistics/` (NEW): RNCStatistics para ADMIN
- ✨ `PATCH /api/rnc/analysis/{num_rnc}` (NEW): Registra análise da qualidade
  - Request: QualityAnalysis
  - Response: RNCRead completo
- ✨ `PATCH /api/rnc/rework/{num_rnc}` (NEW): Registra retrabalho
  - Request: TechnicianRework
  - Response: RNCRead completo
- 🗑️ Remove `/api/rnc/update_rnc` (obsoleto)

**Part Router:**
- 🔧 Atualiza UserRole: `TECNICO_FUNDICAO` → `TECNICO`

**Permissões Atualizadas:**
- ✨ Todos os endpoints agora usam novo role `TECNICO`
- ✨ Análise requerida: QUALIDADE ou ENGENHARIA
- ✨ Retrabalho requerida: TECNICO
- ✨ Estatísticas requerida: ADMIN only

**Motivação:**
- Semantic paths: /list/open/user, /list/analysis/user, /list/rework/user
- Endpoints específicos: Cada etapa do workflow tem endpoint dedicado
- Type safety: Schemas separados validam dados por etapa
- Async: Todos os endpoints async para não bloquear

---

## 7. **WEBSOCKET: Comunicação Real-Time (NEW)**

### Commit: `feat(websocket): implement role-based WebSocket manager with token authentication`

**Escopo:** Real-time communication layer (NEW)
**Tipo:** `feat` (feature)

**Arquivos modificados:**
- `app/websocket/manager.py` (NEW)
- `app/websocket/route.py` (NEW)

**Descrição:**

Implementa camada WebSocket para broadcast de eventos RNC em tempo real, com autenticação JWT e groups por role.

**Detalhes:**

**ConnectionManager (`app/websocket/manager.py`):**
- ✨ Gerencia conexões ativas e agrupa por role
- ✨ Mapa de conexões: `active_connections` (Set), `user_map` (Dict), `ws_to_user` (Dict)
- ✨ Groups por role: admin, qualidade, engenharia, operador, tecnico
- 🔗 `async connect()`: Valida JWT, adiciona a groups, retorna user_data
- 🔗 `_decode_token()`: Extrai user_id e role do token
- 📢 `async broadcast_all()`: Envia evento para todos os clientes
- 📢 `async broadcast_group()`: Envia evento para grupo específico
- 🔓 `disconnect()`: Limpa todas as referências

**WebSocket Endpoint (`app/websocket/route.py`):**
- ✨ Endpoint: `/ws/rncs` (ou `/ws/rncs?token=<JWT>`)
- 🔐 Validação de origem (whitelist localhost:5173)
- 🔐 Validação de token via query param
- 💓 Suporte a ping/pong para heartbeat
- 📝 Logging detalhado para troubleshooting
- 🛡️ Tratamento de exceções com códigos WebSocket:
  - WS_1008_POLICY_VIOLATION: Origin/token inválido
  - WS_1011_INTERNAL_ERROR: Erro interno

**Eventos Broadcast:**
- 📢 `rnc_created`: Novo RNC criado
- 📢 `rnc_analysis_completed`: Análise registrada
- 📢 `rnc_rework_completed`: Retrabalho registrado
- 📢 `rnc_closed`: RNC fechado
- 📢 `rnc_updated`: RNC atualizado

**Payload Format:**
```json
{
  "type": "<event_name>",
  "payload": {RNC data serialized}
}
```

**Motivação:**
- Real-time: Clientes recebem atualizações instantaneamente
- Eficiente: Broadcasts seletivos por role reduzem tráfego
- Seguro: Autenticação JWT valida cada conexão
- Observável: Logging detalhado de conexões/desconexões

---

## 8. **UTILS: Utilitários Serializáveis (NEW)**

### Commit: `feat(utils): add RNC serialization helper for WebSocket broadcasts`

**Escopo:** Utility functions (NEW)
**Tipo:** `feat` (feature)

**Arquivos modificados:**
- `app/utils/serializable.py` (NEW)

**Descrição:**

Utilitário para converter RNC model em dicionário JSON-serializável para broadcasts WebSocket.

**Detalhes:**

**Função `serialize_rnc()`:**
- 🔄 Converte modelo RNC para dict
- 📅 Converte datetimes para ISO format strings
- 📌 Inclui flag `close_rnc` = `is_closed()`
- ✅ Garante compatibilidade JSON para WebSocket

**Uso:**
```python
serialized = serialize_rnc(rnc_model)
await manager.broadcast_all("rnc_created", serialized)
```

**Motivação:**
- Consistência: Um único lugar para serialização
- Manutenibilidade: Fácil atualizar formato
- Performance: Pré-serialização antes de broadcast

---

## 9. **SERVER: Configuração Principal**

### Commit: `feat(server): add logging setup, exception handler, WebSocket support, and API path prefixes`

**Escopo:** Main application file
**Tipo:** `feat` (feature)

**Arquivos modificados:**
- `server.py`

**Descrição:**

Configura logging centralizado, exception handler customizado, WebSocket router, e padroniza prefixos /api.

**Detalhes:**

**Inicialização:**
- ✨ Chama `setup_logging()` antes de criar app
  - Logging DEBUG para app, INFO para uvicorn, DEBUG para WebSocket

**Exception Handling:**
- ✨ Exception handler customizado para HTTPException
  - Retorna `{"error": detail}` em vez de padrão FastAPI

**Middleware CORS:**
- 🔧 Allow origins: localhost:5173, 127.0.0.1:5173
- 🔧 Allow credentials: True (para cookies)

**Route Registration:**
- 🔄 Prefixos atualizados:
  - `/auth` → `/api/auth`
  - `/user` → `/api/user`
  - `/rnc` → `/api/rnc`
  - `/part` → `/api/part`
- ✨ WebSocket router em `/ws` (separado do /api)

**Motivação:**
- Consistência: Todos endpoints sob /api exceto WebSocket
- Logging: Centralizado e configurável
- Observabilidade: Tratamento consistente de erros

---

## 📊 Resumo Estatístico

| Métrica | Valores |
|---------|---------|
| **Commits Semânticos** | 9 |
| **Arquivos Modificados** | 16 |
| **Arquivos Criados** | 3 |
| **Linhas Adicionadas** | ~1500+ |
| **Enums Novos** | 1 (RNCCriticalLevel) |
| **Campos RNC** | +20 campos |
| **Métodos RNC** | +7 métodos |
| **Query Methods** | +10 novos métodos |
| **Endpoints Novos** | 7 |
| **Schemas Novos** | 6 |
| **Roles Consolidados** | 2 → 1 (TECNICO) |

---

## 🔄 Ordem Recomendada de Commit

1. ✅ **Core Infra** - Configuração base
2. ✅ **Models** - Estrutura de dados
3. ✅ **Schemas** - Validação
4. ✅ **Repository** - Acesso a dados
5. ✅ **Service** - Lógica de negócio
6. ✅ **Routers** - HTTP endpoints
7. ✅ **WebSocket** - Real-time
8. ✅ **Utils** - Suporte
9. ✅ **Server** - Configuração final

---

## 🚀 Próximos Passos

- [ ] Executar testes unitários para cada camada
- [ ] Testar workflow completo: abrir → analisar → retrabalhar → fechar
- [ ] Testar WebSocket com múltiplos clientes
- [ ] Validar token refresh flow
- [ ] Performance testing com dataset grande
- [ ] Documentação de API (OpenAPI/Swagger)

---

**Data de Compilação:** 2 de Dezembro de 2025  
**Preparado para:** git commit workflow  
**Desenvolvedor:** Backend RNC Digital System Team
