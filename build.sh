#!/usr/bin/env bash
# HanTone 一键构建脚本（Linux / macOS / WSL）
# 用法: ./build.sh [test|build|clean]
set -euo pipefail

PYTHON="${PYTHON:-python3}"
cd "$(dirname "$0")"

case "${1:-test}" in
  test)
    echo "==> 运行单元测试"
    "$PYTHON" -m unittest discover -s tests -v
    ;;
  build)
    echo "==> 构建分发包"
    "$PYTHON" -m pip install --upgrade build
    "$PYTHON" -m build
    echo "==> 产物位于 dist/"
    ls -lh dist/
    ;;
  clean)
    echo "==> 清理构建产物"
    rm -rf build dist *.egg-info
    find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
    ;;
  *)
    echo "用法: $0 [test|build|clean]"
    exit 1
    ;;
esac
