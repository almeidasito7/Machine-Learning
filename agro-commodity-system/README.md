# AgroAI Commodities — Sistema de Gerenciamento com IA

Sistema completo de gerenciamento de commodities agrícolas com IA integrada via **LangChain4j** e workflow estilo **LangGraph**.

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                     Angular Frontend                         │
│   Dashboard │ Commodity List │ Detail + Charts │ AI Chat     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP / REST
┌──────────────────────▼──────────────────────────────────────┐
│               Spring Boot 3.2 (Java 21)                      │
│   CommodityController │ AIController │ WebSocket             │
│                                                              │
│   ┌──────────────────────────────────────────────────────┐  │
│   │            LangGraph Workflow (Custom)                │  │
│   │                                                       │  │
│   │  [START]                                              │  │
│   │     │                                                 │  │
│   │  [dataCollectionNode]  ← coleta dados de mercado      │  │
│   │     │                                                 │  │
│   │  [marketAnalysisNode]  ← LLM análise de mercado       │  │
│   │     │                                                 │  │
│   │  [riskAssessmentNode]  ← LLM avaliação de riscos      │  │
│   │     │                                                 │  │
│   │  [recommendationNode]  ← síntese + recomendação       │  │
│   │     │                                                 │  │
│   │  [END]                                                │  │
│   └──────────────────────────────────────────────────────┘  │
│                                                              │
│   LangChain4j ─────────────────────► OpenAI GPT-4o-mini     │
│   H2 Database (dev) / PostgreSQL (prod)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Stack Tecnológica

| Camada      | Tecnologia                            |
|-------------|---------------------------------------|
| Frontend    | Angular 17 + Angular Material + Chart.js |
| Backend     | Java 21 + Spring Boot 3.2             |
| IA          | LangChain4j 0.31 + LangGraph (custom) |
| LLM         | OpenAI GPT-4o-mini                    |
| Banco       | H2 (dev), PostgreSQL (prod)           |
| Container   | Docker + Docker Compose               |

---

## Commodities Suportadas

- **Grãos**: Soja, Milho, Trigo, Arroz
- **Café**: Arábica, Robusta
- **Fibras**: Algodão
- **Açúcar e Álcool**: Açúcar Cristal, Etanol
- **Carnes**: Boi Gordo, Frango, Suínos

---

## Como Executar

### Pré-requisitos
- Java 21+
- Node.js 20+
- Maven 3.9+

### Backend

```bash
cd backend

# Com OpenAI (recomendado)
export OPENAI_API_KEY=sua_chave_aqui

mvn spring-boot:run
```

API disponível em: `http://localhost:8080/api`  
Swagger UI: `http://localhost:8080/api/swagger-ui.html`  
H2 Console: `http://localhost:8080/api/h2-console`

### Frontend

```bash
cd frontend
npm install
npm start
```

App disponível em: `http://localhost:4200`

### Docker Compose

```bash
export OPENAI_API_KEY=sua_chave_aqui
docker-compose up --build
```

---

## API Endpoints

### Commodities
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET    | `/api/commodities` | Listar todas |
| GET    | `/api/commodities/{id}` | Buscar por ID |
| GET    | `/api/commodities/type/{type}` | Filtrar por tipo |
| POST   | `/api/commodities` | Criar |
| PUT    | `/api/commodities/{id}` | Atualizar |
| PATCH  | `/api/commodities/{id}/price` | Atualizar preço |
| DELETE | `/api/commodities/{id}` | Remover |
| GET    | `/api/commodities/{id}/history` | Histórico de preços |

### IA (LangChain4j + LangGraph)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST   | `/api/ai/chat` | Chat com assistente |
| POST   | `/api/ai/market-analysis` | Análise de mercado (4 nós LangGraph) |
| POST   | `/api/ai/recommendation` | Recomendação compra/venda |
| POST   | `/api/ai/analyze` | Análise personalizada |

### Exemplo de Request IA

```json
POST /api/ai/market-analysis
{
  "question": "Qual a tendência da soja para as próximas semanas?",
  "commodityId": 1,
  "analysisType": "MARKET_ANALYSIS"
}
```

### Exemplo de Response

```json
{
  "answer": "Com base nos dados de mercado...",
  "sentiment": "BULLISH",
  "confidenceScore": 0.85,
  "workflowSteps": [
    { "stepName": "data_collection", "status": "COMPLETED", "output": "..." },
    { "stepName": "market_analysis", "status": "COMPLETED", "output": "..." },
    { "stepName": "risk_assessment", "status": "COMPLETED", "output": "..." },
    { "stepName": "recommendation",  "status": "COMPLETED", "output": "..." }
  ],
  "modelUsed": "gpt-4o-mini via LangChain4j + LangGraph Workflow"
}
```

---

## Funcionalidades

### Dashboard
- Cotações em tempo real com auto-refresh a cada 60s
- Indicadores de mercado (em alta / em baixa)
- Cards com variação de preço coloridos
- Acesso rápido à análise IA por commodity

### Gestão de Commodities
- CRUD completo
- Filtros por tipo e busca por nome
- Tabela com variação de preço visual
- Atualização de cotação individual

### Gráfico de Preços
- Histórico dos últimos 30 registros
- Chart.js com linha suavizada
- Tooltips com preço e data

### IA Assistente (LangGraph)
- **Chat Livre**: Perguntas sobre agronegócio
- **Análise de Mercado**: Workflow com 4 nós (coleta → análise → risco → recomendação)
- **Recomendação**: COMPRAR / VENDER / AGUARDAR
- Exibe steps do LangGraph no frontend
- Sentimento (BULLISH/BEARISH/NEUTRAL)
- Score de confiança

---

## LangGraph Workflow

O sistema implementa um workflow de grafo dirigido inspirado no LangGraph Python:

```
GraphState {
  userQuestion, commodityContext,
  marketAnalysis, riskAssessment,
  finalRecommendation, sentiment, confidenceScore,
  workflowSteps[]
}

Nodes:
1. dataCollectionNode  → enriquece contexto com metadados
2. marketAnalysisNode  → chama LLM para análise de mercado
3. riskAssessmentNode  → chama LLM para avaliação de riscos
4. recommendationNode  → sintetiza e gera resposta final
```

---

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `OPENAI_API_KEY` | Chave da API OpenAI | `demo` |
| `SPRING_PROFILES_ACTIVE` | Perfil Spring | `default` |

> **Nota**: Sem `OPENAI_API_KEY`, o sistema funciona mas as análises de IA retornam erros. Configure a variável para habilitar a IA completa.
