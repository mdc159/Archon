# Archon V5 - Multi-Agent Coding Workflow

This is the fifth iteration of the Archon project, building upon V4 by implementing a multi-agent coding workflow with specialized refiner agents. The system retains the comprehensive Streamlit UI and Docker support from V4, but now adds a sophisticated refinement process with specialized agents for different aspects of agent creation.

What makes V5 special is its approach to agent refinement. The primary coding agent still creates the initial cohesive agent structure, but now users can trigger specialized refiner agents by simply saying "refine" in the chat. This activates three parallel specialized agents that focus on optimizing different aspects of the agent:

1. **Prompt Refiner Agent**: Specializes in optimizing system prompts
2. **Tools Refiner Agent**: Focuses on implementing and improving agent tools
3. **Agent Refiner Agent**: Optimizes agent configuration and dependencies

The core remains an intelligent documentation crawler and RAG (Retrieval-Augmented Generation) system built using Pydantic AI, LangGraph, and Supabase, but now with a more sophisticated multi-agent workflow for refinement.

## Key Features

- **Specialized Refiner Agents**: Three dedicated agents for different aspects of agent creation
- **Parallel Refinement Process**: Agents work simultaneously to improve different components
- **Two-Phase Development**: Initial cohesive structure followed by specialized refinement
- **Simple Refinement Trigger**: Just say "refine" to activate the specialized agents
- **Improved Workflow Orchestration**: Enhanced LangGraph implementation
- **Comprehensive Streamlit UI**: Unified interface for all Archon functionality (from V4)
- **Docker Support**: Containerized deployment with automated build and run scripts (from V4)
- **Multiple LLM Support**: OpenAI, Anthropic, OpenRouter, and local Ollama models

## Architecture

The V5 architecture introduces a more sophisticated agent workflow:

1. **Initial Request**: User describes the AI agent they want to create
2. **Scope Definition**: Reasoner LLM creates a high-level scope for the agent
3. **Initial Agent Creation**: Primary coding agent creates a cohesive initial agent
4. **User Interaction**: User can provide feedback or request refinement
5. **Specialized Refinement**: When "refine" is requested, three specialized agents work in parallel:
   - Prompt Refiner Agent optimizes the system prompt
   - Tools Refiner Agent improves the agent's tools
   - Agent Refiner Agent enhances the agent configuration
6. **Integrated Improvements**: Primary coding agent incorporates all refinements
7. **Iterative Process**: Steps 4-6 repeat until the user is satisfied
8. **Finalization**: Archon provides the complete code with execution instructions

### Agent Graph

The LangGraph workflow orchestrates the entire process:

![Archon Graph](../../public/ArchonGraph.png)

The graph shows how control flows between different agents and how user input can either continue the conversation or trigger the refinement process.

## Specialized Agents

### Prompt Refiner Agent
- Focuses exclusively on optimizing the system prompt
- Analyzes the conversation history to understand the agent's purpose
- Suggests improvements to make the prompt more effective and precise
- Ensures the prompt aligns with best practices for the specific agent type

### Tools Refiner Agent
- Specializes in implementing and improving agent tools
- Has access to Pydantic AI documentation on tool implementation
- Suggests new tools or improvements to existing tools
- Ensures tools follow best practices and are properly typed

### Agent Refiner Agent
- Optimizes agent configuration and dependencies
- Ensures proper setup of agent dependencies and parameters
- Improves error handling and retry mechanisms
- Optimizes agent performance and reliability

## Prerequisites
- Docker (optional but preferred)
- Python 3.11+
- Supabase account (for vector database)
- OpenAI/Anthropic/OpenRouter API key or Ollama for local LLMs

## Installation

### Option 1: Docker (Recommended)
1. Clone the repository:
```bash
git clone https://github.com/coleam00/archon.git
cd archon
```

2. Run the Docker setup script:
```bash
# This will build both containers and start Archon
python run_docker.py
```

3. Access the Streamlit UI at http://localhost:8501.

### Option 2: Local Python Installation
1. Clone the repository:
```bash
git clone https://github.com/coleam00/archon.git
cd archon
```

2. Install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Start the Streamlit UI:
```bash
streamlit run streamlit_ui.py
```

4. Access the Streamlit UI at http://localhost:8501.

## Using the Refinement Feature

To use the new refinement feature in V5:

1. Start a conversation with Archon and describe the agent you want to create
2. After Archon generates the initial agent, type "refine" or a similar phrase
3. Archon will activate the specialized refiner agents in parallel
4. Once refinement is complete, Archon will present the improved agent
5. You can continue to provide feedback or request additional refinements
6. When satisfied, ask Archon to finalize the agent

## Core Files

### Refiner Agents
- `archon/refiner_agents/`: Directory containing specialized refiner agents
  - `prompt_refiner_agent.py`: Agent specialized in optimizing system prompts
  - `tools_refiner_agent.py`: Agent focused on implementing and improving tools
  - `agent_refiner_agent.py`: Agent for optimizing agent configuration and dependencies

### Workflow Orchestration
- `archon/archon_graph.py`: Enhanced LangGraph workflow with refinement paths
- `archon/pydantic_ai_coder.py`: Main coding agent with RAG capabilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
