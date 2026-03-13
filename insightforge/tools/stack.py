import json
from pathlib import Path


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _read_reqs(root: Path) -> str:
    """Đọc tất cả requirements files, trả về unified lowercase string."""
    content_parts = []
    for req_file in [
        "requirements.txt", "requirements/base.txt",
        "requirements/prod.txt", "requirements/main.txt",
    ]:
        p = root / req_file
        if p.exists():
            content_parts.append(p.read_text().lower())
    if (root / "pyproject.toml").exists():
        content_parts.append((root / "pyproject.toml").read_text().lower())
    return "\n".join(content_parts)


def analyze_stack(folder_path: str) -> str:
    root = Path(folder_path)
    detected: dict[str, list[str]] = {
        "Frontend": [], "Backend": [], "AI/ML": [],
        "Database": [], "CI/CD": [], "Cloud": [], "Container": [],
    }

    req_content = _read_reqs(root)

    # Frontend (JS/TS)
    pkg = root / "package.json"
    if pkg.exists():
        data = _read_json(pkg)
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if "next" in deps:
            detected["Frontend"].append(f"Next.js {deps['next'].lstrip('^~')}")
        elif "react" in deps:
            detected["Frontend"].append("React")
        if "vue" in deps:
            detected["Frontend"].append("Vue.js")
        if "tailwindcss" in deps:
            detected["Frontend"].append("TailwindCSS")
        if "typescript" in deps or (root / "tsconfig.json").exists():
            detected["Frontend"].append("TypeScript")

    for name in ["vite.config.ts", "vite.config.js"]:
        if (root / name).exists():
            detected["Frontend"].append("Vite")

    # Frontend (Python UI)
    if req_content:
        if "streamlit" in req_content:
            detected["Frontend"].append("Streamlit")
        if "gradio" in req_content:
            detected["Frontend"].append("Gradio")

    # Backend (web frameworks)
    if req_content:
        if "fastapi" in req_content:
            detected["Backend"].append("FastAPI")
        if "django" in req_content:
            detected["Backend"].append("Django")
        if "flask" in req_content:
            detected["Backend"].append("Flask")
        if "aiohttp" in req_content:
            detected["Backend"].append("aiohttp")
        # Scrapers / crawlers
        if "selenium" in req_content or "playwright" in req_content:
            detected["Backend"].append("Selenium/Playwright")
        if "beautifulsoup" in req_content or "bs4" in req_content:
            detected["Backend"].append("BeautifulSoup")
        if "scrapy" in req_content:
            detected["Backend"].append("Scrapy")
        # Bots
        if "python-telegram-bot" in req_content or "telegram" in req_content:
            detected["Backend"].append("Telegram Bot")
        if "discord" in req_content:
            detected["Backend"].append("Discord Bot")

    if (root / "go.mod").exists():
        detected["Backend"].append("Go")
    if (root / "pom.xml").exists():
        detected["Backend"].append("Java/Spring")
    if (root / "Cargo.toml").exists():
        detected["Backend"].append("Rust")

    # AI/ML
    if req_content:
        # LLM providers
        if "openai" in req_content:
            detected["AI/ML"].append("OpenAI")
        if "anthropic" in req_content:
            detected["AI/ML"].append("Anthropic")
        if "groq" in req_content:
            detected["AI/ML"].append("Groq")
        if "google-generativeai" in req_content or "google.generativeai" in req_content:
            detected["AI/ML"].append("Google Gemini")
        if "ollama" in req_content:
            detected["AI/ML"].append("Ollama")
        # Frameworks
        if "langchain" in req_content:
            detected["AI/ML"].append("LangChain")
        if "llama-index" in req_content or "llama_index" in req_content:
            detected["AI/ML"].append("LlamaIndex")
        if "haystack" in req_content:
            detected["AI/ML"].append("Haystack")
        # ML/Deep Learning
        if "torch" in req_content or "pytorch" in req_content:
            detected["AI/ML"].append("PyTorch")
        if "tensorflow" in req_content or "tf " in req_content:
            detected["AI/ML"].append("TensorFlow")
        if "transformers" in req_content:
            detected["AI/ML"].append("HuggingFace Transformers")
        if "sentence-transformers" in req_content:
            detected["AI/ML"].append("Sentence Transformers")
        # Data
        if "pandas" in req_content:
            detected["AI/ML"].append("Pandas")
        if "numpy" in req_content:
            detected["AI/ML"].append("NumPy")
        if "scikit-learn" in req_content or "sklearn" in req_content:
            detected["AI/ML"].append("scikit-learn")
        # OCR
        if "easyocr" in req_content:
            detected["AI/ML"].append("EasyOCR")
        if "pytesseract" in req_content:
            detected["AI/ML"].append("Tesseract OCR")
        if "paddleocr" in req_content:
            detected["AI/ML"].append("PaddleOCR")
        # Vector search
        if "faiss" in req_content:
            detected["AI/ML"].append("FAISS")
        if "chromadb" in req_content:
            detected["AI/ML"].append("ChromaDB")
        if "qdrant" in req_content:
            detected["AI/ML"].append("Qdrant")
        if "modal" in req_content:
            detected["AI/ML"].append("Modal (serverless GPU)")

    # Database
    if (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists():
        for fname in ["docker-compose.yml", "docker-compose.yaml"]:
            dc = root / fname
            if dc.exists():
                content = dc.read_text().lower()
                if "postgres" in content:
                    detected["Database"].append("PostgreSQL")
                if "mysql" in content:
                    detected["Database"].append("MySQL")
                if "redis" in content:
                    detected["Database"].append("Redis")
                if "mongo" in content:
                    detected["Database"].append("MongoDB")

    if req_content:
        if "psycopg" in req_content or "asyncpg" in req_content:
            detected["Database"].append("PostgreSQL")
        if "pymongo" in req_content:
            detected["Database"].append("MongoDB")
        if "redis" in req_content:
            detected["Database"].append("Redis")
        if "elasticsearch" in req_content:
            detected["Database"].append("Elasticsearch")
        if "sqlalchemy" in req_content:
            detected["Database"].append("SQLAlchemy")

    if (root / "prisma").exists():
        detected["Database"].append("Prisma ORM")
    if list(root.rglob("alembic.ini")):
        detected["Database"].append("Alembic (migrations)")

    # CI/CD
    if (root / ".github" / "workflows").exists():
        count = len(list((root / ".github" / "workflows").glob("*.yml")))
        detected["CI/CD"].append(f"GitHub Actions ({count} workflows)")
    if (root / ".gitlab-ci.yml").exists():
        detected["CI/CD"].append("GitLab CI")
    if (root / "Jenkinsfile").exists():
        detected["CI/CD"].append("Jenkins")
    if (root / ".circleci").exists():
        detected["CI/CD"].append("CircleCI")

    # Cloud
    if (root / "terraform").exists() or list(root.glob("*.tf")):
        detected["Cloud"].append("Terraform")
    if (root / "serverless.yml").exists():
        detected["Cloud"].append("Serverless Framework")
    if (root / "fly.toml").exists():
        detected["Cloud"].append("Fly.io")
    if (root / "render.yaml").exists():
        detected["Cloud"].append("Render")
    if list(root.rglob("*.yaml")):
        for f in root.rglob("*.yaml"):
            content = f.read_text(errors="ignore").lower()
            if "kind: deployment" in content or "kind: service" in content:
                detected["Cloud"].append("Kubernetes")
                break

    # Container
    if (root / "Dockerfile").exists() or list(root.glob("Dockerfile*")):
        detected["Container"].append("Docker")
    if (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists():
        detected["Container"].append("docker-compose")

    # Build output
    has_anything = any(v for v in detected.values())
    if not has_anything:
        return f"Không phát hiện tech stack nào trong {folder_path}"

    sep = "━" * 48
    lines = [sep, f"  CODEBASE ARCHITECTURE — {Path(folder_path).name}", sep]
    for category, items in detected.items():
        if items:
            unique = list(dict.fromkeys(items))
            lines.append(f"  {category:<12}{', '.join(unique)}")
    lines.append(sep)
    return "\n".join(lines)
