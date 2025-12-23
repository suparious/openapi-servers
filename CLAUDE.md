# CLAUDE.md - OpenAPI Servers AI Assistant Context

**Attach this to every openapi-servers conversation.**

---

## ⚡ QUICK START

**Project**: OpenAPI Servers - Reference implementations for AI agent tools
**Status**: Early Production / Beta
**Owner**: Open WebUI Community + SolidRusT Networks integration
**Rule**: Standards-based REST APIs, no proprietary protocols

**What This Is**:
- 20+ FastAPI server implementations for common AI/agent use cases
- Standardized OpenAPI/REST APIs replacing proprietary protocols
- Reference implementations for tool composition in AI agents
- Docker Compose orchestration with Neo4j, PostgreSQL, Valkey, LiteLLM

**Key Services** (currently deployed):
- **Filesystem Server** (8081) - Safe local file operations
- **Memory Server** (8082) - JSON-based knowledge graph
- **Time Server** (8083) - Timezone utilities
- **Summarizer Server** (8084) - Ollama-based text summarization
- **Weather Server** (8085) - Weather data
- **User Info Server** (8086) - Enriched user profiles
- **Graphiti Server** (8087) - Temporal knowledge graph (Neo4j backend)

---

## 🎯 STRATEGIC CONTEXT (2025-11-11)

**This platform enables AI agent tool composition for the flagship product.**

**Master Strategic Assessment**: `/mnt/c/Users/shaun/repos/STRATEGIC-ASSESSMENT-2025.md`

**OpenAPI Servers' Role in Business**:
- **Tool ecosystem** for AI agents (extends AI Inference Platform capabilities)
- **Standardization advantage**: OpenAPI/REST vs proprietary protocols (no vendor lock-in)
- **Rapid prototyping**: Drop-in server implementations for common agent use cases
- **Differentiation**: Bridges MCP protocol to REST APIs (ecosystem interoperability)

**Integration with Flagship Product** (AI Inference Platform):
- **AI agents** running on vLLM backend can call these tools via REST APIs
- **SolidRusT.net** demonstrates MCP bridge integration (browser tools → Claude servers)
- **Knowledge graphs** (Graphiti + Neo4j) enable sophisticated agent memory and reasoning
- **LiteLLM proxy** provides multi-model LLM access (OpenAI, Anthropic, Google, Groq)

**Business Value**:
- **Competitive differentiation**: "AI agents with built-in tool ecosystem"
- **Customer stickiness**: More tools = more value = harder to switch
- **Rapid feature development**: Pre-built servers accelerate agent capabilities
- **Community leverage**: Open-source contributions extend platform

**Current Capabilities** (compose.yaml):
- ✅ 8 servers deployed (filesystem, memory, time, summarizer, weather, user-info, graphiti)
- ✅ Neo4j knowledge graph (port 7687) for temporal reasoning
- ✅ PostgreSQL (LiteLLM database, port 5432)
- ✅ Valkey/Redis (caching/sessions, port 6379)
- ✅ LiteLLM proxy (multi-model access, port 4000)
- ✅ Prometheus monitoring (port 9090)
- ⚠️ Some servers have known issues (user-info HTTP 401, pipelines service broken)

**Technology Stack**:
- **Framework**: FastAPI + Uvicorn (all servers)
- **Language**: Python 3.10+
- **Containerization**: Docker + Docker Compose
- **Knowledge Store**: Neo4j (graph database)
- **DB Cache**: Valkey (Redis alternative)
- **LLM Integration**: LiteLLM proxy
- **Documentation**: OpenAPI/Swagger auto-generated

**Strategic Importance**:
- **Protocol Bridging**: MCP → OpenAPI converter (mcpo) enables ecosystem interoperability
- **Future-Proof**: Built on stable standards (HTTP, REST, OpenAPI), not experimental protocols
- **No Vendor Lock-In**: Customers can self-host or use cloud, no proprietary dependencies
- **Modular Architecture**: Easy to fork, customize, extend without touching core logic

**Known Limitations** (from compose.yaml):
- User Info server: Constant HTTP 401 errors (needs auth fix)
- Open WebUI Pipelines: Broken, unclear cause (marked in config)
- Git server: Untested MCP port (needs validation)
- External RAG, SQL servers: Minimal implementations (needs expansion)

**Technical Decisions for Business Success**:
- **Stability first**: Fix broken services (user-info, pipelines) before adding new servers
- **Documentation**: Each server needs clear API docs and integration examples
- **Security**: Enable API key authentication (currently optional)
- **Monitoring**: Integrate with srt-hq-monitoring-stack (Prometheus metrics)
- **Testing**: Validate all servers work in production (automated tests)

**Investor Talking Points**:
- "20+ reference server implementations for AI agent tools"
- "Standardized REST/OpenAPI APIs, no vendor lock-in"
- "Knowledge graph integration for sophisticated agent memory (Neo4j)"
- "Multi-LLM provider support (OpenAI, Anthropic, Google, Groq)"
- "Community-driven with open-source ecosystem"

**NEXT STEPS** (for business readiness):
1. Fix broken services (user-info auth, pipelines)
2. Test all servers (automated integration tests)
3. Document API usage (Swagger + examples for each server)
4. Enable security (API key authentication across all servers)
5. Monitoring integration (Prometheus metrics + Grafana dashboards)

---

## 📁 PROJECT STRUCTURE

```
openapi-servers/
├── compose.yaml                # Docker Compose orchestration (8 services)
├── servers/                    # Individual server implementations
│   ├── external-rag/           # RAG pipeline integration
│   ├── filesystem/             # File operations (32KB code)
│   ├── get-oauth-tokens/       # OAuth token management
│   ├── get-tokens-from-cookies/# Cookie-based auth
│   ├── get-user-info/          # User profile enrichment
│   ├── git/                    # Repository operations (untested)
│   ├── google-pse/             # Programmable Search Engine
│   ├── graphiti/               # Knowledge graph (45KB code, Neo4j)
│   ├── memory/                 # JSON knowledge graph
│   ├── slack/                  # Workspace integration (28KB code)
│   ├── sql/                    # Database querying
│   ├── summarizer/             # Text summarization (Ollama)
│   ├── time/                   # Timezone utilities
│   ├── weather/                # Weather data
│   ├── bitcoin-price-predictor/# ML-based prediction
│   ├── mcp-proxy/              # MCP ↔ OpenAPI bridge
│   └── ui/                     # Browser interfaces (flashcards, time, quotes)
├── README.md                   # Project overview
└── docs/                       # Documentation (if exists)
```

**Total Code**: ~3,746 lines across all servers
**Largest Servers**: graphiti (45KB), filesystem (32KB), slack (28KB)
**Smallest Servers**: external-rag, sql (minimal implementations)

---

## 🔧 DEPLOYMENT

### Local Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Access services
curl http://localhost:8081/docs  # Filesystem server
curl http://localhost:8082/docs  # Memory server
curl http://localhost:8087/docs  # Graphiti server
```

### Service Ports

| Service | Port | Purpose |
|---------|------|---------|
| Filesystem | 8081 | File operations |
| Memory | 8082 | Knowledge graph |
| Time | 8083 | Timezone utilities |
| Summarizer | 8084 | Text summarization |
| Weather | 8085 | Weather data |
| User Info | 8086 | User profiles (⚠️ broken) |
| Graphiti | 8087 | Temporal knowledge (Neo4j) |
| LiteLLM Proxy | 4000 | Multi-model LLM access |
| Valkey/Redis | 6379 | Caching |
| Prometheus | 9090 | Monitoring |

### Production Deployment (TBD)

- Kubernetes manifests not yet created
- Could integrate with srt-hq-k8s cluster
- Needs proper secrets management (Sealed Secrets)

---

## 🤝 COMMUNITY & CONTRIBUTIONS

**Source**: Open WebUI community (reference implementations)
**Customizations**: SolidRusT Networks integration for platform

**Philosophy**:
- Open standards over proprietary protocols
- Community contributions welcome
- Clear patterns for building new servers
- No vendor lock-in

---

## 🔗 INTEGRATION WITH SOLIDRUST ECOSYSTEM

**Connections**:
- **srt-hq-vllm**: LLM backend for agents calling these tools
- **srt-hq-k8s**: Potential deployment platform
- **srt-hq-monitoring-stack**: Prometheus integration for observability
- **SolidRusT.net**: MCP WebSocket bridge demonstrates tool integration

**Future Integration**:
- Deploy on srt-hq-k8s cluster (alongside vLLM)
- Expose via Artemis proxy (public tool APIs)
- Integrate with PAM platform (auth for tool access)
- Monitoring via Grafana (tool usage dashboards)

---

**Document Version**: 1.0
**Last Updated**: November 11, 2025
