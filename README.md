# Agentic AI Learning (LangChain, LangGraph, RAG & Agents)

My hands-on journey learning LangChain, LangGraph, RAG architectures, LLM tool calling, and autonomous Agentic AI systems through Jupyter notebooks and PDF study guides.

## 📚 Study Modules

### 🦜 LangChain Study (`langchain-study/`)

| Notebook | Topics | Guide |
| :--- | :--- | :---: |
| [LangChain Intro](langchain-study/1-langchainIntro.ipynb) | Agents, custom tools | [PDF](pdf/langchain/1-langchainIntro.pdf) |
| [Model Integration](langchain-study/2-modelintegration.ipynb) | Gemini, streaming, batching | [PDF](pdf/langchain/2-modelintegration.pdf) |
| [Tool Calling](langchain-study/3-toolcall.ipynb) | Groq, tool binding, execution loops | [PDF](pdf/langchain/3-toolcall.pdf) |
| [Core Messages](langchain-study/4-messages.ipynb) | Message types, personas, speaker metadata, tool handshake | [PDF](pdf/langchain/4-messages.pdf) |
| [Structured Outputs](langchain-study/5-structure.ipynb) | Pydantic v2, TypedDict, schemas, agent response formats | [PDF](pdf/langchain/5-structure.pdf) |
| [Middleware & Governance](langchain-study/6-middleware.ipynb) | Summarization (length & token), HumanInTheLoop (approve, edit, reject) | [PDF](pdf/langchain/6-middleware.pdf) |
| [Agent Starter](langchain-study/langchainIntro.ipynb) | Introductory experiments | — |

### 🕸️ LangGraph Study (`langgraph-study/`)

| Notebook | Topics | Guide |
| :--- | :--- | :---: |
| [Basic ChatBot](langgraph-study/1-BasicChatBot.ipynb) | StateGraph, `add_messages` reducer, ToolNode, ReAct cyclic loops, MemorySaver persistence, streaming (`updates`, `values`, `astream_events`) | [PDF](pdf/langgraph/1-BasicChatBot.pdf) |
| [Human In The Loop](langgraph-study/2-HumanInTheLoop.ipynb) | Dynamic breakpoints (`interrupt()`), checkpoint state freezing, resumption via `Command(resume=...)`, supervisor synthesis | [PDF](pdf/langgraph/2-HumanInTheLoop.pdf) |
| [Model Context Protocol (MCP)](langgraph-study/3-MCP.ipynb) | FastMCP servers, `stdio` OS pipes, `streamable-http` SSE, `MultiServerMCPClient` ReAct orchestration | [PDF](pdf/langgraph/3-MCP.pdf) |

### 🔍 Retrieval-Augmented Generation (`rag-study/`)
*Document chunking, vector embeddings, hybrid search, rerankers, and agentic RAG.* (In progress)

---

## ⚙️ Setup

Requires Python and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/VaradPandey/agentic-ai-learning.git
cd "Agentic AI"
uv sync
```

Create a `.env` file using `.env.example` and add the API keys required by your notebooks.

Run Jupyter Lab:

```bash
uv run jupyter lab
```

> [!IMPORTANT]
> Never commit your `.env` file or API keys.

---

## 🗺️ Progress so far

- [x] LangChain agents and custom tools
- [x] LLM integration, streaming, and batching
- [x] Tool calling and execution loops
- [x] Message types, system personas, and multi-turn tool handshakes
- [x] Structured output extraction, Pydantic schemas, and agent response formats
- [x] Agent middleware, automated sliding summarization, and human-in-the-loop governance (approve, edit, reject)
- [x] LangGraph state machines, cyclical ReAct loops, MemorySaver checkpointing, and execution streaming
- [x] Human-in-the-loop dynamic breakpoints (`interrupt()`) and interactive state resumption (`Command`)
- [x] Model Context Protocol (MCP) servers, dual transports (`stdio` & `streamable-http`), and multi-server ReAct agents
- [ ] Multi-agent supervisor teams and hierarchical graphs
- [ ] RAG pipelines & Vector database retrieval

---

## 📁 Project Structure

```text
langchain-study/ — LangChain notebooks & foundational agent experiments
langgraph-study/ — LangGraph cyclical workflows, state graphs, HITL & MCP
rag-study/       — RAG pipelines, embeddings, and retrieval workflows
pdf/             — High-resolution PDF study guides
  ├── langchain/ — Study guides for LangChain modules
  └── langgraph/ — Study guides for LangGraph & MCP modules
src/             — Reusable Python source package (agentic_ai_learning)
task/            — PDF generation tools and styling assets
scratch/         — Quick experiments and temporary scratchpads
```

This repository will grow as I explore more Agentic AI, LangGraph, and RAG concepts.
