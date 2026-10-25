# LangChain & Agentic AI Learning

My hands-on journey learning LangChain, LLMs, tool calling, and Agentic AI and more through Jupyter notebooks and PDF study guides.

## 📚 Learning Notebooks

| Notebook | Topics | Guide |
| :--- | :--- | :---: |
| [LangChain Intro](langchain-study/1-langchainIntro.ipynb) | Agents, custom tools | [PDF](pdf/1-langchainIntro.pdf) |
| [Model Integration](langchain-study/2-modelintegration.ipynb) | Gemini, streaming, batching | [PDF](pdf/2-modelintegration.pdf) |
| [Tool Calling](langchain-study/3-toolcall.ipynb) | Groq, tool binding, execution loops | [PDF](pdf/3-toolcall.pdf) |
| [Core Messages](langchain-study/4-messages.ipynb) | Message types, personas, speaker metadata, tool handshake | [PDF](pdf/4-messages.pdf) |
| [Structured Outputs](langchain-study/5-structure.ipynb) | Pydantic v2, TypedDict, schemas, agent response formats | [PDF](pdf/5-structure.pdf) |
| [Agent Starter](langchain-study/langchainIntro.ipynb) | Introductory experiments | — |

---

## ⚙️ Setup

Requires Python and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/VaradPandey/langchain-agentic-ai-learning.git
cd langchain-agentic-ai-learning
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

---

## 📁 Project Structure

```text
langchain-study/ — Jupyter notebooks
pdf/             — PDF study guides
src/             — Python source code
task/            — PDF generation tools and instructions
scratch/         — Experiments and temporary work
```

This repository will grow as I explore more LangChain and Agentic AI concepts.
