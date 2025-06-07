# Graphiti Knowledge Graph Server

A FastAPI-based server that provides a temporal knowledge graph API using Graphiti, designed for AI agents with episodic memory capabilities.

## Overview

Graphiti is a framework for building and querying temporally-aware knowledge graphs. This server wraps Graphiti's core functionality in a RESTful API, enabling AI systems to maintain contextual awareness over time by tracking how facts and relationships evolve.

## Features

- **Temporal Knowledge Management**: Track how information changes over time with episodic processing
- **Multi-LLM Support**: Works with OpenAI, Anthropic Claude, Google Gemini, and Groq
- **Hybrid Retrieval**: Combines semantic embeddings, keyword search (BM25), and graph traversal
- **Real-time Updates**: Add episodes and search the knowledge graph with low latency
- **Neo4j Backend**: Leverages the power of Neo4j for graph storage and querying
- **Full CRUD Operations**: Complete node and relationship management capabilities
- **Graph Statistics**: Real-time insights into your knowledge graph structure

## Prerequisites

- Python 3.10+
- Neo4j 5.26+ (running and accessible)
- At least one LLM API key (OpenAI is required for embeddings)

## Installation

### Using Docker (Recommended)

```bash
docker compose up
```

### Manual Installation

```bash
pip install -r requirements.txt
python main.py
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Required Environment Variables

- `OPENAI_API_KEY`: Required for embeddings (even when using other LLM providers)
- `NEO4J_PASSWORD`: Your Neo4j database password
- `NEO4J_URI`: Neo4j connection URI (default: `bolt://localhost:7687`)
- `NEO4J_USER`: Neo4j username (default: `neo4j`)

### Optional LLM Providers

Configure one of these for LLM operations:
- `ANTHROPIC_API_KEY`: For Claude models
- `GOOGLE_API_KEY`: For Gemini models
- `GROQ_API_KEY`: For Groq-hosted models

## API Endpoints

### Health Check
- `GET /health` - Check API and database connectivity

### Episodes
- `POST /episodes/add` - Add a new episode to the knowledge graph
  ```json
  {
    "content": "John met Jane at the conference",
    "source": "meeting_notes",
    "name": "Conference Meeting",
    "episode_type": "message",
    "reference_time": "2024-01-15T10:30:00Z",
    "metadata": {"location": "NYC"}
  }
  ```

### Search
- `POST /search` - Search the knowledge graph
  ```json
  {
    "query": "conference meetings",
    "limit": 10,
    "num_hops": 2
  }
  ```

### Nodes
- `POST /nodes/add` - Add a new node
- `GET /nodes/{uuid}` - Get a specific node
- `PUT /nodes/update` - Update a node
- `DELETE /nodes/delete` - Delete a node

### Relationships
- `POST /relationships/add` - Create a relationship between nodes

### Graph Statistics
- `GET /graph/stats` - Get statistics about the knowledge graph

## Docker Deployment

The server is configured to work within the openapi-servers ecosystem:

```yaml
services:
  graphiti-server:
    build:
      context: ./servers/graphiti
    ports:
      - 8087:8000
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - NEO4J_PASSWORD=${NEO4J_PASSWORD}
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

## LLM Provider Priority

The server automatically selects LLM providers in this order:
1. Anthropic Claude (if `ANTHROPIC_API_KEY` is set)
2. Groq (if `GROQ_API_KEY` is set)
3. Google Gemini (if `GOOGLE_API_KEY` is set)
4. OpenAI (default)

## Neo4j Connection

The server connects to Neo4j using the Bolt protocol. In Docker, use `host.docker.internal` to connect to Neo4j running on the host machine.

## API Documentation

When running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Usage

### Add an Episode
```bash
curl -X POST "http://localhost:8000/episodes/add" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Alice started working on the AI project",
    "source": "project_log",
    "episode_type": "event"
  }'
```

### Search the Graph
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI project",
    "limit": 5
  }'
```

## Troubleshooting

1. **Neo4j Connection Issues**: Ensure Neo4j is running and accessible at the configured URI
2. **API Key Errors**: Verify all required API keys are set in the environment
3. **Docker Networking**: Use `host.docker.internal` when Neo4j is running on the host

## License

This server follows the same license as the parent openapi-servers project.
