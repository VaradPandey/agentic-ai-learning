# LangChain & Agentic AI Learning Journey

Welcome to **LangChain & Agentic AI Learning**! This repository documents my hands-on learning path through modern LangChain (v1+), Large Language Model (LLM) integrations, tool calling, agent loops, and Agentic AI concepts.

Every milestone is documented with runnable Jupyter Notebooks and accompanying educational PDF study guides.

---

## 🎯 Purpose and Learning Goals

The objective of this repository is to build a practical, foundational understanding of Agentic AI by building from scratch:

1. **Modern LangChain Abstractions**: Working with the unified interface in modern LangChain (`init_chat_model`, `create_agent`, `@tool`).
2. **Multi-Model Integrations**: Interfacing seamlessly with various LLM providers (Google Gemini, Groq, OpenAI).
3. **Inference Patterns**: Mastering standard invocation (`invoke`), real-time token streaming (`stream`), and parallel batch processing (`batch`).
4. **Tool Calling & Execution Loops**: Empowering models with external tools, structured outputs, argument passing, and multi-turn execution loops.
5. **Agentic Workflows**: Laying the foundation for autonomous agents, Retrieval-Augmented Generation (RAG), and Model Context Protocol (MCP).

---

## 🗺️ Learning Roadmap & Notebook Directory

All hands-on notebooks reside in [`langchain-study/`](langchain-study/). Accompanying publication-grade PDF study guides are located in [`pdf/`](pdf/).

| # | Notebook | Topic & Core Concepts | Accompanying Guide | Status |
| :---: | :--- | :--- | :--- | :---: |
| 1 | [`1-langchainIntro.ipynb`](langchain-study/1-langchainIntro.ipynb) | **LangChain V1 Agent & Custom Tools**<br>• Initializing LangChain v1<br>• Custom weather tool definition<br>• Creating an agent with `create_agent`<br>• Message-based invocation | [`1-langchainIntro.pdf`](pdf/1-langchainIntro.pdf) | Completed |
| 2 | [`2-modelintegration.ipynb`](langchain-study/2-modelintegration.ipynb) | **Model Integrations, Streaming & Batching**<br>• Initializing chat models with `init_chat_model`<br>• Google Gemini integration (`gemini-3.8-flash`)<br>• Token streaming with `model.stream()` and live flushing<br>• Batching multiple queries in parallel with `model.batch()` | [`2-modelintegration.pdf`](pdf/2-modelintegration.pdf) | Completed |
| 3 | [`3-toolcall.ipynb`](langchain-study/3-toolcall.ipynb) | **Tool Calling & Execution Loop**<br>• Groq provider integration (`groq:openai/gpt-oss-20b`)<br>• Tool declaration using `@tool`<br>• Tool binding via `model.bind_tools()`<br>• Extracting model tool calls (`response.tool_calls`)<br>• Full multi-turn Tool Execution Loop | [`3-toolcall.pdf`](pdf/3-toolcall.pdf) | Completed |
| - | [`langchainIntro.ipynb`](langchain-study/langchainIntro.ipynb) | **LangChain Agent Starter**<br>• Exploratory introductory notebook covering initial setup and agent structure | - | Completed |

---

## 📁 Repository Structure

```text
Langchain_Learn/
├── langchain-study/                  # Hands-on Jupyter notebooks
│   ├── 1-langchainIntro.ipynb        # Agent & tool introduction
│   ├── 2-modelintegration.ipynb      # Provider integration, streaming & batch
│   ├── 3-toolcall.ipynb              # Tool binding & execution loop
│   └── langchainIntro.ipynb          # Exploratory introduction
├── pdf/                              # Educational study guide PDFs
│   ├── 1-langchainIntro.pdf          # Deep-dive study guide for Notebook 1
│   ├── 2-modelintegration.pdf        # Deep-dive study guide for Notebook 2
│   └── 3-toolcall.pdf                # Deep-dive study guide for Notebook 3
├── src/                              # Source package modules
│   └── langchain_learn/
│       └── __init__.py
├── task/                             # Automation & documentation tooling
│   ├── NOTEBOOK_PDF_INSTRUCTIONS.md  # Standard operating procedures for PDF guides
│   └── generate_notebook_pdf.py      # Automated PDF study guide generator
├── scratch/                          # Local scratchpad and experiment scripts
├── .env.example                      # Safe template for required environment variables
├── .gitignore                        # Git ignore rules for credentials, caches & venvs
├── .python-version                   # Python version specification (3.14)
├── pyproject.toml                    # UV / PEP 621 project configuration
├── requirements.txt                  # Standard pip dependencies list
└── uv.lock                           # UV reproducible dependency lockfile
```

---

## ⚙️ Setup and Installation

### Prerequisites

- Python 3.11+ installed (project configured for 3.14).
- [`uv`](https://docs.astral.sh/uv/) (recommended) or standard `pip`.

### 1. Clone the Repository

```bash
git clone https://github.com/VaradPandey/langchain-agentic-ai-learning.git
cd langchain-agentic-ai-learning
```

### 2. Set Up the Environment

#### Option A: Using `uv` (Recommended)

```bash
# Sync dependencies and create virtual environment automatically
uv sync
```

#### Option B: Using standard Python `venv` and `pip`

```bash
# Create and activate virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔑 API Key Configuration

This project integrates with Google Gemini, Groq, and OpenAI. API keys are loaded securely via `python-dotenv` from a local `.env` file.

> [!IMPORTANT]
> Never commit your `.env` file to version control. The `.gitignore` file is pre-configured to keep your credentials private.

1. Copy the provided `.env.example` template to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and insert your API keys:
   ```env
   # Google Gemini (Notebooks 1 & 2)
   # Obtain key: https://aistudio.google.com/
   GEMINI_API_KEY=your_gemini_api_key_here

   # Groq (Notebook 3)
   # Obtain key: https://console.groq.com/
   GROQ_API_KEY=your_groq_api_key_here

   # OpenAI (Optional / Future modules)
   # Obtain key: https://platform.openai.com/
   OPENAI_API_KEY=your_openai_api_key_here
   ```

---

## 🚀 How to Run the Notebooks

1. Activate your virtual environment:
   ```bash
   # Windows:
   .venv\Scripts\activate
   # macOS / Linux:
   source .venv/bin/activate
   ```

2. Register the kernel in Jupyter:
   ```bash
   python -m ipykernel install --user --name=langchain-learn --display-name "Python (langchain-learn)"
   ```

3. Launch Jupyter Lab or open the notebooks in VS Code / Antigravity IDE:
   ```bash
   jupyter lab
   ```

4. Select the `Python (langchain-learn)` kernel and run the cells sequentially!

---

## 📋 Progress Checklist

- [x] **LangChain Environment Setup**: Configured `uv`, dependencies, and virtual environment.
- [x] **Agent Basics**: Created basic agent with custom Python tools (`1-langchainIntro.ipynb`).
- [x] **LLM Integrations**: Connected to Google Gemini 3.8 Flash (`2-modelintegration.ipynb`).
- [x] **Streaming**: Implemented token streaming with live console flush (`2-modelintegration.ipynb`).
- [x] **Batch Processing**: Configured parallel batch queries with `max_concurrency` (`2-modelintegration.ipynb`).
- [x] **Tool Calling**: Bound tools to Groq OSS models and handled `tool_calls` payloads (`3-toolcall.ipynb`).
- [x] **Tool Execution Loop**: Built complete loop parsing tool calls and feeding results back to LLM (`3-toolcall.ipynb`).
- [x] **Study Guides**: Generated publication-grade PDF educational documentation for all core notebooks.
- [ ] **Advanced RAG**: Retrieval-Augmented Generation with vector stores and embeddings *(Planned)*.
- [ ] **Agentic AI & MCP**: Model Context Protocol servers and multi-agent coordination *(Planned)*.
