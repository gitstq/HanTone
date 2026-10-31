# 🤝 贡献指南 / Contributing

感谢你关注 HanTone！本项目欢迎任何形式的贡献，但请务必遵守以下规范。

## 📋 提交规范

提交信息遵循 **Angular / Conventional Commits** 规范：

| 前缀 | 用途 |
| --- | --- |
| `feat:` | 新增功能 |
| `fix:` | 修复问题 |
| `docs:` | 文档更新 |
| `refactor:` | 代码重构（不改变外部行为） |
| `test:` | 测试用例 |
| `perf:` | 性能优化 |
| `chore:` | 构建 / 工具 / 杂项 |

示例：`feat: 新增闽南语读音扩展开关`

## 🔧 开发流程

```bash
git clone https://github.com/gitstq/HanTone.git
cd HanTone
make test          # 运行单元测试
make demo          # 功能演示
```

## 🧪 提交前检查清单

- [ ] `make test` 全部通过（34 项）
- [ ] 新增功能配套单元测试
- [ ] 未引入任何第三方运行时依赖（**硬性要求**）
- [ ] 代码含中文注释，符合 PEP 8
- [ ] 若修改数据表，同步更新 `tools/build_data.py` 并重新生成

## 🐛 Issue 规范

提交 Issue 时请附：

1. HanTone 版本（`python -m hantone --version`）
2. Python 版本与操作系统
3. 可复现的最小输入与期望 / 实际输出

## 📄 多音字纠错

若发现读音错误，请提交 Issue 并注明：

- 具体词组与期望读音
- 依据来源（如《现代汉语词典》第 7 版页码）
