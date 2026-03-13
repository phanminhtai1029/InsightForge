import json
from pathlib import Path


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def analyze_stack(folder_path: str) -> str:
    root = Path(folder_path)
    detected: dict[str, list[str]] = {
        "Frontend": [], "Backend": [], "Database": [],
        "CI/CD": [], "Cloud": [], "Container": [],
    }

    # Frontend
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

    # Backend
    for req_file in ["requirements.txt", "requirements/base.txt"]:
        req_path = root / req_file
        if req_path.exists():
            content = req_path.read_text().lower()
            if "fastapi" in content:
                detected["Backend"].append("FastAPI")
            if "django" in content:
                detected["Backend"].append("Django")
            if "flask" in content:
                detected["Backend"].append("Flask")

    if (root / "pyproject.toml").exists():
        content = (root / "pyproject.toml").read_text().lower()
        if "fastapi" in content:
            detected["Backend"].append("FastAPI")

    if (root / "go.mod").exists():
        detected["Backend"].append("Go")
    if (root / "pom.xml").exists():
        detected["Backend"].append("Java/Spring")
    if (root / "Cargo.toml").exists():
        detected["Backend"].append("Rust")

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

    sep = "━" * 42
    lines = [sep, f"  CODEBASE ARCHITECTURE — {Path(folder_path).name}", sep]
    for category, items in detected.items():
        if items:
            unique = list(dict.fromkeys(items))
            lines.append(f"  {category:<12}{', '.join(unique)}")
    lines.append(sep)
    return "\n".join(lines)
