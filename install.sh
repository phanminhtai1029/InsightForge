#!/usr/bin/env bash
# InsightForge — One-line installer
# Usage: curl -fsSL https://raw.githubusercontent.com/phanminhtai1029/InsightForge/master/install.sh | bash
set -euo pipefail

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[InsightForge]${RESET} $*"; }
success() { echo -e "${GREEN}✓${RESET} $*"; }
warn()    { echo -e "${YELLOW}⚠${RESET} $*"; }
die()     { echo -e "${RED}✗ $*${RESET}" >&2; exit 1; }

echo ""
echo -e "${BOLD}InsightForge Installer${RESET}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ── OS Detection ─────────────────────────────────────────────────────────────
OS="$(uname -s)"
case "$OS" in
  Darwin) PLATFORM="macos" ;;
  Linux)
    if grep -qi microsoft /proc/version 2>/dev/null; then
      PLATFORM="wsl"
    else
      PLATFORM="linux"
    fi
    ;;
  *)
    die "Windows native không được hỗ trợ. Hãy dùng WSL2 hoặc Docker.\nXem: https://github.com/phanminhtai1029/InsightForge#option-2--docker"
    ;;
esac
info "Platform: $PLATFORM"

# ── Require curl ─────────────────────────────────────────────────────────────
command -v curl &>/dev/null || die "curl chưa được cài. Hãy cài curl trước."

# ── Install uv ───────────────────────────────────────────────────────────────
if command -v uv &>/dev/null; then
  success "uv $(uv --version | cut -d' ' -f2) đã có sẵn"
else
  info "Cài uv (Python package manager)..."
  curl -Ls https://astral.sh/uv/install.sh | sh
  # Thêm vào PATH cho phiên này
  export PATH="${HOME}/.local/bin:${PATH}"
  command -v uv &>/dev/null || export PATH="${HOME}/.cargo/bin:${PATH}"
  command -v uv &>/dev/null || die "Cài uv thất bại. Thử cài thủ công: https://docs.astral.sh/uv/getting-started/installation/"
  success "uv $(uv --version | cut -d' ' -f2) đã được cài"
fi

# ── Clone / Update repo ───────────────────────────────────────────────────────
INSTALL_DIR="${HOME}/.local/share/insightforge"
REPO_URL="https://github.com/phanminhtai1029/InsightForge.git"

if [ -d "${INSTALL_DIR}/.git" ]; then
  info "Cập nhật InsightForge tại ${INSTALL_DIR}..."
  git -C "${INSTALL_DIR}" pull --ff-only --quiet
  success "Đã cập nhật"
else
  info "Clone InsightForge về ${INSTALL_DIR}..."
  git clone --quiet "${REPO_URL}" "${INSTALL_DIR}"
  success "Clone hoàn tất"
fi

# ── Install Python dependencies ───────────────────────────────────────────────
info "Cài Python dependencies (lần đầu có thể mất 1-2 phút)..."
cd "${INSTALL_DIR}"
uv sync --no-dev --quiet
success "Dependencies đã cài"

# ── Install Ollama ────────────────────────────────────────────────────────────
if command -v ollama &>/dev/null; then
  success "Ollama đã có sẵn ($(ollama --version 2>&1 | head -1))"
else
  info "Cài Ollama (AI model runner)..."
  if [ "$PLATFORM" = "macos" ]; then
    if command -v brew &>/dev/null; then
      brew install --cask ollama --quiet
    else
      warn "Homebrew chưa có. Tải Ollama tại: https://ollama.com/download"
      warn "Sau khi cài Ollama xong, chạy lại script này."
      exit 0
    fi
  else
    # Linux / WSL2
    curl -fsSL https://ollama.com/install.sh | sh
  fi
  success "Ollama đã được cài"
fi

# ── Start Ollama server (nếu chưa chạy) ──────────────────────────────────────
if ollama list &>/dev/null 2>&1; then
  success "Ollama server đang chạy"
else
  info "Khởi động Ollama server..."
  if [ "$PLATFORM" = "macos" ]; then
    open -a Ollama 2>/dev/null || ollama serve &>/dev/null &
  else
    ollama serve &>/dev/null &
  fi
  # Chờ server sẵn sàng (tối đa 15 giây)
  for i in $(seq 1 15); do
    if ollama list &>/dev/null 2>&1; then
      success "Ollama server đã sẵn sàng"
      break
    fi
    sleep 1
    if [ "$i" -eq 15 ]; then
      warn "Ollama server khởi động chậm. Tiếp tục pull models..."
    fi
  done
fi

# ── Pull models ───────────────────────────────────────────────────────────────
MODELS=("qwen2.5:7b" "nomic-embed-text")
for model in "${MODELS[@]}"; do
  if ollama list 2>/dev/null | grep -q "^${model}"; then
    success "Model ${model} đã có sẵn"
  else
    info "Tải model ${model} (có thể mất vài phút tùy tốc độ mạng)..."
    ollama pull "${model}"
    success "Model ${model} đã sẵn sàng"
  fi
done

# ── Create wrapper script ─────────────────────────────────────────────────────
BIN_DIR="${HOME}/.local/bin"
mkdir -p "${BIN_DIR}"
WRAPPER="${BIN_DIR}/insightforge"
cat > "${WRAPPER}" <<WRAPPER_EOF
#!/usr/bin/env bash
exec "${INSTALL_DIR}/.venv/bin/insightforge" "\$@"
WRAPPER_EOF
chmod +x "${WRAPPER}"
success "Lệnh insightforge đã được tạo tại ${WRAPPER}"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BOLD}${GREEN}InsightForge đã sẵn sàng!${RESET}"
echo ""
echo -e "  ${CYAN}insightforge .${RESET}               # analyze thư mục hiện tại"
echo -e "  ${CYAN}insightforge /path/to/project${RESET}  # analyze project bất kỳ"
echo ""

# Kiểm tra PATH
if ! echo "${PATH}" | grep -q "${BIN_DIR}"; then
  warn "Thêm vào PATH (copy vào ~/.bashrc hoặc ~/.zshrc):"
  echo -e "  ${BOLD}export PATH=\"\${HOME}/.local/bin:\${PATH}\"${RESET}"
  echo ""
  warn "Hoặc chạy ngay bây giờ:"
  echo -e "  ${BOLD}export PATH=\"\${HOME}/.local/bin:\${PATH}\" && insightforge .${RESET}"
fi
