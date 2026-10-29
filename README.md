# Agentic AI Learning (LangChain, LangGraph, RAG & Agents)

My hands-on journey learning LangChain, LangGraph, RAG architectures, LLM tool calling, and autonomous Agentic AI systems through Jupyter notebooks and PDF study guides.

## 📚 Study Modules

### 🦜 LangChain Study (`langchain-study/`)

| Notebook | Topics | Guide |
| :--- | :--- | :---: |
| [LangChain Intro](langchain-study/1-langchainIntro.ipynb) | Agents, custom tools | [PDF](pdf/1-langchainIntro.pdf) |
| [Model Integration](langchain-study/2-modelintegration.ipynb) | Gemini, streaming, batching | [PDF](pdf/2-modelintegration.pdf) |
| [Tool Calling](langchain-study/3-toolcall.ipynb) | Groq, tool binding, execution loops | [PDF](pdf/3-toolcall.pdf) |
| [Core Messages](langchain-study/4-messages.ipynb) | Message types, personas, speaker metadata, tool handshake | [PDF](pdf/4-messages.pdf) |
| [Structured Outputs](langchain-study/5-structure.ipynb) | Pydantic v2, TypedDict, schemas, agent response formats | [PDF](pdf/5-structure.pdf) |
| [Middleware & Governance](langchain-study/6-middleware.ipynb) | Summarization (length & token), HumanInTheLoop (approve, edit, reject) | [PDF](pdf/6-middleware.pdf) |
| [Agent Starter](langchain-study/langchainIntro.ipynb) | Introductory experiments | — |

### 🕸️ LangGraph Study (`langgraph-study/`)
*Stateful agents, multi-agent workflows, human-in-the-loop graphs, and persistence.* (In progress)

### 🔍 Retrieval-Augmented Generation (`rag-study/`)
*Document chunking, vector embeddings, hybrid search, rerankers, and agentic RAG.* (In progress)

---

## ⚙️ Setup

Requires Python and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/VaradPandey/langchain-agentic-ai-learning.git
cd Agentic-AI
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
- [ ] LangGraph cyclic workflows & supervisor agents
- [ ] RAG pipelines & Vector database retrieval

---

## 📁 Project Structure

```text
langchain-study/ — LangChain notebooks & foundational agent experiments
langgraph-study/ — LangGraph cyclical workflows and state graphs
rag-study/       — RAG pipelines, embeddings, and retrieval workflows
pdf/             — High-resolution PDF study guides
src/             — Reusable Python source package (agentic_ai_learning)
task/            — PDF generation tools and styling assets
scratch/         — Quick experiments and temporary scratchpads
```

This repository will grow as I explore more Agentic AI, LangGraph, and RAG concepts.
