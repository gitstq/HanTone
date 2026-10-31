# HanTone —— 一键构建 / 测试 / 打包
# 全部命令仅依赖 Python 标准库，无需预装任何第三方包。

PYTHON ?= python3
PKG    := hantone

.PHONY: help install test data build clean check demo

help:
	@echo "HanTone 可用目标："
	@echo "  make install   以可编辑模式安装到当前环境"
	@echo "  make test      运行单元测试"
	@echo "  make data      重新生成内置拼音数据表（需 Unihan_Readings.txt）"
	@echo "  make build     构建 sdist 与 wheel 分发包"
	@echo "  make check     安装并冒烟验证命令行"
	@echo "  make demo      运行功能演示"
	@echo "  make clean     清理构建产物"

install:
	$(PYTHON) -m pip install -e .

test:
	$(PYTHON) -m unittest discover -s tests -v

data:
	$(PYTHON) tools/build_data.py $(UNIHAN) hantone/_data.py

build:
	$(PYTHON) -m pip install --upgrade build
	$(PYTHON) -m build

check: install
	$(PYTHON) -m $(PKG) pinyin 中国银行
	$(PYTHON) -m $(PKG) info

demo:
	$(PYTHON) -m $(PKG) pinyin 重庆银行
	$(PYTHON) -m $(PKG) pinyin 好好学习 --sandhi
	$(PYTHON) -m $(PKG) slug 汉语拼音转换引擎
	$(PYTHON) -m $(PKG) lookup 行

clean:
	rm -rf build dist *.egg-info
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	find . -name '*.py[co]' -delete
