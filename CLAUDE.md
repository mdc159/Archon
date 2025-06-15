# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Docker (Recommended)

```bash
# Build and run Archon
python run_docker.py

# Stop containers
docker stop archon-container && docker rm archon-container
```

### Local Development

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run Streamlit UI
streamlit run streamlit_ui.py

# Run tests
pytest
```

### Updating

```bash
git pull
python run_docker.py  # For Docker
# OR
pip install -r requirements.txt && streamlit run streamlit_ui.py  # For local
```

## High-Level Architecture

### System Overview

Archon is an "Agenteer" - an AI agent that autonomously builds other AI agents using Pydantic AI. It uses a multi-agent architecture orchestrated by LangGraph.

### Core Components

1. **Streamlit UI (`streamlit_ui.py`)**: Web interface providing chat, configuration, and database management
2. **Agent Graph (`archon/archon_graph.py`)**: LangGraph workflow orchestrating the multi-step agent creation process
3. **Primary Coder (`archon/pydantic_ai_coder.py`)**: Main agent generating Pydantic AI agent code with RAG support
4. **FastAPI Service (`graph_service.py`)**: HTTP API for agent workflow and MCP integration

### Agent Workflow

1. **Scope Definition**: Reasoner LLM (O3-mini) creates detailed scope from user description
2. **Advisor Stage**: Analyzes prebuilt resources (tools/examples/MCPs) for recommendations
3. **Coding Stage**: Primary agent generates initial code (agent.py, agent_tools.py, agent_prompts.py, .env.example, requirements.txt)
4. **Refinement Loop**: User feedback or autonomous refinement through specialized agents
5. **Completion**: Final code output with execution instructions

### Key Integrations

- **RAG**: Supabase vector database with OpenAI embeddings for documentation retrieval
- **MCP**: Model Context Protocol server for AI IDE integration (Windsurf, Cursor, Cline)
- **Multi-Model**: Supports OpenAI, Anthropic, and Ollama models

### Important Directories

- `archon/`: Core agent implementations and workflow
- `archon/refiner_agents/`: Specialized agents for prompt, tools, and agent refinement
- `agent-resources/`: Prebuilt tools, examples, and MCP configurations
- `workbench/`: Runtime files (logs, scope, environment variables)
- `streamlit_pages/`: UI components for different functionalities

### Access Points

- Streamlit UI: http://localhost:8501
- Graph Service API: http://localhost:8100
- Health Check: http://localhost:8100/health
