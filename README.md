# InsightForge

**AI-powered codebase analyst** running entirely on your local machine. Ask questions about any codebase in plain language — no API keys, no data leaving your machine.

![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-52%20passing-brightgreen)
![LLM](https://img.shields.io/badge/LLM-Ollama%20local-orange)

---

## Features

- **RAG-powered Q&A** — index any codebase with ChromaDB + `nomic-embed-text`, then ask anything
- **Tech stack detection** — automatically detect frontend, backend, database, AI/ML, CI/CD, cloud, containers
- **GitHub repo reader** — scan and read files from any public GitHub repo (or private with a token) without cloning
- **Sensitive file guard** — auto-masks API keys, tokens, and credentials before sending to the LLM
- **Offline mode** — `/scan`, `/stack`, `/history` work without Ollama running
- **Session history** — conversations are saved, searchable, and deletable
- **Fully local** — runs on `qwen2.5:7b` via [Ollama](https://ollama.com), no internet required for chat

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.13+ | [python.org](https://python.org) |
| [uv](https://docs.astral.sh/uv/) | latest | `curl -Ls https://astral.sh/uv/install.sh \| sh` |
| [Ollama](https://ollama.com) | latest | [ollama.com/download](https://ollama.com/download) |

After installing Ollama, pull the required models:

```bash
ollama pull qwen2.5:7b          # LLM (~4.7 GB)
ollama pull nomic-embed-text    # Embeddings (~137 MB)
```

---

## Installation

```bash
# Clone the repo
git clone https://github.com/phanminhtai1029/InsightForge.git
cd InsightForge

# Create virtual environment and install dependencies
uv sync

# Activate venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate        # Windows
```

---

## Quick Start

```bash
# Analyze your current project
insightforge .

# Or point to any folder
insightforge /path/to/your/project
```

On first run, InsightForge will:
1. Check Ollama availability
2. Scan for sensitive files and warn you
3. Offer to load previous conversation history

---

## Usage

### Built-in Commands

| Command | Works offline | Description |
|---------|:---:|-------------|
| `/scan` | ✅ | List and classify all files in the current folder |
| `/stack` | ✅ | Detect tech stack (frontend, backend, DB, AI/ML, CI/CD...) |
| `/index` | ❌ | Index the codebase into ChromaDB for RAG queries |
| `/history` | ✅ | List saved conversation sessions |
| `/history delete <n>` | ✅ | Delete session #n |
| `/history delete all` | ✅ | Delete all saved sessions (with confirmation) |
| `/save [filename]` | ✅ | Export current conversation to Markdown |
| `/clear` | ✅ | Clear in-memory conversation (saved sessions untouched) |
| `/exit` | ✅ | Exit and auto-save current session |

### CLI Options

```bash
insightforge --help

insightforge .                  # analyze current directory
insightforge /path/to/project   # analyze specific folder
insightforge . --fresh          # start new session, skip loading history
insightforge . --model llama3.2 # override default LLM model
```

### Chat Examples

Once the agent is running, you can ask questions in natural language:

**Easy — tool use:**
```
> What's the tech stack of this project?
> List all Python files and their purpose.
> Are there any sensitive files I should know about?
```

**Medium — code understanding:**
```
> Read the main entry point and explain what it does.
> How is authentication handled in this codebase?
> What design patterns are used in the core module?
```

**Hard — RAG + reasoning:**
```
> [after /index] How does the event bus communicate between agents?
> Find all places where database connections are created.
> What would break if I removed the rate limiter?
```

**GitHub repos:**
```
> Scan the GitHub repo huggingface/transformers and explain its structure.
> Read the file src/transformers/modeling_utils.py from huggingface/transformers.
> Compare the architecture of pytorch/pytorch vs tensorflow/tensorflow.
```

---

## GitHub Repo Reader

InsightForge can scan and read files from GitHub without cloning:

```
> Scan repo vercel/next.js
> Read file packages/next/src/server/next-server.ts from vercel/next.js
```

**For private repositories**, set the `GITHUB_TOKEN` environment variable:

```bash
export GITHUB_TOKEN=ghp_your_token_here
insightforge .
```

The token needs `repo` scope. Without it, you're limited to public repos and 60 API requests/hour (5,000/hour with token).

---

## Configuration

### Models

Override defaults via CLI flag or environment variables:

```bash
# Use a different LLM
insightforge . --model llama3.2

# Available Ollama models that work well:
# - qwen2.5:7b (default, best balance)
# - llama3.2 (fast, less accurate)
# - qwen2.5:14b (better quality, needs ~9 GB RAM)
```

### Session Data

All session data is stored in `~/.insightforge/`:

```
~/.insightforge/
├── chroma/          # Vector store (RAG indexes per project)
└── sessions/
    └── <folder_hash>/
        ├── 2026-03-13_14h00.md
        └── latest.txt
```

To clear all data: `rm -rf ~/.insightforge/`

---

## Project Structure

```
InsightForge/
├── insightforge/
│   ├── main.py              # CLI entry point (Click + Rich)
│   ├── agent.py             # LlamaIndex AgentWorkflow wrapper
│   ├── config.py            # Configuration dataclass
│   ├── guard.py             # Sensitive file detection & masking
│   ├── ollama_checker.py    # Ollama availability check
│   └── tools/
│       ├── scanner.py       # File tree scanner
│       ├── stack.py         # Tech stack analyzer
│       ├── runner.py        # Shell command runner
│       ├── indexer.py       # ChromaDB RAG indexer
│       ├── retriever.py     # ChromaDB query
│       ├── history.py       # Session history manager
│       └── github.py        # GitHub REST API reader
├── tests/                   # 52 tests (pytest)
├── pyproject.toml
└── uv.lock
```

---

## Agent Tools

The AI agent has access to 9 tools:

| Tool | Description |
|------|-------------|
| `scan_folder` | List and classify files in a local folder |
| `read_file` | Read a local file (with sensitive value masking) |
| `analyze_stack` | Detect tech stack from package files |
| `index_codebase` | Index codebase into ChromaDB for RAG |
| `query_index` | Search the RAG index for relevant code snippets |
| `run_script` | Execute shell commands and return output |
| `search_history` | Search previous conversation sessions |
| `scan_github_repo` | List files in a GitHub repo |
| `read_github_file` | Read a file from a GitHub repo |

---

## Development

```bash
# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=insightforge

# Run the CLI directly
uv run insightforge .
```

---

## Requirements

- **RAM**: ~6 GB minimum (for `qwen2.5:7b` + ChromaDB)
- **Disk**: ~5 GB for models + variable for indexes
- **OS**: Linux, macOS, Windows (WSL2 recommended on Windows)

---

## License

MIT
